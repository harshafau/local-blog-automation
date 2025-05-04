#!/usr/bin/env python3
"""
EV Blog Automation Web Interface Launcher

This script launches the web interface for the EV Blog Automation Suite.
"""

import os
import sys
import webbrowser
import time
import socket
import importlib.util

# Check if required modules are installed
required_modules = ['flask', 'requests', 'selenium', 'dotenv']

missing_modules = []
for module in required_modules:
    if importlib.util.find_spec(module) is None:
        missing_modules.append(module)

if missing_modules:
    print("Error: Missing required Python modules:")
    for module in missing_modules:
        print(f"  - {module}")
    print("\nPlease run the setup script to install dependencies:")
    print("  python3 setup.py")
    print("\nOr install them manually:")
    print(f"  pip install {' '.join(missing_modules)}")
    sys.exit(1)

# Import app after checking dependencies
from web_interface import app

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    port = start_port
    for _ in range(max_attempts):
        if check_port_available(port):
            return port
        port += 1
    return start_port  # Default fallback

if __name__ == "__main__":
    try:
        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('temp/images', exist_ok=True)

        # Find an available port
        port = find_available_port(8000)

        # Print startup message
        print("\n" + "="*60)
        print(f"Starting Blog Automation Web Interface on port {port}...")
        print(f"The web interface will be available at: http://127.0.0.1:{port}")
        print("="*60 + "\n")

        # Open browser after a short delay
        def open_browser():
            time.sleep(2)  # Longer delay to ensure server is ready
            try:
                url = f'http://127.0.0.1:{port}'
                print(f"Opening browser to {url}")
                # Try different browser opening methods
                try:
                    webbrowser.get('chrome').open(url)
                except:
                    try:
                        webbrowser.get('firefox').open(url)
                    except:
                        webbrowser.open(url)
                print("Browser opened successfully. If you don't see the interface, manually navigate to the URL above.")
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print(f"Please manually open your browser and go to: http://127.0.0.1:{port}")

        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Start the Flask app with host explicitly set to 0.0.0.0 to allow all interfaces
        print("Starting web server...")
        app.run(host='0.0.0.0', debug=False, port=port)

    except Exception as e:
        print(f"Error starting web interface: {e}")
        print("Please check if you have the required dependencies installed:")
        print("  pip install flask")
        import traceback
        traceback.print_exc()
