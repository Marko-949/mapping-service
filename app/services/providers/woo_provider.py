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
        self.cache_path = os.path.join(settings.BASE_DIR, "data", "cachedAttributesOptions", f"{self.shop_domain}_cache.json")
        
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
                logger.error(f"Error fetching categories: {e}")
                break

        parent_ids = {cat['parent'] for cat in all_categories if cat.get('parent') != 0}
        leaf_map = {cat['id']: cat['name'] for cat in all_categories if cat['id'] not in parent_ids}
        
        return leaf_map

    def _fetch_from_api(self):
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
                    logger.error(f"Error on page {page}: Status {response.status_code}")
                    break
                    
                products = response.json()

                if not products:
                    break

                logger.info(f"Processing page {page} for shop {self.shop_domain}...")

                for product in products:
                    product_cats = product.get("categories", [])
                    leaf_names = [leaf_categories_map[c['id']] for c in product_cats if c['id'] in leaf_categories_map]
                    
                    if not leaf_names:
                        continue

                    cat_key = tuple(sorted(leaf_names))

                    if cat_key not in category_map:
                        category_map[cat_key] = []

                    for attr in product.get("attributes", []):
                        attr_name = attr.get("name")
                        if not attr_name or attr_name.lower() == "ean":
                            continue

                        options = attr.get("options", [])
                        
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
                logger.error(f"Critical error while fetching products on page {page}: {e}")
                break

        final_result = []
        for cat_tuple, attrs in category_map.items():
            cat_display = cat_tuple[0] if len(cat_tuple) == 1 else list(cat_tuple)
            final_result.append({
                "category": cat_display,
                "attributes": attrs
            })

        logger.info(f"Total processed {len(final_result)} unique categories.")
        return final_result

    def get_shop_structure(self, force_refresh: bool = False):
        if not force_refresh and os.path.exists(self.cache_path):
            logger.info(f"Loading cache for: {self.shop_domain}")
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        data = self._fetch_from_api()

        if data:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data
    
    def get_categories(self) -> list:

        logger.info(f"Fetching all categories for shop: {self.shop_domain}")
        
        url = f"{self.api_url}/products/categories"
        all_categories = []
        page = 1

        while True:
            res = requests.get(url, params={"page": page, "per_page": 100}, auth=self.auth, timeout=60)
            data = res.json()
            if not data or res.status_code != 200:
                break
            all_categories.extend(data)
            page += 1

        if not all_categories:
            return []

        cat_map = {c['id']: {"name": c['name'], "parent": c['parent']} for c in all_categories}

        def get_full_path(cat_id):
            cat = cat_map.get(cat_id)
            if not cat:
                return ""
            
            if cat['parent'] == 0:
                return cat['name']
            
            parent_path = get_full_path(cat['parent'])
            return f"{parent_path};{cat['name']}"

        full_paths = [get_full_path(c['id']) for c in all_categories]

        final_list = sorted(list(set(full_paths)))
        
        logger.info(f"Generated {len(final_list)} category paths.")
        return final_list