import logging
from google.cloud import firestore
from google.api_core import exceptions

logger = logging.getLogger(__name__)

# Hardcoded GCP Project ID per requirement
FIRESTORE_PROJECT = "qwiklabs-gcp-03-4796b5681dc3"
COLLECTION_NAME = "greenhouse_inventory"

# Seed data for in-memory fallback and database seeding
INITIAL_SEED_ITEMS = {
    "monstera_deliciosa": {
        "id": "monstera_deliciosa",
        "name": "Monstera Deliciosa",
        "category": "Tropical",
        "quantity": 12,
        "price": 29.99,
        "care_notes": "Bright indirect light, water when top 2 inches of soil dry out.",
        "in_stock": True
    },
    "fiddle_leaf_fig": {
        "id": "fiddle_leaf_fig",
        "name": "Fiddle Leaf Fig",
        "category": "Ficus",
        "quantity": 5,
        "price": 45.00,
        "care_notes": "Needs consistent bright light, sensitive to overwatering.",
        "in_stock": True
    },
    "snake_plant": {
        "id": "snake_plant",
        "name": "Snake Plant (Sansevieria)",
        "category": "Succulent",
        "quantity": 25,
        "price": 18.50,
        "care_notes": "Tolerates low light, water sparingly every 3-4 weeks.",
        "in_stock": True
    },
    "peace_lily": {
        "id": "peace_lily",
        "name": "Peace Lily",
        "category": "Flowering",
        "quantity": 8,
        "price": 22.00,
        "care_notes": "Medium to low light, keep soil moist, droops when thirsty.",
        "in_stock": True
    }
}

_memory_store = dict(INITIAL_SEED_ITEMS)

def get_db_client():
    """Initializes Firestore client with hardcoded project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT)

def list_inventory(category_filter: str = "") -> list[dict]:
    """Retrieves items from Firestore or local fallback store."""
    try:
        db = get_db_client()
        docs = db.collection(COLLECTION_NAME).stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            if category_filter:
                if category_filter.lower() in data.get("category", "").lower():
                    items.append(data)
            else:
                items.append(data)
        if items:
            return items
    except Exception as e:
        logger.warning(f"Firestore query failed ({e}). Using in-memory inventory store.")

    items = list(_memory_store.values())
    if category_filter:
        items = [i for i in items if category_filter.lower() in i.get("category", "").lower()]
    return items

def get_item(item_id: str) -> dict | None:
    """Gets a specific item by ID."""
    try:
        db = get_db_client()
        doc = db.collection(COLLECTION_NAME).document(item_id).get()
        if doc.exists:
            return doc.to_dict()
    except Exception as e:
        logger.warning(f"Firestore get failed ({e}). Using in-memory store.")

    return _memory_store.get(item_id)

def update_inventory_quantity(item_id: str, new_quantity: int) -> dict:
    """Updates the quantity of an item."""
    # Normalize ID: handle case where name is passed instead of exact ID
    normalized_id = item_id.lower().replace(" ", "_")
    target_id = item_id if item_id in _memory_store else (normalized_id if normalized_id in _memory_store else item_id)
    
    # Try finding by name if ID still doesn't match
    if target_id not in _memory_store:
        for k, v in _memory_store.items():
            if item_id.lower() in v.get("name", "").lower():
                target_id = k
                break

    updated_item = None
    try:
        db = get_db_client()
        doc_ref = db.collection(COLLECTION_NAME).document(target_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update({"quantity": new_quantity, "in_stock": new_quantity > 0})
            updated_item = doc_ref.get().to_dict()
    except Exception as e:
        logger.warning(f"Firestore update failed ({e}). Updating in-memory store.")

    if target_id in _memory_store:
        _memory_store[target_id]["quantity"] = new_quantity
        _memory_store[target_id]["in_stock"] = new_quantity > 0
        if not updated_item:
            updated_item = _memory_store[target_id]

    if not updated_item:
        return {"error": f"Item ID or name '{item_id}' not found."}
    return updated_item

def add_inventory_item(item_id: str, name: str, category: str, quantity: int, price: float, care_notes: str) -> dict:
    """Adds a new item to the inventory."""
    item = {
        "id": item_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "price": price,
        "care_notes": care_notes,
        "in_stock": quantity > 0
    }
    try:
        db = get_db_client()
        db.collection(COLLECTION_NAME).document(item_id).set(item)
    except Exception as e:
        logger.warning(f"Firestore set failed ({e}). Writing to in-memory store.")

    _memory_store[item_id] = item
    return item
