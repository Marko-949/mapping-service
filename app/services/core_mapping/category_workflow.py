import os
import json
import logging
from app.services.ai.mapping_categories import category_mapper
from app.services.excel_service.excel_service import save_final_mapping
from app.utils.data_preparation.categories_formatter import get_formatted_categories
from app.core.config import settings

logger = logging.getLogger(__name__)

class CategoryMappingWorkflow:
    def run(self, input_json_path, shop_name, source_type="standard"):
        logger.info(f"[{shop_name}] Započinjem workflow mapiranja kategorija. Source: {source_type}")
        try:
            # 1. Provjera i učitavanje ulaznog fajla
            if not os.path.exists(input_json_path):
                logger.error(f"Ulazni fajl nije pronađen: {input_json_path}")
                return None

            with open(input_json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # 2. Standardizacija na osnovu source_type-a (koristi tvoj novi formatter)
            cleaned_categories = get_formatted_categories(raw_data, source_type)

            if not cleaned_categories:
                logger.error(f"[{shop_name}] Nema validnih kategorija nakon formatiranja.")
                return None

            # 3. Učitavanje Internih (Mungos) kategorija
            mungos_db_path = settings.DATA_DIR / "categories" / "allCategoriesCode.txt"
            if not os.path.exists(mungos_db_path):
                logger.error(f"Mungos baza nije pronađena na: {mungos_db_path}")
                return None

            with open(mungos_db_path, 'r', encoding='utf-8') as f:
                internal_list = [line.strip() for line in f if line.strip()]

            if not internal_list:
                logger.error(f"Fajl {mungos_db_path} je prazan!")
                return None

            logger.info(f"Učitano {len(internal_list)} internih kategorija iz .txt fajla.")

            # 4. BATCH OBRADA 
            batch_size = 50
            master_results = []
            total_items = len(cleaned_categories)
            
            logger.info(f"[{shop_name}] Ukupno kategorija za obradu: {total_items}. Batch size: {batch_size}")

            for i in range(0, total_items, batch_size):
                batch = cleaned_categories[i : i + batch_size]
                current_batch_num = (i // batch_size) + 1
                total_batches = (total_items + batch_size - 1) // batch_size
                
                logger.info(f"[{shop_name}] Šaljem batch {current_batch_num}/{total_batches} Geminiju...")

                # Pozivamo AI mapper 
                batch_mapped_results = category_mapper.get_mapped_categories(
                    external_categories=batch,
                    internal_categories=internal_list
                )

                if batch_mapped_results:
                    master_results.extend(batch_mapped_results)
                    logger.info(f"[{shop_name}] Primljeno {len(batch_mapped_results)} rezultata iz batch-a {current_batch_num}.")
                else:
                    logger.error(f"[{shop_name}] Batch {current_batch_num} nije vratio rezultate!")

            # 5. Provjera rezultata i generisanje Excela
            if not master_results:
                logger.error(f"[{shop_name}] Nijedan batch nije vratio rezultate. Prekidam.")
                return None

            # Definisanje izlazne putanje
            output_filename = f"{shop_name}_category_mapping.xlsx"
            output_dir = os.path.join(settings.DATA_DIR, "mapped_categories")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)

            # Čuvanje finalnog Excela
            final_path = save_final_mapping(master_results, output_path)

            # BRISANJE ULAZNOG FAJLA (Cleanup kao u starom servisu)
            if os.path.exists(input_json_path):
                os.remove(input_json_path)
                logger.info(f"[{shop_name}] Obrisan privremeni ulazni fajl.")

            logger.info(f"[{shop_name}] Workflow uspješno završen. Fajl: {final_path}")
            return final_path

        except Exception as e:
            logger.error(f"Greška u CategoryMappingWorkflow: {str(e)}")
            raise e