// This JavaScript file will be used to display the transcript of what ChatGPT voice agent is saying on the page as it is said by the voice bot.

// static/print_transcript.js
// This JavaScript file is used to display the transcript of what the voice agent is saying on the page.

// Flag to track if it's the first transcript entry, used to remove the initial placeholder text.
let isFirstTranscript = true;

/**
 * Displays a tool/function call notification in the transcript output area.
 * It shows what tool was called in a plain English format.
 *
 * @param {string} toolName - The name of the tool that was called
 * @param {object} arguments - The arguments passed to the tool
 */
function displayToolCall(toolName, arguments) {
    const transcriptContainer = document.getElementById('transcriptOutput');

    if (!transcriptContainer) {
        console.error("Error: Transcript container element with ID 'transcriptOutput' not found.");
        return;
    }

    // Remove placeholder if this is the first entry
    if (isFirstTranscript) {
        const placeholder = transcriptContainer.querySelector('.text-gray-400.italic');
        if (placeholder) {
            transcriptContainer.removeChild(placeholder);
        }
        isFirstTranscript = false;
    }

    // Create a new paragraph for the tool call notification
    const newEntry = document.createElement('p');
    newEntry.style.color = '#6B7280'; // Gray color for tool calls
    newEntry.style.fontStyle = 'italic';
    
    // Create plain English description based on the tool name
    let description = '🔧 ';
    
    switch(toolName) {
        case 'get_plan_coverage_summary':
            description += `Looking up coverage summary for ${arguments.plan_name || 'plan'}...`;
            break;
        case 'get_plan_table_of_contents':
            description += `Retrieving table of contents for ${arguments.plan_name || 'plan'}...`;
            break;
        case 'search_plan_document':
            description += `Searching for "${arguments.search_term || ''}" in ${arguments.plan_name || 'plan'} documents...`;
            break;
        case 'get_all_plans_summary':
            description += 'Getting summary of all available plans...';
            break;
        default:
            description += `Calling ${toolName}...`;
    }
    
    newEntry.textContent = description;
    transcriptContainer.appendChild(newEntry);
    transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
}

/**
 * Displays a complete transcript utterance in the transcript output area on the HTML page.
 * It appends the new text as a paragraph and scrolls the container to the bottom.
 *
 * @param {string} text - The transcript text received from the assistant (usually a complete sentence or phrase).
 */
function displayFinalTranscript(text) {
    // Get the HTML element where the transcript should be displayed.
    const transcriptContainer = document.getElementById('transcriptOutput');

    // Safety check: Make sure the transcript container element exists in the DOM.
    if (!transcriptContainer) {
        console.error("Error: Transcript container element with ID 'transcriptOutput' not found.");
        return; // Exit the function if the container isn't found.
    }

    // If this is the very first transcript being added, find and remove the placeholder text.
    if (isFirstTranscript) {
        const placeholder = transcriptContainer.querySelector('.text-gray-400.italic');
        if (placeholder) {
            transcriptContainer.removeChild(placeholder);
        }
        // Set the flag to false so the placeholder isn't removed again.
        isFirstTranscript = false;
    }

    // Create a new paragraph element (<p>) to hold this line of the transcript.
    const newEntry = document.createElement('p');

    // Add the actual transcript text content to the paragraph.
    // Prepending "Assistant: " makes it clear who is speaking.
    newEntry.textContent = 'Assistant: ' + text;

    // Optional: Add any specific CSS classes if needed for styling the entry.
    // Tailwind classes defined on the container (like font-mono, text-sm) will apply.
    // You could add classes like 'mb-1' here if the container's 'space-y-2' isn't sufficient.
    // newEntry.classList.add('mb-1');

    // Append the newly created paragraph element to the transcript container.
    transcriptContainer.appendChild(newEntry);

    // Automatically scroll the transcript container to the bottom.
    // This ensures the latest transcript entry is always visible.
    transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
}

// Note: This script assumes that your main script ('script.js') will call
// the `displayFinalTranscript(text)` function when it receives the appropriate
// message (e.g., 'response.audio_transcript.done') from the WebSocket/WebRTC data channel.
// Make sure the call in `script.js` passes the relevant transcript string.

// Example of how you might call this from script.js (within the dc.onmessage handler):
/*
   const messageData = JSON.parse(event.data);
   // Check for events containing the final transcript for an utterance
   if (messageData.type === "response.audio_transcript.done" && messageData.transcript) {
       displayFinalTranscript(messageData.transcript);
   } else if (messageData.type === "response.done" && messageData.response?.output?.[0]?.content?.[0]?.transcript) {
       // Fallback check in response.done event, structure might vary
       displayFinalTranscript(messageData.response.output[0].content[0].transcript);
   }
   // Add other event handling as needed...
*/