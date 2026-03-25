import json
import logging
from app.services.ai.gemini_client import gemini_client
from app.services.ai.prompts.promprts_templates import ATTRIBUTE_MAPPING_PROMPT

logger = logging.getLogger(__name__)

class AttributeMapper:
    def get_mapped_data_as_json(self, specific_category_attributes, mungos_attributes):
        """
        Priprema prompt i poziva GeminiClient.
        """
        try:
            # Priprema podataka za prompt
            external_data_str = json.dumps(specific_category_attributes, ensure_ascii=False)
            internal_data_str = json.dumps(mungos_attributes, ensure_ascii=False)

            prompt = ATTRIBUTE_MAPPING_PROMPT.format(
                external_data=external_data_str,
                internal_data=internal_data_str
            )

            result = gemini_client.generate(prompt)
            
            return result

        except Exception as e:
            logger.error(f"Greška u AttributeMapper-u: {str(e)}")
            return None

attribute_mapper = AttributeMapper()