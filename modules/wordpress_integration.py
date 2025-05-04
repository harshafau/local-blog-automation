import requests
import logging
import os
import mimetypes
from config.config import WORDPRESS_URL as DEFAULT_WORDPRESS_URL
from config.config import WORDPRESS_USERNAME as DEFAULT_WORDPRESS_USERNAME
from config.config import WORDPRESS_PASSWORD as DEFAULT_WORDPRESS_PASSWORD

class WordPressIntegration:
    def __init__(self, wordpress_url=None, wordpress_username=None, wordpress_password=None):
        self.setup_logging()

        # Use provided values or fall back to defaults
        self.wordpress_url = (wordpress_url or DEFAULT_WORDPRESS_URL).rstrip('/')
        self.wordpress_username = wordpress_username or DEFAULT_WORDPRESS_USERNAME
        self.wordpress_password = wordpress_password or DEFAULT_WORDPRESS_PASSWORD

        # Validate WordPress URL
        if not self.wordpress_url:
            self.logger.error("No WordPress URL provided")
            raise ValueError("No WordPress URL provided. Please enter a valid WordPress URL.")

        # Ensure URL has a scheme
        if not self.wordpress_url.startswith(('http://', 'https://')):
            self.logger.error(f"Invalid WordPress URL (missing http:// or https://): {self.wordpress_url}")
            raise ValueError(f"Invalid WordPress URL: {self.wordpress_url}. URL must start with http:// or https://")

        # Set up API endpoints
        self.base_url = f"{self.wordpress_url}/wp-json/wp/v2"
        self.media_base_url = f"{self.wordpress_url}/wp-content/uploads"
        self.auth = (self.wordpress_username, self.wordpress_password)

        self.logger.info(f"Initialized WordPress integration for {self.wordpress_url}")

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def get_mime_type(self, file_path):
        """Get the MIME type of a file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'image/jpeg'

    def upload_media(self, image_path):
        """Upload an image to WordPress media library"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            mime_type = self.get_mime_type(image_path)
            filename = os.path.basename(image_path)

            with open(image_path, 'rb') as image_file:
                files = {
                    'file': (filename, image_file, mime_type)
                }
                headers = {
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }

                response = requests.post(
                    f"{self.base_url}/media",
                    auth=self.auth,
                    files=files,
                    headers=headers
                )

                response.raise_for_status()
                media_data = response.json()

                if 'id' not in media_data or 'source_url' not in media_data:
                    raise ValueError("No media ID or source URL in WordPress response")

                media_id = media_data['id']
                image_url = media_data['source_url']
                self.logger.info(f"Successfully uploaded image: {filename} -> ID: {media_id}, URL: {image_url}")
                return {'id': media_id, 'url': image_url}

        except Exception as e:
            self.logger.error(f"Error uploading image {image_path}: {str(e)}")
            raise

    def create_post(self, title, content, featured_media=None, status='publish'):
        """Create a new blog post with optional featured image"""
        try:
            post_data = {
                'title': title,
                'content': content,
                'status': status
            }

            if featured_media:
                # featured_media should be the media ID
                post_data['featured_media'] = int(featured_media)

            response = requests.post(
                f"{self.base_url}/posts",
                auth=self.auth,
                json=post_data
            )
            response.raise_for_status()
            post_id = response.json()['id']
            self.logger.info(f"Successfully created post with ID: {post_id}")
            return post_id
        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            raise

    def publish_post(self, title, content, featured_image_path=None):
        """Publish a blog post with optional featured image"""
        try:
            featured_media_id = None
            if featured_image_path:
                media_data = self.upload_media(featured_image_path)
                featured_media_id = media_data['id']

            # Create and publish the post
            post_id = self.create_post(
                title=title,
                content=content,
                featured_media=featured_media_id
            )

            self.logger.info(f"Successfully published post with ID: {post_id}")
            return post_id
        except Exception as e:
            self.logger.error(f"Error publishing post: {str(e)}")
            raise