import logging
import json
import re
from app.services.ai.mapping_attributes import attribute_mapper
from app.services.excel_service.excel_service import read_input_plan, save_final_mapping
from app.utils.mungos.mungos_client import get_mungos_attributes
from app.utils.mungos.uuid_utils import get_category_uuid 
from app.core.config import settings
import os

logger = logging.getLogger(__name__)

class AttributeOptionWorkflow:
    def run(self, task_id, provider, input_json_path, input_excel_path, shop_name, token):
        try:
            logger.info(f"Starting workflow for Task: {task_id}")
            requested_categories = read_input_plan(input_excel_path)
            
            if not os.path.exists(input_json_path):
                raise FileNotFoundError(f"Cached JSON not found: {input_json_path}")
            
            with open(input_json_path, 'r', encoding='utf-8') as f:
                shop_data = json.load(f)

            all_mapped_results = []
            mungos_json_db = settings.DATA_DIR / "mappedUuidCode" / "allCategoriesUuidCode.json"

            for row in requested_categories:
                external_key = str(row.get('ExternalKey', '')).strip()
                internal_key = str(row.get('InternalKey', '')).strip()
                type_from = str(row.get('TypeFrom', '')).strip()

                category_entry = {
                    "TypeFrom": "Category",
                    "ExternalKey": external_key,
                    "TypeTo": "Category",
                    "InternalKey": internal_key,
                }
                
                if type_from != "Category":
                    all_mapped_results.append(category_entry)
                    continue
                logger.info(f"[{shop_name}] Processing category: {external_key} -> {internal_key}")

                category_id = get_category_uuid(mungos_json_db, internal_key)
                if not category_id:
                    all_mapped_results.append(category_entry)
                    logger.warning(f"UUID not found for category: {internal_key}. Skipping.")
                    continue
                    
                logger.info(f"Fetching Mungos attributes for category: {internal_key} (UUID: {category_id})")
                mungos_attributes = get_mungos_attributes(category_id, token)
                if mungos_attributes is None:
                    logger.warning(f"API for Mungos attributes returned None for category: {internal_key}")
                    all_mapped_results.append(category_entry)
                    continue
                logger.info(f"mungos attributes for {internal_key} (UUID: {category_id}): {len(mungos_attributes)} found.")
                
                if not mungos_attributes:
                    all_mapped_results.append(category_entry)
                    logger.warning(f"No Mungos attributes found for category: {internal_key}. Skipping AI mapping.")
                    continue

                specific_data = self._find_category_in_data(external_key, shop_data)
                
                if not specific_data:
                    all_mapped_results.append(category_entry)
                    logger.warning(f"Category {external_key} not found in shop.")
                    continue

                all_mapped_results.append(category_entry)

                logger.info(f"specific attributes for {external_key}: {len(specific_data.get('attributes', []))} found. Sending to AI mapping... mungos attributes: {mungos_attributes}")
                ai_response = attribute_mapper.get_mapped_data_as_json(
                    specific_category_attributes=specific_data['attributes'],
                    mungos_attributes=mungos_attributes
                )

                if ai_response:
                    for ai_row in ai_response:
                        ai_row['Category'] = external_key
                        if 'TypeFrom' not in ai_row: ai_row['TypeFrom'] = "CategoryAttribute"
                        if 'TypeTo' not in ai_row: ai_row['TypeTo'] = "CategoryAttribute"
                        all_mapped_results.append(ai_row)

            output_filename = f"{shop_name}_mapping.xlsx"
            output_path = os.path.join(settings.DATA_DIR, "mapped_attributes", output_filename)
            output_path = save_final_mapping(all_mapped_results, output_path)
            logger.info(f"Workflow completed successfully. File: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error in Workflow: {str(e)}")
            raise e

    def _find_category_in_data(self, category_name, shop_data):
        if not category_name or not shop_data:
            return None

        parts = re.split(r'[;,>]', str(category_name))
        leaf_from_excel = [p.strip() for p in parts if p.strip()][-1].lower()

        for item in shop_data:
            cat = item.get('category')
            
            if isinstance(cat, list) and cat:
                leaf_from_shop = str(cat[-1]).strip().lower()
                if leaf_from_shop == leaf_from_excel:
                    return item
            
            elif cat:
                leaf_from_shop = str(cat).strip().lower()
                if leaf_from_shop == leaf_from_excel:
                    return item
                    
        return None