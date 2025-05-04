# Troubleshooting Guide

## Common Issues and Solutions

### 1. Python Installation Issues
- **Error**: "Python not found"
- **Solution**: Install Python 3.6 or higher from [python.org](https://www.python.org/downloads/)

### 2. Package Installation Issues
- **Error**: "Module not found"
- **Solution**: Run `python3 setup.py` again

### 3. Ollama Issues
- **Error**: "Ollama not found"
- **Solution**: 
  1. Install Ollama from [ollama.ai/download](https://ollama.ai/download)
  2. Run `ollama pull gemma3:latest`

### 4. Google Sheets Access
- **Error**: "Cannot access Google Sheet"
- **Solution**: Make sure your Google Sheet is:
  1. Publicly readable
  2. Has correct column names
  3. Has valid data

### 5. WordPress Connection
- **Error**: "Cannot connect to WordPress"
- **Solution**: Check:
  1. WordPress URL is correct
  2. Username/password are correct
  3. WordPress site is accessible

### 6. Port Already in Use
- **Error**: "Port 8000 is already in use"
- **Solution**: The app will automatically try different ports

## Still Having Issues?

1. Check the logs in the `logs/` directory
2. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Log files (if any) 