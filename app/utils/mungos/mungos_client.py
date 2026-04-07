import requests
import logging
from app.core.config import settings
logger = logging.getLogger(__name__)

def get_mungos_attributes(category_id, token):
    url = f"{settings.MUNGOS_API_URL}/reference_data/attributes_for_category?categoryUuid={category_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            simplified_data = []

            for item in data:
                simplified_item = {
                    "code": item.get("code"),
                    "optionsForMultioptionAttribute": []
                }

                options = item.get("optionsForMultioptionAttribute") or []
                for opt in options:
                    opt_code = opt.get("code")
                    if opt_code:
                        simplified_item["optionsForMultioptionAttribute"].append({
                            "code": opt_code
                        })

                simplified_data.append(simplified_item)
            
            return simplified_data
            
        elif response.status_code == 401:
            logger.error(f"Unauthorized access to Mungos API. Check your token.")
            return None
        elif response.status_code == 404:
            logger.warning(f"Mungos API: Category {category_id} not found (404).")
            return None
        else:
            logger.error(f"Error on request (Mungos): {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"Mungos API: Request timed out (30s).")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Mungos module: {str(e)}")
        return None