import logging
logger = logging.getLogger(__name__)

def format_standard(raw_data):
        all_paths = []

        def walk(node, current_path=""):
            name = node.get("name", "").strip()
            
            new_path = f"{current_path};{name}" if current_path else name
            
            children = node.get("children", [])
            
            if not children:
                all_paths.append(new_path)
            else:
                for child in children:
                    walk(child, new_path)

        for root_node in raw_data:
            walk(root_node)

        return sorted(list(set(all_paths)))

# def format_woo(data: list) -> list:
#     formatted = []
#     for item in data:
#         cat = item.get('category', '')
#         # Ako je lista (ono što smo pričali ranije), spoji ih ili uzmi glavnu
#         if isinstance(cat, list):
#             formatted.append(" / ".join(cat))
#         else:
#             formatted.append(str(cat))
#     return list(set(formatted)) # unique vrijednosti

# def format_raw_list(data: list) -> list:
#     return [str(item).strip() for item in data if item]

# def format_shopify_style(data: list) -> list:
#     return [item.get('title', '') for item in data if item.get('title')]

FORMATTERS = {
    "standard": format_standard,
    # "woo_cache": format_woo_cache,
    # "raw_list": format_raw_list,
    # "shopify": format_shopify_style,
}

def get_formatted_categories(raw_data: list, source_type: str) -> list:
    formatter_func = FORMATTERS.get(source_type, FORMATTERS["standard"])
    logger.info(f"Using formatter {formatter_func.__name__} for source_type: {source_type}")
    return formatter_func(raw_data)