import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
SPREADSHEET_ID = ""  # Will be set from web interface
WORKSHEET_NAME = 'Blog Posts'

# WordPress Configuration
WORDPRESS_URL = ""  # Will be set from web interface
WORDPRESS_USERNAME = ""  # Will be set from web interface
WORDPRESS_PASSWORD = ""  # Will be set from web interface

# LLM Configuration
OLLAMA_URL = 'http://localhost:11434'
MODEL_NAME = 'gemma3:latest'

# Image Configuration
MAX_IMAGES_PER_POST = 3
IMAGE_DOWNLOAD_PATH = 'temp/images'
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
DEFAULT_IMAGE_PATH = 'assets/default_images'  # Fallback directory for default images

# Logging Configuration
LOG_FILE = 'logs/blog_publisher.log'
LOG_LEVEL = 'INFO'

# Content Configuration
REQUIRED_ELEMENTS = {
    'table': '<table>',
    'bullet_points': '<ul>',
    'image_slider': '<div class="image-slider">',
    'code_block': '<pre><code>'
}

# Google AdSense Configuration
ADSENSE_SCRIPT = """
<div class="adsense-container">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4921107726870735"
         crossorigin="anonymous"></script>
    <!-- new ad 15 apr -->
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-4921107726870735"
         data-ad-slot="6937559389"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</div>
"""