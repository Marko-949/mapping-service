import json
import logging
import os

logger = logging.getLogger(__name__)

def get_category_uuid(json_file_path: str, target_code: str):
    """
    Pronađe UUID u lokalnom JSON fajlu na osnovu code-a.
    Prilagođeno za rad unutar asinhronih taskova.
    """
    if not os.path.exists(json_file_path):
        logger.error(f"Fajl sa UUID bazom nije pronađen na putanji: {json_file_path}")
        return None

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Pretvaramo target_code u string i čistimo razmake (za svaki slučaj)
            target_code = str(target_code).strip()

            for item in data:
                if str(item.get("code")).strip() == target_code:
                    return item.get("uuid")
                    
            logger.warning(f"UUID nije pronađen u bazi za kod: {target_code}")
            
    except json.JSONDecodeError:
        logger.error(f"Greška: Fajl {json_file_path} nije validan JSON.")
    except Exception as e:
        logger.error(f"Neočekivana greška pri čitanju UUID baze: {e}")
        
    return None