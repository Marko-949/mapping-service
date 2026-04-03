import os
import json
import logging
from app.services.ai.mapping_categories import category_mapper
from app.services.excel_service.excel_service import save_final_mapping
from app.utils.data_preparation.categories_formatter import get_formatted_categories
from app.core.config import settings

logger = logging.getLogger(__name__)

class CategoryMappingWorkflow:
    def run(self, input_json_path, shop_name, provider):
        
        try:
            if not os.path.exists(input_json_path):
                logger.error(f"Ulazni fajl nije pronađen: {input_json_path}")
                return None

            with open(input_json_path, 'r', encoding='utf-8') as f:
                categories_to_map = json.load(f)

            if not categories_to_map:
                logger.error(f"[{shop_name}] JSON fajl je prazan.")
                return None

            mungos_db_path = settings.DATA_DIR / "categories" / "allCategoriesCode.txt"
            if not os.path.exists(mungos_db_path):
                logger.error(f"Mungos baza nije pronađena na: {mungos_db_path}")
                return None

            with open(mungos_db_path, 'r', encoding='utf-8') as f:
                internal_list = [line.strip() for line in f if line.strip()]

            batch_size = 50
            master_results = []
            total_items = len(categories_to_map)
            
            for i in range(0, total_items, batch_size):
                batch = categories_to_map[i : i + batch_size]
                current_batch_num = (i // batch_size) + 1
                total_batches = (total_items + batch_size - 1) // batch_size
                
                logger.info(f"[{shop_name}] Batch {current_batch_num}/{total_batches} šaljem na AI...")

                batch_mapped_results = category_mapper.get_mapped_categories(
                    external_categories=batch,
                    internal_categories=internal_list
                )

                if batch_mapped_results:
                    master_results.extend(batch_mapped_results)
                else:
                    logger.warning(f"[{shop_name}] Batch {current_batch_num} nije vratio rezultate.")

            if not master_results:
                logger.error(f"[{shop_name}] AI nije vratio rezultate mapiranja.")
                return None

            provider_folder = provider.lower()
            
            output_dir = settings.DATA_DIR / "mapped_categories" / provider_folder
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_filename = f"{shop_name}_category_mapping.xlsx"
            output_path = output_dir / output_filename

            final_path = save_final_mapping(master_results, str(output_path))

            logger.info(f"[{shop_name}] Mapiranje završeno. Excel sačuvan: {final_path}")
            return final_path

        except Exception as e:
            logger.error(f"Kritična greška u CategoryMappingWorkflow za {shop_name}: {str(e)}")
            raise e
