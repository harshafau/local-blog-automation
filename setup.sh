#!/bin/bash
# Setup script for EV Blog Automation Suite

echo "Setting up EV Blog Automation Suite..."

# Create necessary directories
mkdir -p logs
mkdir -p temp/images
mkdir -p modules/webdriver

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run the setup.py script
echo "Running setup script..."
python3 setup.py

echo "Setup complete! You can now run the web interface with:"
echo "python3 run_web_interface.py"
