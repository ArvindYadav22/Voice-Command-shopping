import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
CART_FILE = PROJECT_ROOT / "carts.json"


if not CART_FILE.exists():
    with open(CART_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def _read_cart():
    with open(CART_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            
            with open(CART_FILE, "w", encoding="utf-8") as wf:
                json.dump([], wf)
            return []

def _write_cart(cart_data):
    with open(CART_FILE, "w", encoding="utf-8") as f:
        json.dump(cart_data, f, indent=2)

def add_to_cart(item: dict):
    cart = _read_cart()
    cart.append(item)
    _write_cart(cart)

def remove_from_cart(name: str) -> bool:
    cart = _read_cart()
    initial_len = len(cart)
    cart = [i for i in cart if i.get("name", "").lower() != name.lower()]
    _write_cart(cart)
    return len(cart) < initial_len

def get_cart():
    return _read_cart()

def clear_cart():
    _write_cart([])
