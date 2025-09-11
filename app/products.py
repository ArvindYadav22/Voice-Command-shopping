import json
from pathlib import Path


PRODUCTS_FILE = Path(__file__).parent.parent / "products.json"

with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

def get_all_products():
    """
    Return all products grouped by category.
    """
    return PRODUCTS

def find_product_by_name(name: str):
    """
    Search for a product by exact name (case-insensitive).
    Returns the product dict if found, else None.
    """
    name = name.strip().lower()
    for category, items in PRODUCTS.items():
        for item in items:
            if item["name"].lower() == name:
                return item
    return None

def search_products_by_keyword(keyword: str):
    """
    Search for products containing the keyword in their name.
    Returns a list of matching product dicts.
    """
    keyword = keyword.strip().lower()
    matches = []
    for category, items in PRODUCTS.items():
        for item in items:
            if keyword in item["name"].lower():
                matches.append(item)
    return matches
