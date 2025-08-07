import os
from dotenv import load_dotenv
import json # Added for JSON loading in error handling
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from plans.plans_routes import plans_bp
from realtime_functions import (
    get_plan_coverage_summary,
    get_plan_table_of_contents,
    search_plan_document
)
from plans.plans_model import Base
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from voice_chat_sessions.voice_chat_session import VoiceChatSession

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# It's highly recommended to load sensitive keys from environment variables
# Ensure OPENAI_API_KEY is set in your environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# Use the latest recommended model or the specific one you need
# Update model string as per OpenAI documentation or announcements
# Check OpenAI docs for the current recommended preview model.
# OPENAI_REALTIME_MODEL = os.environ.get("OPENAI_REALTIME_MODEL", "gpt-4o-mini-realtime-preview") # Using a reasonable default gpt-4o-mini-realtime-preview
OPENAI_REALTIME_MODEL = os.environ.get("OPENAI_REALTIME_MODEL", "gpt-4o-realtime-preview") # Using a reasonable default gpt-4o-mini-realtime-preview
OPENAI_SESSION_URL = "https://api.openai.com/v1/realtime/sessions"



# --- Database Initialization ---
database_url = os.environ.get('DATABASE_URL')
Session = None  # Initialize Session variable
engine = None   # Initialize engine variable

if database_url:
    # Use connection pooling with retry settings
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections before Neon's 5-minute timeout
        pool_pre_ping=True  # Enable connection health checks
    )

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()
else:
    print("Warning: DATABASE_URL not found in environment variables")

# --- Flask App Initialization ---
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")
app.register_blueprint(plans_bp)


# --- Routes ---
@app.route('/health')
def health_check():
    """Health check endpoint for Azure."""
    return jsonify({"status": "healthy", "service": "healthfirst-agent"}), 200

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/execute-function', methods=['POST'])
def execute_function():
    """
    Execute a function called by the OpenAI Realtime API.
    This endpoint is called when the voice assistant needs to query plan information.
    """
    try:
        data = request.json
        function_name = data.get('name')
        arguments = data.get('arguments', {})
        
        print(f"Executing function: {function_name} with arguments: {arguments}")
        
        # Broadcast tool call start to frontend
        socketio.emit('tool_call_start', {
            'function_name': function_name,
            'arguments': arguments,
            'timestamp': json.dumps({"timestamp": "now"})  # Simple timestamp
        })
        
        if not Session:
            error_result = {"error": "Database not available"}
            socketio.emit('tool_call_error', {
                'function_name': function_name,
                'error': "Database not available"
            })
            return jsonify(error_result), 500
            
        db_session = Session()
        
        try:
            # Execute the appropriate function
            if function_name == 'get_plan_coverage_summary':
                result = get_plan_coverage_summary(
                    arguments.get('plan_name', ''),
                    db_session
                )
            elif function_name == 'get_plan_table_of_contents':
                result = get_plan_table_of_contents(
                    arguments.get('plan_name', ''),
                    db_session
                )
            elif function_name == 'search_plan_document':
                result = search_plan_document(
                    arguments.get('plan_name', ''),
                    arguments.get('search_term', ''),
                    db_session
                )
            else:
                result = {"error": f"Unknown function: {function_name}"}
            
            print(f"Function result: {json.dumps(result)[:500]}...")  # Log first 500 chars
            
            # Broadcast tool call completion to frontend
            result_preview = json.dumps(result)[:200] + "..." if len(json.dumps(result)) > 200 else json.dumps(result)
            socketio.emit('tool_call_complete', {
                'function_name': function_name,
                'result_preview': result_preview,
                'success': True
            })
            
            return jsonify(result)
            
        finally:
            db_session.close()
            
    except Exception as e:
        print(f"Error executing function: {e}")
        
        # Broadcast tool call error to frontend
        socketio.emit('tool_call_error', {
            'function_name': function_name,
            'error': str(e)
        })
        
        return jsonify({"error": str(e)}), 500

@app.route('/session', methods=['GET'])
def get_session_token():
    """
    Server-side endpoint to securely generate an ephemeral OpenAI API key (token)
    using the VoiceChatSession handler.
    The client-side JavaScript will call this endpoint.
    """
    print("Session endpoint called - starting session creation process")
    
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return jsonify({"error": "OpenAI API key not configured on the server."}), 500
    
    # Create VoiceChatSession instance
    voice_session = VoiceChatSession(
        openai_api_key=OPENAI_API_KEY,
        model=OPENAI_REALTIME_MODEL,
        session_url=OPENAI_SESSION_URL
    )
    
    # Create database session if available
    db_session = Session() if Session else None
    
    try:
        # Create the OpenAI session
        session_data = voice_session.create_session(db_session)
        return jsonify(session_data)
        
    except ValueError as e:
        print(f"ValueError in /session endpoint: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error in /session endpoint: {e}")
        error_details = str(e)
        # Try to extract more details if it's a requests exception
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
            except:
                error_details = getattr(e.response, 'text', str(e))
        return jsonify({"error": "Failed to create voice session.", "details": error_details}), 502
    finally:
        if db_session:
            db_session.close()

# --- Run the App ---
if __name__ == '__main__':
    # Note: Use host='0.0.0.0' for accessibility within Docker/Replit,
    # but be mindful of security implications in production environments.
    # Use environment variable for port if available, default to 8080 locally
    # Azure deployment will set PORT=8000 via environment variable
    port = int(os.environ.get('PORT', 8080)) # Default 8080 locally, Azure sets PORT=8000
    # Debug mode should ideally be off in production
    # Read FLASK_DEBUG env var, default to 'false' if not set
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    print(f"Starting Flask app with SocketIO on host 0.0.0.0 port {port} with debug mode: {debug_mode}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode, allow_unsafe_werkzeug=True)