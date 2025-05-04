#!/usr/bin/env python3
"""
Setup script for EV Blog Automation Suite

This script checks for required dependencies and installs them if needed.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is 3.6 or higher"""
    required_version = (3, 6)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current Python version: {current_version[0]}.{current_version[1]}")
        return False
    return True

def check_pip():
    """Check if pip is installed"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not working properly.")
        return False

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All required packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed"""
    system = platform.system()
    
    if system == "Windows":
        ollama_cmd = "where ollama"
    else:  # Linux or macOS
        ollama_cmd = "which ollama"
    
    try:
        subprocess.check_call(ollama_cmd, shell=True, 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        print("Ollama is installed.")
        return True
    except subprocess.CalledProcessError:
        print("Warning: Ollama is not installed or not in PATH.")
        print("The EV Blog Automation Suite requires Ollama for content generation.")
        print("Please install Ollama from: https://ollama.ai/download")
        return False

def check_gemma_model():
    """Check if Gemma model is available in Ollama"""
    try:
        result = subprocess.run(["ollama", "list"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if "gemma" in result.stdout.lower():
            print("Gemma model is available in Ollama.")
            return True
        else:
            print("Warning: Gemma model is not available in Ollama.")
            print("The EV Blog Automation Suite requires the Gemma model for content generation.")
            print("You can install it with: ollama pull gemma3:latest")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If Ollama is not installed, we already warned about it
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "temp/images", "templates", "static/css", "static/js"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Created necessary directories.")
    return True

def main():
    """Main setup function"""
    print("Setting up EV Blog Automation Suite...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Check Ollama (optional)
    ollama_installed = check_ollama()
    
    # Check Gemma model (optional)
    if ollama_installed:
        check_gemma_model()
    
    print("\nSetup completed successfully!")
    print("\nTo run the EV Blog Automation Suite, use:")
    print("  python3 run_web_interface.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
