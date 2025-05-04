import os
import logging
from datetime import datetime
from modules.google_sheets import GoogleSheetsManager
from modules.content_processor import ContentProcessor
from modules.wordpress_integration import WordPressIntegration
from modules.llm_integration import LLMIntegration
from modules.image_handler import ImageHandler
from config.config import LOG_FILE, LOG_LEVEL

def setup_logging():
    """Setup logging configuration"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

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

def main():
    """Main function to orchestrate the blog publishing process"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting blog publishing process")

        # Initialize components
        sheets_manager = GoogleSheetsManager()
        content_processor = ContentProcessor()
        wordpress = WordPressIntegration()
        llm = LLMIntegration()
        image_handler = ImageHandler()

        # Get blog data from Google Sheets
        blog_data = sheets_manager.get_blog_data()
        if not blog_data:
            logger.warning("No blog data found in Google Sheets")
            return

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
                    keywords=post_data['keywords']
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

                # Generate content using LLaMA
                logger.info(f"Generating content for: {post_data['title']}")
                logger.info(f"Topic: {post_data['topic']}")
                logger.info(f"Keywords: {post_data['keywords']}")
                logger.info(f"Context: {post_data['context']}")
                
                markdown_content = llm.generate_content(
                    title=post_data['title'],
                    topic=post_data['topic'],
                    keywords=post_data['keywords'],
                    context=post_data['context']
                )
                logger.info("Generated content using LLaMA")

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
                logger.info("Note: Sheet status cannot be updated as the sheet is public")

            except Exception as e:
                logger.error(f"Error processing post {post_data.get('title', 'Unknown')}: {str(e)}")
                continue

        logger.info("Blog publishing process completed")

    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 