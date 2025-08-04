// debug.js - Tool call debugging functionality

document.addEventListener('DOMContentLoaded', function() {
    const debugOutput = document.getElementById('debugOutput');
    
    // Initialize Socket.IO connection
    const socket = io();
    
    // Helper function to add debug messages
    function addDebugMessage(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const messageDiv = document.createElement('div');
        messageDiv.className = `p-2 rounded border-l-4 ${getTypeClasses(type)}`;
        messageDiv.innerHTML = `
            <div class="text-xs text-gray-500 mb-1">${timestamp}</div>
            <div class="font-mono text-sm">${message}</div>
        `;
        
        // Clear "waiting" message if it exists
        const waitingMsg = debugOutput.querySelector('.text-yellow-600.italic');
        if (waitingMsg) {
            waitingMsg.remove();
        }
        
        debugOutput.appendChild(messageDiv);
        debugOutput.scrollTop = debugOutput.scrollHeight;
    }
    
    // Helper function to get CSS classes based on message type
    function getTypeClasses(type) {
        switch (type) {
            case 'start':
                return 'border-blue-400 bg-blue-50';
            case 'complete':
                return 'border-green-400 bg-green-50';
            case 'error':
                return 'border-red-400 bg-red-50';
            default:
                return 'border-gray-400 bg-gray-50';
        }
    }
    
    // Format arguments for display
    function formatArguments(args) {
        if (!args || Object.keys(args).length === 0) {
            return 'No arguments';
        }
        return Object.entries(args)
            .map(([key, value]) => `${key}: "${value}"`)
            .join(', ');
    }
    
    // Socket event handlers
    socket.on('connect', function() {
        console.log('Debug WebSocket connected');
        addDebugMessage('🔌 Debug WebSocket connected', 'info');
    });
    
    socket.on('disconnect', function() {
        console.log('Debug WebSocket disconnected');
        addDebugMessage('❌ Debug WebSocket disconnected', 'error');
    });
    
    socket.on('tool_call_start', function(data) {
        console.log('Tool call started:', data);
        const message = `
            🚀 <strong>TOOL CALL STARTED</strong><br>
            Function: <strong>${data.function_name}</strong><br>
            Arguments: ${formatArguments(data.arguments)}
        `;
        addDebugMessage(message, 'start');
    });
    
    socket.on('tool_call_complete', function(data) {
        console.log('Tool call completed:', data);
        const message = `
            ✅ <strong>TOOL CALL COMPLETED</strong><br>
            Function: <strong>${data.function_name}</strong><br>
            Result Preview: <code class="text-xs">${data.result_preview}</code>
        `;
        addDebugMessage(message, 'complete');
    });
    
    socket.on('tool_call_error', function(data) {
        console.log('Tool call error:', data);
        const message = `
            ❌ <strong>TOOL CALL ERROR</strong><br>
            Function: <strong>${data.function_name}</strong><br>
            Error: <span class="text-red-600">${data.error}</span>
        `;
        addDebugMessage(message, 'error');
    });
    
    // Handle debug messages from WebRTC data channel
    socket.on('debug_message', function(data) {
        console.log('Debug message received:', data);
        const message = `
            🔍 <strong>WEBRTC DEBUG</strong><br>
            Type: <strong>${data.type}</strong><br>
            Data: <code class="text-xs">${JSON.stringify(data.data).substring(0, 200)}...</code>
        `;
        addDebugMessage(message, 'info');
    });

    // Make socket available globally for debugging
    window.debugSocket = socket;
});