import requests
import logging
from config.config import SPREADSHEET_ID as DEFAULT_SPREADSHEET_ID

class GoogleSheetsManager:
    def __init__(self, spreadsheet_id=None):
        self.setup_logging()
        # Use the provided spreadsheet_id or fall back to the config value
        self.spreadsheet_id = spreadsheet_id if spreadsheet_id else DEFAULT_SPREADSHEET_ID
        self.logger.info(f"GoogleSheetsManager initialized with spreadsheet ID: {self.spreadsheet_id}")

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def get_blog_data(self):
        """Fetch blog post data from public Google Sheet"""
        try:
            # Check if spreadsheet ID is provided
            if not self.spreadsheet_id:
                self.logger.error("No Google Sheet ID provided. Please enter a valid Google Sheet ID.")
                raise ValueError("No Google Sheet ID provided. Please enter a valid Google Sheet ID in the form.")

            # Convert the spreadsheet ID to a CSV export URL
            csv_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/export?format=csv"
            self.logger.info(f"Fetching data from Google Sheet: {self.spreadsheet_id}")

            # Fetch the CSV data
            response = requests.get(csv_url)
            response.raise_for_status()

            # Parse CSV data
            csv_data = response.text.split('\n')
            if not csv_data:
                self.logger.warning("No data found in the spreadsheet")
                return []

            # Convert to list of dictionaries
            headers = [h.strip() for h in csv_data[0].strip().split(',')]
            blog_data = []

            for row in csv_data[1:]:
                if row.strip():  # Skip empty rows
                    values = [v.strip() for v in row.strip().split(',')]
                    if len(values) >= len(headers):
                        post_data = dict(zip(headers, values))
                        # Log the data we're getting for debugging
                        self.logger.info(f"Processing post data: {post_data}")
                        blog_data.append(post_data)
                    else:
                        # Pad the row with empty strings if it's shorter than headers
                        padded_values = values + [''] * (len(headers) - len(values))
                        post_data = dict(zip(headers, padded_values))
                        self.logger.info(f"Processing padded post data: {post_data}")
                        blog_data.append(post_data)

            return blog_data
        except Exception as e:
            self.logger.error(f"Error fetching blog data: {str(e)}")
            raise

    def update_status(self, row_index, status):
        """This is a placeholder since we can't update public sheets without authentication"""
        self.logger.warning(f"Cannot update status in public sheet without authentication. Sheet ID: {self.spreadsheet_id}")
        # These parameters are intentionally unused as this is a placeholder method
        _ = row_index, status
        return False