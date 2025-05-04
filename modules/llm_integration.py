import requests
import logging
from config.config import OLLAMA_URL, MODEL_NAME

class LLMIntegration:
    def __init__(self):
        self.setup_logging()
        self.base_url = OLLAMA_URL
        self.model_name = MODEL_NAME

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)

    def clean_text(self, text):
        """Clean and format text input"""
        if not text:
            return ""
        # Remove extra quotes and whitespace
        text = text.strip().strip('"\'')
        return text

    def generate_content(self, title, topic, keywords, context, word_count=1000):
        """Generate blog content using Gemma 3"""
        try:
            # Clean and format inputs
            title = self.clean_text(title)
            topic = self.clean_text(topic)
            keywords = self.clean_text(keywords)
            context = self.clean_text(context)

            # Calculate word count range
            word_count = int(word_count)  # Ensure word_count is an integer
            min_words = max(500, int(word_count * 0.8))
            max_words = int(word_count * 1.2)

            # Construct the prompt
            prompt = f"""You are a professional content writer specializing in electric vehicles. Write a detailed, informative blog post with the following specifications:

Title: {title}
Main Topic: {topic}
Keywords to include: {keywords}
Context: {context}

Requirements:
1. Write in a professional, engaging tone suitable for an electric vehicle industry website
2. Include an attention-grabbing introduction
3. Provide detailed analysis and insights about {topic}
4. Incorporate the specified keywords naturally throughout the content
5. Include relevant statistics or data points where applicable
6. End with a strong conclusion that summarizes key points
7. Ensure the content is well-structured with proper headings and paragraphs
8. Maintain a word count between {min_words}-{max_words} words

Format the response in markdown with appropriate headings, bullet points, and paragraphs."""

            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                },
                timeout=60  # Increased timeout for longer responses
            )
            response.raise_for_status()

            # Get the generated content
            content = response.json().get('response', '')
            if not content:
                raise ValueError("Empty response from Gemma")

            self.logger.info("Successfully generated content using Gemma")
            return content
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to Ollama. Please make sure Ollama is running and Gemma model is installed."
            self.logger.error(error_msg)
            # Return a fallback message instead of raising an exception
            return f"""# {title}

*Note: This content was generated as a fallback because Ollama could not be reached. Please ensure Ollama is running with the Gemma model installed.*

## About {topic}

This is a placeholder article about {topic}. The actual article would include information about:

- {keywords}
- {context}

Please start Ollama and try again to generate a complete article."""
        except requests.exceptions.Timeout:
            error_msg = "Request to Ollama timed out. Please try again."
            self.logger.error(error_msg)
            # Return a fallback message instead of raising an exception
            return f"""# {title}

*Note: This content was generated as a fallback because the request to Ollama timed out.*

## About {topic}

This is a placeholder article about {topic}. The actual article would include information about:

- {keywords}
- {context}

Please try again to generate a complete article."""
        except Exception as e:
            self.logger.error(f"Error generating content with Gemma: {str(e)}")
            # Return a fallback message instead of raising an exception
            return f"""# {title}

*Note: This content was generated as a fallback due to an error: {str(e)}*

## About {topic}

This is a placeholder article about {topic}. The actual article would include information about:

- {keywords}
- {context}

Please check the logs and try again to generate a complete article."""