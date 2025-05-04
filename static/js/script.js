document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const form = document.getElementById('blogForm');
    const generateBtn = document.getElementById('generateBtn');
    const logsContainer = document.getElementById('logs');
    const terminal = document.getElementById('terminal');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = statusIndicator.querySelector('.status-text');
    const clearLogsBtn = document.getElementById('clearLogsBtn');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('wordpress_password');
    const helpLink = document.getElementById('helpLink');
    const aboutLink = document.getElementById('aboutLink');
    const helpModal = document.getElementById('helpModal');
    const closeModalBtn = document.querySelector('.close-modal');

    // Function to scroll terminal to bottom
    function scrollToBottom() {
        terminal.scrollTop = terminal.scrollHeight;
    }

    // Function to update status indicator
    function updateStatus(status, message) {
        statusIndicator.className = 'status-indicator ' + status;
        statusText.textContent = message;

        if (status === 'processing') {
            generateBtn.disabled = true;
            generateBtn.classList.add('loading');
        } else {
            generateBtn.disabled = false;
            generateBtn.classList.remove('loading');
        }
    }

    // Function to format log messages with colors
    function formatLogMessage(message) {
        if (message.includes('ERROR') || message.includes('Error')) {
            return `<span class="error">${message}</span>`;
        } else if (message.includes('WARNING') || message.includes('Warning')) {
            return `<span class="warning">${message}</span>`;
        } else if (message.includes('SUCCESS') || message.includes('Successfully')) {
            return `<span class="success">${message}</span>`;
        } else if (message.includes('INFO') || message.includes('Starting')) {
            return `<span class="info">${message}</span>`;
        }
        return message;
    }

    // Toggle password visibility
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Toggle icon
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    // Clear logs button
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', function() {
            logsContainer.innerHTML = 'Logs cleared. Ready for new process.\n';
            updateStatus('', 'Ready');
        });
    }

    // Modal functionality
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
        }
    }

    function closeModal() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            modal.classList.remove('show');
        });
    }

    // Help link
    if (helpLink) {
        helpLink.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('helpModal');
        });
    }

    // About link
    if (aboutLink) {
        aboutLink.addEventListener('click', function(e) {
            e.preventDefault();
            openModal('helpModal');
        });
    }

    // Close modal button
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal();
        }
    });

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Update status
        updateStatus('processing', 'Processing...');

        // Clear previous logs
        logsContainer.innerHTML = '';

        // Get form data
        const formData = new FormData(form);

        // Send AJAX request
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Add initial message
                logsContainer.innerHTML += formatLogMessage('Starting blog automation process...\n\n');
                scrollToBottom();

                // Start listening for log events
                startLogStream();
            } else {
                // Show error
                updateStatus('error', 'Error');

                // Format the error message
                let errorMessage = data.message;

                // Special handling for common errors
                if (errorMessage.includes("Google Sheet not found") || errorMessage.includes("No Google Sheet ID provided")) {
                    errorMessage = `📋 ${errorMessage}\n\nPlease check that:\n- You entered the correct Google Sheet ID\n- The Google Sheet is publicly accessible\n- The Sheet contains the required columns`;
                } else if (errorMessage.includes("WordPress")) {
                    errorMessage = `🌐 ${errorMessage}\n\nPlease check that:\n- Your WordPress URL is correct\n- Your username and password are correct\n- Your WordPress site is accessible`;
                } else if (errorMessage.includes("Ollama")) {
                    errorMessage = `🤖 ${errorMessage}\n\nPlease check that:\n- Ollama is installed and running\n- The Gemma model is installed\n- You can run: ollama run gemma3:latest`;
                }

                logsContainer.innerHTML += formatLogMessage(`Error: ${errorMessage}\n`);
                scrollToBottom();
            }
        })
        .catch(error => {
            updateStatus('error', 'Error');
            logsContainer.innerHTML += formatLogMessage(`Error: ${error.message}\n`);
            scrollToBottom();
        });
    });

    // Function to start listening for log events
    function startLogStream() {
        // Add initial connection message
        logsContainer.innerHTML += formatLogMessage('Connecting to log stream...\n');
        scrollToBottom();

        // Create event source with retry mechanism
        let retryCount = 0;
        const maxRetries = 3;
        let eventSource;

        function connectEventSource() {
            eventSource = new EventSource('/logs');

            eventSource.onopen = function() {
                retryCount = 0;
                logsContainer.innerHTML += formatLogMessage('Connected to log stream. Waiting for process to start...\n');
                scrollToBottom();
            };

            eventSource.onmessage = function(event) {
                // Skip heartbeat messages
                if (event.data === 'heartbeat') return;

                // Add log message to terminal
                logsContainer.innerHTML += formatLogMessage(event.data) + '\n';
                scrollToBottom();

                // Update status based on log content
                if (event.data.includes('ERROR') || event.data.includes('Error')) {
                    updateStatus('error', 'Error');
                }

                // Check if process is complete
                if (event.data.includes('Blog publishing process completed')) {
                    // Close the event source
                    eventSource.close();

                    // Update status
                    updateStatus('', 'Completed');

                    // Add completion message
                    logsContainer.innerHTML += formatLogMessage('\nProcess finished successfully. You can generate more articles.\n');
                    scrollToBottom();
                } else if (event.data.includes('Fatal error in blog automation process')) {
                    // Close the event source
                    eventSource.close();

                    // Update status
                    updateStatus('error', 'Failed');

                    // Add completion message
                    logsContainer.innerHTML += formatLogMessage('\nProcess failed. Please check the logs for errors.\n');
                    scrollToBottom();
                }
            };

            eventSource.onerror = function(e) {
                // Close the current event source
                eventSource.close();

                // Try to reconnect if we haven't exceeded max retries
                if (retryCount < maxRetries) {
                    retryCount++;
                    logsContainer.innerHTML += formatLogMessage(`\nLog stream disconnected. Attempting to reconnect (${retryCount}/${maxRetries})...\n`);
                    scrollToBottom();

                    // Wait before reconnecting
                    setTimeout(connectEventSource, 2000);
                } else {
                    // Give up after max retries
                    updateStatus('error', 'Disconnected');
                    logsContainer.innerHTML += formatLogMessage('\nCould not maintain connection to log stream. The process may still be running in the background.\n');
                    logsContainer.innerHTML += formatLogMessage('You can refresh the page to try reconnecting.\n');
                    scrollToBottom();
                }
            };
        }

        // Start the connection
        connectEventSource();
    }
});
