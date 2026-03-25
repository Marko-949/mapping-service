import requests
import logging

logger = logging.getLogger(__name__)

def get_mungos_attributes(category_id, token):
    """
    Dohvata atribute sa Mungos API-ja za specifičnu kategoriju.
    Prilagođeno za rad unutar asinhronih taskova (FastAPI/Celery).
    """
    # Dinamički URL
    url = f"https://mungos.ba/api/v1/core/reference_data/attributes_for_category?categoryUuid={category_id}"
    
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
            logger.error(f"Mungos API: Token je nevažeći ili je istekao (401).")
            return None
        elif response.status_code == 404:
            logger.warning(f"Mungos API: Kategorija {category_id} nije pronađena (404).")
            return None
        else:
            logger.error(f"Greška pri zahtjevu (Mungos): {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"Mungos API: Zahtjev je prekinut zbog timeout-a (30s).")
        return None
    except Exception as e:
        logger.error(f"Neočekivana greška u Mungos modulu: {str(e)}")
        return None