import logging
from app.services.ai.gemini_client import gemini_client
from app.services.ai.prompts.promprts_templates import CATEGORY_MAPPING_PROMPT

logger = logging.getLogger(__name__)

class CategoryMapper:
    def get_mapped_categories(self, external_categories: list, internal_categories: list):
        try:
            prompt = CATEGORY_MAPPING_PROMPT.format(
                external_categories=external_categories,
                internal_categories=internal_categories
            )
            return gemini_client.generate(prompt)
        except Exception as e:
            logger.error(f"Error in CategoryMapper: {e}")
            return None

category_mapper = CategoryMapper()