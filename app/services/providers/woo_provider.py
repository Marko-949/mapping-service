# app/services/providers/woo_provider.py

import requests
import json
import os
import logging
from requests.auth import HTTPBasicAuth
from app.core.config import settings
from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

class WooCommerceProvider(BaseProvider):
    def __init__(self, base_url, ck, cs):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wc/v3"
        self.auth = HTTPBasicAuth(ck, cs)
        self.shop_domain = self.base_url.split("//")[-1].split("/")[0].replace(".", "_")
        self.cache_path = os.path.join(settings.BASE_DIR, "data", "cachedShops", f"{self.shop_domain}_cache.json")
        
    def _get_leaf_categories_map(self):
        cat_url = f"{self.api_url}/products/categories"
        all_categories = []
        page = 1

        while True:
            try:
                res = requests.get(cat_url, params={"page": page, "per_page": 100}, auth=self.auth, timeout=60)
                data = res.json()
                if not data or res.status_code != 200:
                    break
                all_categories.extend(data)
                page += 1
            except Exception as e:
                logger.error(f"Greška pri dohvatanju kategorija: {e}")
                break

        # Pronađi sve ID-jeve koji su parent nekome
        parent_ids = {cat['parent'] for cat in all_categories if cat.get('parent') != 0}
        
        # Leaf su one čiji ID nije u parent_ids setu
        leaf_map = {cat['id']: cat['name'] for cat in all_categories if cat['id'] not in parent_ids}
        
        return leaf_map

    def _fetch_from_api(self):
        """Direktno dohvatanje sa Woo API-ja i procesiranje"""
        products_url = f"{self.api_url}/products"
        
        leaf_categories_map = self._get_leaf_categories_map()
        category_map = {}
        page = 1

        while True:
            params = {"page": page, "per_page": 100}
            try:
                response = requests.get(
                    products_url, 
                    params=params, 
                    auth=self.auth, 
                    timeout=60
                )
                
                if response.status_code != 200:
                    logger.error(f"Greška na stranici {page}: Status {response.status_code}")
                    break
                    
                products = response.json()

                if not products:
                    break

                logger.info(f"Obrađujem stranicu {page} za shop {self.shop_domain}...")

                for product in products:
                    product_cats = product.get("categories", [])
                    # Izvlačenje imena leaf kategorija iz mape 
                    leaf_names = [leaf_categories_map[c['id']] for c in product_cats if c['id'] in leaf_categories_map]
                    
                    if not leaf_names:
                        continue

                    # Pravimo ključ (npr. "Laptopi" ili "Televizori")
                    cat_key = tuple(sorted(leaf_names))

                    if cat_key not in category_map:
                        category_map[cat_key] = []

                    for attr in product.get("attributes", []):
                        attr_name = attr.get("name")
                        # Preskačemo EAN ili prazne atribute
                        if not attr_name or attr_name.lower() == "ean":
                            continue

                        options = attr.get("options", [])
                        
                        # Provjeravamo da li već imamo ovaj atribut u ovoj kategoriji
                        existing_attr = next((a for a in category_map[cat_key] if a["name"] == attr_name), None)
                        
                        if existing_attr:
                            for opt in options:
                                if opt not in existing_attr["options"]:
                                    existing_attr["options"].append(opt)
                        else:
                            category_map[cat_key].append({
                                "name": attr_name,
                                "options": options
                            })
                
                page += 1 

            except Exception as e:
                logger.error(f"Kritična greška tokom preuzimanja proizvoda na str {page}: {e}")
                break

        # 3. Finalizacija - pretvaranje mape u listu
        final_result = []
        for cat_tuple, attrs in category_map.items():
            cat_display = cat_tuple[0] if len(cat_tuple) == 1 else list(cat_tuple)
            final_result.append({
                "category": cat_display,
                "attributes": attrs
            })

        logger.info(f"Ukupno obrađeno {len(final_result)} jedinstvenih kategorija.")
        return final_result

    def get_shop_structure(self, force_refresh: bool = False):
        """Glavna metoda koja brine o keširanju"""
        # Provjera Cache-a
        if not force_refresh and os.path.exists(self.cache_path):
            logger.info(f"Učitavam cache za: {self.shop_domain}")
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Dohvatanje novih podataka
        data = self._fetch_from_api()

        # Čuvanje u Cache
        if data:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data