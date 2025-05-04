import os
import sys
import logging
import threading
import queue
import requests
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from config.config import LOG_FILE, LOG_LEVEL

# Import the main functionality
from modules.google_sheets import GoogleSheetsManager
from modules.content_processor import ContentProcessor
from modules.wordpress_integration import WordPressIntegration
from modules.llm_integration import LLMIntegration
from modules.image_handler import ImageHandler

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Queue for storing log messages
log_queue = queue.Queue()

# Custom log handler to capture logs for the web interface
class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

# Setup logging
def setup_logging():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Setup file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    # Setup stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Setup queue handler for web interface
    queue_handler = QueueHandler(log_queue)
    queue_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(queue_handler)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Function to run the blog automation process
def run_blog_automation(spreadsheet_id, wordpress_url, wordpress_username, wordpress_password, num_images=3, article_length=1000):
    # Ensure numeric parameters are integers
    num_images = int(num_images)
    article_length = int(article_length)
    try:
        logger.info(f"Starting blog publishing process with custom parameters:")
        logger.info(f"  - Google Sheet ID: {spreadsheet_id}")
        logger.info(f"  - WordPress URL: {wordpress_url}")
        logger.info(f"  - Number of Images: {num_images}")
        logger.info(f"  - Article Length: {article_length} words")

        # Override config values with user input
        from config import config
        config.SPREADSHEET_ID = spreadsheet_id
        config.WORDPRESS_URL = wordpress_url
        config.WORDPRESS_USERNAME = wordpress_username
        config.WORDPRESS_PASSWORD = wordpress_password
        config.MAX_IMAGES_PER_POST = int(num_images)

        # Initialize components
        sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)

        # Initialize WordPress integration with user credentials
        wordpress = WordPressIntegration(
            wordpress_url=wordpress_url,
            wordpress_username=wordpress_username,
            wordpress_password=wordpress_password
        )

        # Pass WordPress integration to ContentProcessor
        content_processor = ContentProcessor(wordpress_integration=wordpress)

        llm = LLMIntegration()
        image_handler = ImageHandler()

        # Get blog data from Google Sheets
        try:
            blog_data = sheets_manager.get_blog_data()
            if not blog_data:
                logger.warning("No blog data found in Google Sheets")
                return
        except ValueError as e:
            logger.error(f"Google Sheets error: {str(e)}")
            raise
        except requests.exceptions.HTTPError as e:
            if "404" in str(e):
                logger.error(f"Google Sheet not found or not accessible: {spreadsheet_id}")
                raise ValueError(f"Google Sheet not found or not accessible. Please check the Sheet ID and make sure it's publicly accessible: {spreadsheet_id}")
            else:
                logger.error(f"HTTP error accessing Google Sheet: {str(e)}")
                raise

        # Process each blog post
        for post in blog_data:
            try:
                # Clean and format the post data
                post_data = clean_sheet_data(post)
                logger.info(f"Processing post: {post_data}")

                # Skip if already published
                if post_data['status'].lower() == 'published ✅':
                    logger.info(f"Skipping already published post: {post_data['title']}")
                    continue

                # Skip if title is empty
                if not post_data['title']:
                    logger.warning("Skipping post with empty title")
                    continue

                # Search and download images
                logger.info(f"Searching for images for: {post_data['title']}")
                images = image_handler.search_and_download_images(
                    topic=post_data['topic'],
                    keywords=post_data['keywords'],
                    num_images=int(num_images)
                )

                if not images:
                    logger.warning(f"No images found for post: {post_data['title']}")
                    continue

                # Select featured image
                featured_image = image_handler.select_featured_image(images)
                if not featured_image:
                    logger.warning(f"Could not select featured image for post: {post_data['title']}")
                    continue

                # Remove featured image from content images
                content_images = [img for img in images if img != featured_image]

                # Generate content using LLM
                logger.info(f"Generating content for: {post_data['title']}")
                logger.info(f"Topic: {post_data['topic']}")
                logger.info(f"Keywords: {post_data['keywords']}")
                logger.info(f"Context: {post_data['context']}")
                logger.info(f"Target article length: {article_length} words")

                markdown_content = llm.generate_content(
                    title=post_data['title'],
                    topic=post_data['topic'],
                    keywords=post_data['keywords'],
                    context=post_data['context'],
                    word_count=article_length
                )
                logger.info("Generated content using LLM")

                # Convert markdown to HTML
                html_content = content_processor.convert_markdown_to_html(markdown_content)
                logger.info("Converted markdown to HTML")

                # Add required elements if specified
                if post_data['must_have_elements']:
                    required_elements = [elem.strip() for elem in post_data['must_have_elements'].split(',')]
                    logger.info(f"Adding required elements: {required_elements}")
                    html_content = content_processor.add_required_elements(html_content, required_elements)

                # Insert images into content (excluding featured image)
                logger.info("Inserting images into content")
                html_content = content_processor.insert_images(html_content, content_images)

                # Insert AdSense
                html_content = content_processor.insert_adsense(html_content)
                logger.info("Added AdSense to content")

                # Publish to WordPress with featured image
                logger.info(f"Publishing post: {post_data['title']}")
                post_id = wordpress.publish_post(
                    title=post_data['title'],
                    content=html_content,
                    featured_image_path=featured_image
                )

                # Log success
                logger.info(f"Successfully published post: {post_data['title']} (ID: {post_id})")

            except Exception as e:
                logger.error(f"Error processing post {post_data.get('title', 'Unknown')}: {str(e)}")
                continue

        logger.info("Blog publishing process completed")

    except Exception as e:
        logger.error(f"Fatal error in blog automation process: {str(e)}")
        raise

def clean_sheet_data(post):
    """Clean and format data from Google Sheets"""
    # Get images and clean them
    images = post.get('images', '')
    if images:
        # Split by comma and clean each URL/path
        image_list = [img.strip() for img in images.split(',') if img.strip()]
    else:
        image_list = []

    return {
        'title': post.get('title', '').strip(),
        'topic': post.get('topic name', '').strip(),
        'keywords': post.get('keywords', '').strip().strip('"'),
        'context': post.get('context', '').strip().strip('"'),
        'status': post.get('status', '').strip().strip('"'),
        'must_have_elements': post.get('must have elements', '').strip().strip('"'),
        'images': image_list
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get form data
        spreadsheet_id = request.form.get('spreadsheet_id', '').strip()
        wordpress_url = request.form.get('wordpress_url', '').strip()
        wordpress_username = request.form.get('wordpress_username', '').strip()
        wordpress_password = request.form.get('wordpress_password', '').strip()
        num_images = int(request.form.get('num_images', '3'))
        article_length = int(request.form.get('article_length', '1000'))

        # Validate required fields
        missing_fields = []
        if not spreadsheet_id:
            missing_fields.append("Google Sheet ID")
        if not wordpress_url:
            missing_fields.append("WordPress URL")
        if not wordpress_username:
            missing_fields.append("WordPress Username")
        if not wordpress_password:
            missing_fields.append("WordPress Password")

        if missing_fields:
            error_message = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_message)
            return jsonify({'status': 'error', 'message': error_message})

        # Validate Google Sheet ID format
        if not spreadsheet_id or len(spreadsheet_id) < 10:
            error_message = "Invalid Google Sheet ID. Please enter a valid ID from your Google Sheets URL."
            logger.error(error_message)
            return jsonify({'status': 'error', 'message': error_message})

        # Validate WordPress URL format
        if not wordpress_url.startswith(('http://', 'https://')):
            error_message = "Invalid WordPress URL. Please include http:// or https://"
            logger.error(error_message)
            return jsonify({'status': 'error', 'message': error_message})

        # Start the blog automation process in a separate thread
        thread = threading.Thread(
            target=run_blog_automation,
            args=(spreadsheet_id, wordpress_url, wordpress_username, wordpress_password, num_images, article_length)
        )
        thread.daemon = True
        thread.start()

        logger.info(f"Started blog automation process with Sheet ID: {spreadsheet_id}, WordPress URL: {wordpress_url}")
        return jsonify({'status': 'success', 'message': 'Blog automation process started'})

    except ValueError as e:
        error_message = str(e)
        logger.error(f"Validation error: {error_message}")
        return jsonify({'status': 'error', 'message': error_message})
    except Exception as e:
        error_message = f"Error starting blog automation: {str(e)}"
        logger.error(error_message)
        return jsonify({'status': 'error', 'message': error_message})

@app.route('/logs')
def logs():
    def generate():
        while True:
            try:
                # Get log message from queue (non-blocking)
                log_message = log_queue.get(block=False)
                yield f"data: {log_message}\n\n"
            except queue.Empty:
                # If queue is empty, yield a heartbeat to keep connection alive
                yield f"data: heartbeat\n\n"
                import time
                time.sleep(0.5)

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

@app.after_request
def add_header(response):
    """Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes."""
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
