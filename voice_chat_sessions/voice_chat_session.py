import os
import requests
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from realtime_functions import get_all_plans_summary

class VoiceChatSession:
    """Handles OpenAI Realtime API session creation and management for voice chat."""
    
    def __init__(self, openai_api_key: str, model: str, session_url: str):
        """
        Initialize the VoiceChatSession handler.
        
        Args:
            openai_api_key: OpenAI API key for authentication
            model: OpenAI Realtime model to use
            session_url: OpenAI Realtime sessions endpoint URL
        """
        self.api_key = openai_api_key
        self.model = model
        self.session_url = session_url
        self.instructions_filename = "call_center_guide.md"
    
    def read_instructions_from_file(self) -> Optional[str]:
        """
        Reads the instructions content from the specified file.
        
        Returns:
            The contents of the instructions file, or None if not found/error.
        """
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            instructions_file_path = os.path.join(script_dir, self.instructions_filename)
            
            print(f"Attempting to read instructions file: {instructions_file_path}")
            
            with open(instructions_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"Successfully read instructions from '{self.instructions_filename}'.")
                return content
                
        except FileNotFoundError:
            print(f"Warning: Instructions file '{self.instructions_filename}' not found at {instructions_file_path}. Proceeding without custom instructions.")
            return None
        except Exception as e:
            print(f"Error reading instructions file '{self.instructions_filename}': {e}")
            return None
    
    def create_session(self, db_session: Optional[DBSession] = None) -> Dict[str, Any]:
        """
        Create a new OpenAI Realtime API session with ephemeral token.
        
        Args:
            db_session: Optional database session for retrieving plan summaries
            
        Returns:
            Session data from OpenAI API containing client_secret and other session info.
            
        Raises:
            ValueError: If API key is not configured
            requests.RequestException: If API request fails
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured on the server.")
        
        print(f"Using OpenAI model: {self.model}")
        
        # Read instructions from file
        instructions_text = self.read_instructions_from_file()
        
        # Generate plans summary for initial context if database session provided
        plans_summary = ""
        if db_session:
            try:
                plans_summary = get_all_plans_summary(db_session)
                print(f"Generated plans summary ({len(plans_summary)} characters)")
            except Exception as e:
                print(f"Error generating plans summary: {e}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Build session payload
        payload = self._build_session_payload(instructions_text, plans_summary)
        
        try:
            print(f"Requesting session from OpenAI with payload: {json.dumps(payload)}")
            print(f"Making request to URL: {self.session_url}")
            
            response = requests.post(self.session_url, headers=headers, json=payload)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            response.raise_for_status()
            
            session_data = response.json()
            
            # Verify client_secret is present
            if "client_secret" not in session_data:
                print(f"Error: 'client_secret' not found in OpenAI response: {session_data}")
                raise ValueError("Failed to retrieve client_secret from OpenAI session.")
            
            print(f"Successfully created OpenAI session ID: {session_data.get('id', 'N/A')}")
            return session_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error requesting OpenAI session token: {e}")
            error_details = self._extract_error_details(e)
            print(f"Error details from OpenAI API: {error_details}")
            raise
    
    def _build_session_payload(self, instructions_text: Optional[str], plans_summary: str) -> Dict[str, Any]:
        """
        Build the payload for session creation request.
        
        Args:
            instructions_text: Optional instructions from file
            plans_summary: Summary of available health plans
            
        Returns:
            Dictionary containing the session creation payload
        """
        payload = {
            "model": self.model,
            "voice": "alloy",
            "turn_detection": {
                "type": "semantic_vad",
                "eagerness": "high"
            },
            "tools": self._get_function_tools(),
            "tool_choice": "auto"
        }
        
        # Combine instructions with plans summary
        full_instructions = instructions_text or ""
        if plans_summary:
            full_instructions += f"\n\n## Available Health Plans Overview\n{plans_summary}\n\nUse the functions to get detailed information about specific plans when needed."
        
        # Only add instructions if we have content
        if full_instructions:
            payload["instructions"] = full_instructions
            print("Including instructions and plans summary in session creation request.")
        else:
            print("No instructions found; session will be created without custom instructions.")
        
        return payload
    
    def _get_function_tools(self) -> list:
        """
        Get the function tool definitions for the session.
        
        Returns:
            List of function tool definitions
        """
        return [
            {
                "type": "function",
                "name": "get_plan_coverage_summary",
                "description": "Get comprehensive coverage details and benefits for a specific health plan by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_name": {
                            "type": "string",
                            "description": "The name or partial name of the health plan (e.g., 'Gold', 'CompleteCare', 'Signature HMO')"
                        }
                    },
                    "required": ["plan_name"]
                }
            },
            {
                "type": "function",
                "name": "get_plan_table_of_contents",
                "description": "Get the table of contents to find specific sections and page numbers in plan documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_name": {
                            "type": "string",
                            "description": "The name or partial name of the health plan"
                        }
                    },
                    "required": ["plan_name"]
                }
            },
            {
                "type": "function",
                "name": "search_plan_document",
                "description": "Search within a plan's documents for specific information like prior authorization, copays, coverage details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan_name": {
                            "type": "string",
                            "description": "The name or partial name of the health plan"
                        },
                        "search_term": {
                            "type": "string",
                            "description": "The term or phrase to search for (e.g., 'prior authorization', 'emergency care', 'prescription drugs')"
                        }
                    },
                    "required": ["plan_name", "search_term"]
                }
            }
        ]
    
    def _extract_error_details(self, e: requests.exceptions.RequestException) -> Any:
        """
        Extract error details from a RequestException.
        
        Args:
            e: The RequestException to extract details from
            
        Returns:
            Error details as dict, string, or original exception string
        """
        if e.response is not None:
            try:
                return e.response.json()
            except json.JSONDecodeError:
                return e.response.text
        return str(e)