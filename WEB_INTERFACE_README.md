# Blog Automation Web Interface

This web interface allows you to easily configure and run the blog automation tool through a user-friendly browser interface.

## Features

- Simple form to input your configuration parameters
- Real-time terminal output display
- Customizable article length and image count
- No need to edit configuration files manually

## Setup

1. Make sure you have all the required dependencies installed:

```bash
pip install -r requirements.txt
```

2. Make sure Ollama is installed and running with the Gemma model:

```bash
ollama run gemma3:latest
```

3. Run the web interface:

```bash
python run_web_interface.py
```

This will automatically open your default web browser to the interface at http://localhost:5000.

## Using the Web Interface

1. **Enter your configuration details:**
   - Google Sheet ID: The ID from your Google Sheets URL
   - WordPress URL: Your WordPress site URL
   - WordPress Username: Your WordPress admin username
   - WordPress Password: Your WordPress admin password
   - Number of Images (Optional): Maximum number of images per post (default: 3)
   - Article Length: Target word count for generated articles (default: 1000)

2. **Click "Generate Articles"** to start the process

3. **Monitor the process** in the terminal output display on the right side

## Troubleshooting

- If you encounter any issues with the web interface, check the logs in the `logs` directory
- Make sure Ollama is running and the Gemma model is installed
- Verify that your Google Sheet is publicly accessible for reading
- Ensure your WordPress credentials are correct and have publishing permissions

## Notes

- The web interface runs locally on your machine and does not send your credentials to any external servers
- All processing happens on your local machine, including LLM content generation through Ollama
- Your WordPress credentials are only used to publish posts to your WordPress site
