import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import logging
from config.config import IMAGE_DOWNLOAD_PATH, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGES_PER_POST

class ImageProcessor:
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.setup_selenium()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def setup_directories(self):
        """Create necessary directories for image storage"""
        os.makedirs(IMAGE_DOWNLOAD_PATH, exist_ok=True)

    def setup_selenium(self):
        """Setup Selenium WebDriver for image scraping"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def search_images(self, query, max_images=MAX_IMAGES_PER_POST):
        """Search for images using Google Images"""
        try:
            search_url = f"https://www.google.com/search?q={query}&tbm=isch"
            self.driver.get(search_url)
            
            # Wait for images to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.rg_i"))
            )
            
            # Get image URLs
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
            image_urls = []
            
            for img in image_elements[:max_images]:
                try:
                    img_url = img.get_attribute('src')
                    if img_url and img_url.startswith('http'):
                        image_urls.append(img_url)
                except Exception as e:
                    self.logger.warning(f"Error getting image URL: {str(e)}")
            
            return image_urls
        except Exception as e:
            self.logger.error(f"Error searching images: {str(e)}")
            return []

    def download_image(self, url, filename):
        """Download and save an image"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get file extension
            ext = os.path.splitext(url)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                ext = '.jpg'  # Default extension
            
            filepath = os.path.join(IMAGE_DOWNLOAD_PATH, f"{filename}{ext}")
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return filepath
        except Exception as e:
            self.logger.error(f"Error downloading image: {str(e)}")
            return None

    def process_images(self, topic, max_images=MAX_IMAGES_PER_POST):
        """Process images for a blog post"""
        try:
            # Search for images
            image_urls = self.search_images(topic, max_images)
            if not image_urls:
                self.logger.warning(f"No images found for topic: {topic}")
                return []

            # Download images
            downloaded_images = []
            for i, url in enumerate(image_urls):
                filename = f"{topic.replace(' ', '_')}_{i}"
                filepath = self.download_image(url, filename)
                if filepath:
                    downloaded_images.append(filepath)

            return downloaded_images
        except Exception as e:
            self.logger.error(f"Error processing images: {str(e)}")
            return []

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}") 