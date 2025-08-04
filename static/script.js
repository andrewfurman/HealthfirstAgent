// static/script.js
// This JavaScript File Is Used To Interact With The ChatGPT Real Time Voice Model

document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const statusDiv = document.getElementById('status');
    const remoteAudio = document.getElementById('remoteAudio'); // Get the audio element

    let pc; // RTCPeerConnection
    let dc; // RTCDataChannel
    let localStream; // User's microphone stream

    startButton.addEventListener('click', startChat);
    stopButton.addEventListener('click', stopChat);

    // Function to handle function calls from OpenAI Realtime API
    async function handleFunctionCall(messageData) {
        try {
            console.log("Processing function call:", messageData);
            
            // Extract function name and arguments from the message
            const functionName = messageData.name;
            const argumentsString = messageData.arguments;
            const callId = messageData.call_id;
            
            // Parse the arguments
            let parsedArguments;
            try {
                parsedArguments = JSON.parse(argumentsString);
            } catch (e) {
                console.error("Failed to parse function arguments:", argumentsString);
                return;
            }
            
            console.log(`Calling function: ${functionName} with args:`, parsedArguments);
            
            // Send to our Flask endpoint
            const response = await fetch('/execute-function', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: functionName,
                    arguments: parsedArguments
                })
            });
            
            const result = await response.json();
            console.log("Function call result:", result);
            
            // Send the result back to OpenAI via the data channel
            if (dc && dc.readyState === 'open') {
                const responseMessage = {
                    type: "conversation.item.create",
                    item: {
                        type: "function_call_output",
                        call_id: callId,
                        output: JSON.stringify(result)
                    }
                };
                
                console.log("Sending function result back to OpenAI:", responseMessage);
                dc.send(JSON.stringify(responseMessage));
                
                // Trigger a response generation
                dc.send(JSON.stringify({
                    type: "response.create"
                }));
            }
            
        } catch (error) {
            console.error("Error handling function call:", error);
        }
    }

    async function startChat() {
        console.log('=== Starting Chat Session ===');
        console.log('1. Initial setup...');
        console.log('- Setting status and button states');
        statusDiv.textContent = 'Connecting...';
        startButton.disabled = true;
        stopButton.disabled = false;

        try {
            // 1. Get an ephemeral key from your server
            console.log('2. Requesting session token...');
            console.log('- Making fetch request to /session endpoint');
            const tokenResponse = await fetch("/session");
            console.log('- Session response status:', tokenResponse.status);
            if (!tokenResponse.ok) {
                 const errorData = await tokenResponse.json();
                 console.error('Session token request failed:', {
                     status: tokenResponse.status,
                     statusText: tokenResponse.statusText,
                     errorData
                 });
                 throw new Error(`Failed to get session token: ${tokenResponse.status} ${tokenResponse.statusText} - ${JSON.stringify(errorData.details || errorData.error)}`);
            }
            const sessionData = await tokenResponse.json();
            const EPHEMERAL_KEY = sessionData.client_secret?.value; // Use optional chaining
            // Use the model specified in the session response or fallback if needed
            const REALTIME_MODEL = sessionData.model || "gpt-4o-realtime-preview";

            if (!EPHEMERAL_KEY) {
                 throw new Error("Ephemeral key (client_secret.value) not found in session response.");
            }
            console.log(`Using model: ${REALTIME_MODEL}`);
            console.log('Ephemeral key received.');

            console.log('3. Setting up WebRTC...');
            // 2. Create a peer connection
            pc = new RTCPeerConnection();
            console.log('- RTCPeerConnection created');

            // 3. Set up to play remote audio from the model
            pc.ontrack = e => {
                console.log('Remote track received:', e.track);
                console.log('Track kind:', e.track.kind);
                console.log('Track enabled:', e.track.enabled);
                console.log('Track muted:', e.track.muted);
                console.log('Track readyState:', e.track.readyState);
                
                if (e.streams && e.streams[0]) {
                    const stream = e.streams[0];
                    console.log('Stream active:', stream.active);
                    console.log('Stream id:', stream.id);
                    console.log('Audio tracks in stream:', stream.getAudioTracks().length);
                    
                    // Get the audio track and try to unmute it
                    const audioTracks = stream.getAudioTracks();
                    if (audioTracks.length > 0) {
                        const audioTrack = audioTracks[0];
                        console.log('Audio track before unmute attempt:', {
                            enabled: audioTrack.enabled,
                            muted: audioTrack.muted,
                            readyState: audioTrack.readyState,
                            label: audioTrack.label,
                            id: audioTrack.id
                        });
                        
                        // Force enable the track
                        audioTrack.enabled = true;
                        
                        // Monitor track state changes
                        audioTrack.addEventListener('mute', () => {
                            console.warn('Audio track was muted!');
                        });
                        
                        audioTrack.addEventListener('unmute', () => {
                            console.log('Audio track was unmuted!');
                        });
                        
                        audioTrack.addEventListener('ended', () => {
                            console.warn('Audio track ended!');
                        });
                        
                        // Set up periodic monitoring of track state
                        const monitorInterval = setInterval(() => {
                            if (!audioTrack || audioTrack.readyState === 'ended') {
                                clearInterval(monitorInterval);
                                return;
                            }
                            
                            if (audioTrack.muted) {
                                console.warn('Audio track is still muted, attempting to handle...');
                                // Try to recreate the audio element connection
                                remoteAudio.srcObject = null;
                                remoteAudio.srcObject = stream;
                                remoteAudio.play().catch(e => console.error('Play retry failed:', e));
                            }
                        }, 2000); // Check every 2 seconds
                        
                        // Store interval ID for cleanup
                        if (window.audioMonitorInterval) {
                            clearInterval(window.audioMonitorInterval);
                        }
                        window.audioMonitorInterval = monitorInterval;
                    }
                    
                    remoteAudio.srcObject = stream;
                    console.log('Assigned remote stream to audio element.');
                    console.log('Audio element paused:', remoteAudio.paused);
                    console.log('Audio element muted:', remoteAudio.muted);
                    console.log('Audio element volume:', remoteAudio.volume);
                    
                    // Ensure audio element settings
                    remoteAudio.muted = false;
                    remoteAudio.volume = 1.0;
                    
                    // Attempt to play audio programmatically after user interaction
                    remoteAudio.play()
                        .then(() => {
                            console.log('Audio playback started successfully');
                            console.log('Audio element paused after play:', remoteAudio.paused);
                            
                            // Additional check after play starts
                            setTimeout(() => {
                                const tracks = stream.getAudioTracks();
                                if (tracks.length > 0) {
                                    console.log('Audio track status after play:', {
                                        muted: tracks[0].muted,
                                        enabled: tracks[0].enabled,
                                        readyState: tracks[0].readyState
                                    });
                                    
                                    // Check if audio context is needed
                                    if (tracks[0].muted && window.AudioContext) {
                                        console.log('Track is muted, attempting AudioContext workaround...');
                                        try {
                                            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                                            const source = audioContext.createMediaStreamSource(stream);
                                            source.connect(audioContext.destination);
                                            console.log('AudioContext workaround applied');
                                        } catch (err) {
                                            console.error('AudioContext workaround failed:', err);
                                        }
                                    }
                                }
                            }, 1000);
                        })
                        .catch(e => console.error("Audio play failed:", e));
                } else {
                     console.warn("Received track event without streams.");
                     // Fallback for older browser compatibility if needed, but less common now
                }
            };

            // Handle connection state changes for debugging/status updates
             pc.onconnectionstatechange = event => {
                  statusDiv.textContent = `Connection State: ${pc.connectionState}`;
                  console.log(`Peer Connection State: ${pc.connectionState}`);
                  if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected' || pc.connectionState === 'closed') {
                      stopChat(); // Clean up if connection drops
                  }
             };

             pc.onicecandidateerror = event => {
                 console.error("ICE Candidate Error:", event);
                 statusDiv.textContent = `Error: ICE Candidate Error - ${event.errorCode}: ${event.errorText}`;
             };

             pc.onicegatheringstatechange = () => console.log(`ICE Gathering State: ${pc.iceGatheringState}`);

            // 4. Add local audio track for microphone input in the browser
            console.log('Requesting microphone access...');
            localStream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
            localStream.getTracks().forEach(track => {
                 pc.addTrack(track, localStream);
                 console.log('Local audio track added.');
             });

            // 5. Set up data channel for sending and receiving events
            dc = pc.createDataChannel("oai-events");
            console.log('Data channel created.');

            dc.onopen = () => {
                 console.log('Data channel opened.');
                 statusDiv.textContent = 'Data channel open. Ready to chat!';
                 // Example: Send initial configuration or greeting if needed
                 // dc.send(JSON.stringify({ type: 'configure', settings: {} }));
             };

            // =============================================================
            // === VVVVVVVVVVVV MODIFICATION START VVVVVVVVVVVV ===
            // =============================================================
            dc.onmessage = (event) => {
                // Log ALL raw messages for debugging tool calls
                console.log('Raw Data channel message received:', event.data);

                try {
                    const messageData = JSON.parse(event.data);

                    // Log ALL parsed message types for debugging
                    console.log(`Parsed message type: ${messageData.type}`, messageData);

                    // Check for function calling related events
                    if (messageData.type === "response.function_call_arguments.done") {
                        console.log("🚀 FUNCTION CALL DETECTED:", messageData);
                        // Emit to debug panel
                        if (window.debugSocket) {
                            window.debugSocket.emit('debug_message', {
                                type: 'function_call_detected',
                                data: messageData
                            });
                        }
                        
                        // Handle the function call by sending it to our Flask endpoint
                        handleFunctionCall(messageData);
                    }
                    
                    // Check for function call results
                    if (messageData.type === "response.function_call_arguments.delta") {
                        console.log("🔄 FUNCTION CALL ARGUMENTS DELTA:", messageData);
                    }

                    // Check for the specific event that contains the final transcript for an utterance
                    // Based on OpenAI docs and your transcript_seen.md, 'response.audio_transcript.done' is key.
                    if (messageData.type === "response.audio_transcript.done" && messageData.transcript) {
                        console.log("Received final transcript:", messageData.transcript);
                        // Check if the display function from print_transcript.js exists
                        if (typeof displayFinalTranscript === 'function') {
                            // Call the function to add the transcript to the page
                            displayFinalTranscript(messageData.transcript);
                        } else {
                            console.error("displayFinalTranscript function is not defined. Ensure print_transcript.js is loaded correctly before script.js tries to use it.");
                        }
                    }
                     // Add handlers for other potentially useful events if needed
                     else if (messageData.type === "error") {
                         console.error("Received error event from Realtime API:", messageData);
                         statusDiv.textContent = `Error: ${messageData.message || 'Unknown API error'}`;
                     }
                     else if (messageData.type === "session.created") {
                         console.log("Session created event received:", messageData.session);
                     }
                     // Check for any other function-related events
                     else if (messageData.type && messageData.type.includes("function")) {
                         console.log("🔍 FUNCTION-RELATED EVENT:", messageData.type, messageData);
                     }
                     // Check for response events that might indicate tool usage
                     else if (messageData.type && messageData.type.startsWith("response.")) {
                         console.log("📤 RESPONSE EVENT:", messageData.type, messageData);
                     }

                } catch (e) {
                    console.error("Failed to parse data channel message or handle event:", e);
                    console.error("Raw data received:", event.data); // Log raw data on error
                }
            };
            // =============================================================
            // === ^^^^^^^^^^^^ MODIFICATION END ^^^^^^^^^^^^ ===
            // =============================================================


             dc.onclose = () => {
                 console.log('Data channel closed.');
                 // Only update status if the connection isn't already closing/closed
                 if (pc && pc.connectionState !== 'closed' && pc.connectionState !== 'disconnected') {
                    statusDiv.textContent = 'Data channel closed.';
                 }
             };

             dc.onerror = (error) => {
                 console.error('Data channel error:', error);
                 statusDiv.textContent = `Error: Data channel error - ${error.message || 'Unknown error'}`;
             };

            // 6. Start the session using the Session Description Protocol (SDP)
            console.log('Creating SDP offer...');
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            console.log('Local description set.');

            const baseUrl = "https://api.openai.com/v1/realtime";
            // Use the model name obtained from the session endpoint
            const sdpResponse = await fetch(`${baseUrl}?model=${REALTIME_MODEL}`, {
                method: "POST",
                body: offer.sdp, // Send the SDP offer text directly
                headers: {
                    Authorization: `Bearer ${EPHEMERAL_KEY}`,
                    "Content-Type": "application/sdp" // Crucial header
                },
            });

            if (!sdpResponse.ok) {
                const errorText = await sdpResponse.text();
                 throw new Error(`SDP exchange failed: ${sdpResponse.status} ${sdpResponse.statusText} - ${errorText}`);
            }

            const answerSdp = await sdpResponse.text();
            console.log('Received SDP answer.');
            const answer = {
                type: "answer",
                sdp: answerSdp,
            };
            await pc.setRemoteDescription(answer);
            console.log('Remote description set. WebRTC setup complete.');
            // Status update moved to dc.onopen for better user feedback timing
            // statusDiv.textContent = 'Connected!';

        } catch (error) {
            console.error('Error starting chat:', error);
            statusDiv.textContent = `Error: ${error.message}`;
            stopChat(); // Clean up on error
            startButton.disabled = false;
            stopButton.disabled = true;
        }
    }

    function stopChat() {
        console.log('Stopping chat...');
        
        // Clear audio monitoring interval if it exists
        if (window.audioMonitorInterval) {
            clearInterval(window.audioMonitorInterval);
            window.audioMonitorInterval = null;
            console.log('Cleared audio monitoring interval');
        }
        
        if (dc) {
            // dc.onclose will handle status update unless connection already closed
            dc.close();
            dc = null; // Nullify after closing
            console.log('Data channel close initiated.');
        }
        if (pc) {
             // Stop sending tracks
             pc.getSenders().forEach(sender => {
                 if (sender.track) {
                     sender.track.stop();
                 }
             });
              // Stop receiving tracks (though srcObject = null is often sufficient)
              pc.getReceivers().forEach(receiver => {
                  if (receiver.track) {
                      receiver.track.stop();
                  }
              });

            // pc.onconnectionstatechange handles status update
            pc.close();
            pc = null; // Nullify after closing
            console.log('Peer connection close initiated.');
        }
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
            console.log('Local microphone stream stopped.');
        }
        // Clear the audio source
         if (remoteAudio) {
            remoteAudio.srcObject = null;
            remoteAudio.pause(); // Ensure it's paused
            remoteAudio.load(); // Reset the element
         }

        // Update status definitively if not already handled by events
        if (statusDiv.textContent !== 'Disconnected') {
             statusDiv.textContent = 'Disconnected';
        }
        startButton.disabled = false;
        stopButton.disabled = true;
        console.log('Chat stopped and resources released.');
    }
});