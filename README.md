# EV Blog Automation Suite

A simple tool to automatically generate and publish blog posts about electric vehicles to WordPress.

## Quick Start

1. **Install Python 3.6+** if you don't have it already

2. **Install the tool**:
   ```bash
   git clone https://github.com/harshafau/local-blog-automation.git
   cd local-blog-automation
   python3 setup.py
   ```

3. **Run the tool**:
   ```bash
   python3 run_web_interface.py
   ```

## What You Need

1. **Ollama with Gemma model** (for AI content):
   ```bash
   # Install Ollama from https://ollama.ai/download
   ollama pull gemma3:latest
   ```

2. **A Google Sheet** with your blog post data (must be publicly readable)

3. **WordPress site** with admin access

## Features

- 🖥️ Easy web interface
- 🤖 AI-powered content generation
- 📸 Automatic image search and download
- 📝 Direct WordPress publishing
- 📊 Google Sheets integration

## Support

If you need help:
1. Check the [troubleshooting guide](TROUBLESHOOTING.md)
2. Open an issue on GitHub

## License

MIT License - see [LICENSE](LICENSE) for details