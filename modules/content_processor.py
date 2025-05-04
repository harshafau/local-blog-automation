import markdown2
import logging
import os
import re
from urllib.parse import urlparse
from config.config import REQUIRED_ELEMENTS, ADSENSE_SCRIPT
from modules.wordpress_integration import WordPressIntegration

class ContentProcessor:
    def __init__(self, wordpress_integration=None):
        self.setup_logging()
        self.adsense_script = ADSENSE_SCRIPT
        # Use the provided WordPress integration or create a new one
        self.wordpress = wordpress_integration or WordPressIntegration()
        self.logger.info("ContentProcessor initialized")

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def is_valid_url(self, url):
        """Check if the given string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def convert_markdown_to_html(self, markdown_content):
        """Convert markdown content to HTML"""
        try:
            # Convert markdown to HTML
            html_content = markdown2.markdown(
                markdown_content,
                extras=['tables', 'fenced-code-blocks', 'break-on-newline']
            )
            return html_content
        except Exception as e:
            self.logger.error(f"Error converting markdown to HTML: {str(e)}")
            raise

    def insert_images(self, html_content, image_paths):
        """Insert images into the HTML content with proper structure"""
        try:
            if not image_paths:
                self.logger.warning("No images provided for insertion")
                return html_content

            # Upload images to WordPress and get their URLs
            image_data = []
            for img_path in image_paths:
                try:
                    if not os.path.exists(img_path):
                        self.logger.error(f"Image file not found: {img_path}")
                        continue

                    media_data = self.wordpress.upload_media(img_path)
                    if media_data:
                        image_data.append(media_data)
                        self.logger.info(f"Successfully uploaded and added image: {img_path}")
                except Exception as e:
                    self.logger.error(f"Error uploading image {img_path}: {str(e)}")
                    continue

            if not image_data:
                self.logger.warning("No images were successfully uploaded")
                return html_content

            # Split content into paragraphs
            paragraphs = html_content.split('</p>')
            new_content = []
            image_index = 0

            # Process each paragraph
            for i, paragraph in enumerate(paragraphs):
                new_content.append(paragraph)

                # Add AdSense after the first paragraph (intro)
                if i == 0:
                    new_content.append(self.adsense_script)

                # Add image after every second paragraph (except the last one)
                if i % 2 == 1 and i < len(paragraphs) - 1 and image_index < len(image_data):
                    img_data = image_data[image_index]
                    new_content.append(f"""
                    <div class="blog-image-container" style="margin: 20px 0; text-align: center;">
                        <img src="{img_data['url']}"
                             alt="Blog image"
                             class="blog-image"
                             style="max-width: 100%; height: auto; border-radius: 8px;"
                             loading="lazy">
                    </div>
                    """)
                    image_index += 1

                    # Add AdSense after every image
                    new_content.append(self.adsense_script)

                if i < len(paragraphs) - 1:
                    new_content.append('</p>')

            # Add any remaining images at the end
            while image_index < len(image_data):
                img_data = image_data[image_index]
                new_content.append(f"""
                <div class="blog-image-container" style="margin: 20px 0; text-align: center;">
                    <img src="{img_data['url']}"
                         alt="Blog image"
                         class="blog-image"
                         style="max-width: 100%; height: auto; border-radius: 8px;"
                         loading="lazy">
                </div>
                """)
                image_index += 1

                # Add AdSense after the last image
                if image_index == len(image_data):
                    new_content.append(self.adsense_script)

            html_content = ''.join(new_content)
            self.logger.info(f"Successfully inserted {len(image_data)} images into content")
            return html_content
        except Exception as e:
            self.logger.error(f"Error inserting images: {str(e)}")
            return html_content

    def add_required_elements(self, html_content, required_elements):
        """Add required elements to the HTML content"""
        try:
            # Check for required elements
            for element in required_elements:
                if element in REQUIRED_ELEMENTS:
                    if REQUIRED_ELEMENTS[element] not in html_content:
                        self.logger.info(f"Adding {element} to content")
                        if element == 'table':
                            html_content += self._create_sample_table()
                        elif element == 'bullet_points':
                            html_content += self._create_bullet_points()
                        elif element == 'image_slider':
                            html_content += self._create_image_slider()
                        elif element == 'code_block':
                            html_content += self._create_code_block()

            return html_content
        except Exception as e:
            self.logger.error(f"Error adding required elements: {str(e)}")
            raise

    def _create_sample_table(self):
        """Create a sample table"""
        return """
        <table>
            <thead>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Data 1</td>
                    <td>Data 2</td>
                </tr>
            </tbody>
        </table>
        """

    def _create_bullet_points(self):
        """Create bullet points"""
        return """
        <ul>
            <li>Point 1</li>
            <li>Point 2</li>
            <li>Point 3</li>
        </ul>
        """

    def _create_image_slider(self):
        """Create image slider HTML"""
        return """
        <div class="image-slider">
            <div class="slider-container">
                <!-- Images will be added dynamically -->
            </div>
        </div>
        """

    def _create_code_block(self):
        """Create code block"""
        return """
        <pre><code>
        // Sample code block
        function example() {
            console.log("Hello, World!");
        }
        </code></pre>
        """

    def insert_adsense(self, html_content):
        """Insert AdSense script into the HTML content"""
        try:
            # Insert AdSense after the first paragraph
            paragraphs = html_content.split('</p>')
            if len(paragraphs) > 1:
                paragraphs[1] = paragraphs[1] + self.adsense_script
                html_content = '</p>'.join(paragraphs)
            else:
                html_content += self.adsense_script

            self.logger.info("Successfully inserted AdSense into content")
            return html_content
        except Exception as e:
            self.logger.error(f"Error inserting AdSense: {str(e)}")
            return html_content