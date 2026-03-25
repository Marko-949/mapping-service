import re
import logging

logger = logging.getLogger(__name__)

def get_specific_category(woo_attributes, category_path):
    """
    Pronaći će ispravnu leaf kategoriju iz pročišćenog woo_attributes JSON-a,
    analizirajući 'haotične' stringove iz Excela (npr. "Kompjuteri; Laptopi, Gaming").
    """
    if not category_path or not woo_attributes:
        return None

    # Razbijanje stringa na delove (razdvajamo po ; ili , ili |)
    parts = re.split(r'[;,|]', str(category_path))
    search_terms = [p.strip() for p in parts if p.strip()]

    # Pravimo brzu mapu dostupnih kategorija iz Woo podataka 
    available_woo_cats = {}
    
    for item in woo_attributes:
        woo_cat = item.get("category")
        
        if isinstance(woo_cat, list):
            for c in woo_cat:
                available_woo_cats[str(c).lower().strip()] = item.get("attributes", [])
        else:
            available_woo_cats[str(woo_cat).lower().strip()] = item.get("attributes", [])

    # Prolazimo kroz pojmove iz Excela i tražimo podudaranje u mapi
    for term in search_terms:
        term_lower = term.lower().strip()
        
        if term_lower in available_woo_cats:
            logger.info(f"Pronađena leaf kategorija u Woo podacima: '{term}'")
            return available_woo_cats[term_lower]

    logger.warning(f"Nijedan od pojmova {search_terms} nije pronađen kao leaf kategorija u keširanim Woo podacima.")
    return None