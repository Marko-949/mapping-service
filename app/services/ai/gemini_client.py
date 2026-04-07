import google.generativeai as genai
import logging
from app.core.config import settings
import json
import re
logger = logging.getLogger(__name__)    

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in settings. Please set the GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Gemini model returned an empty response.")
                return None

            match = re.search(r'\[\s*\{.*\}\s*\]', response.text, re.DOTALL)
            if match:
                raw_json = match.group(0)
            else:
                raw_json = response.text.replace('```json', '').replace('```', '').strip()

            mapped_data = json.loads(raw_json)
            return mapped_data

        except json.JSONDecodeError as e:
            logger.error(f"AI model did not return valid JSON: {str(e)} | Response: {response.text[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Error occurred while mapping with AI model: {str(e)}")
            return None          

gemini_client = GeminiClient()