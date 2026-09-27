import os
from google.cloud import firestore

# Hardcode GCP Project ID as required
PROJECT_ID = "qwiklabs-gcp-03-4796b5681dc3"

def seed_database():
    print(f"Connecting to Firestore with hardcoded Project ID: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    
    collection_ref = db.collection("greenhouse_inventory")
    
    initial_items = [
        {
            "id": "monstera_deliciosa",
            "name": "Monstera Deliciosa",
            "category": "Tropical",
            "quantity": 12,
            "price": 29.99,
            "care_notes": "Bright indirect light, water when top 2 inches of soil dry out.",
            "in_stock": True
        },
        {
            "id": "fiddle_leaf_fig",
            "name": "Fiddle Leaf Fig",
            "category": "Ficus",
            "quantity": 5,
            "price": 45.00,
            "care_notes": "Needs consistent bright light, sensitive to overwatering and drafts.",
            "in_stock": True
        },
        {
            "id": "snake_plant",
            "name": "Snake Plant (Sansevieria)",
            "category": "Succulent",
            "quantity": 25,
            "price": 18.50,
            "care_notes": "Tolerates low light, water sparingly every 3-4 weeks.",
            "in_stock": True
        },
        {
            "id": "peace_lily",
            "name": "Peace Lily",
            "category": "Flowering",
            "quantity": 8,
            "price": 22.00,
            "care_notes": "Medium to low light, keep soil moist, droops when thirsty.",
            "in_stock": True
        }
    ]
    
    for item in initial_items:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded item: {item['name']} (ID: {doc_id})")
        
    print(f"Successfully seeded {len(initial_items)} items to 'greenhouse_inventory' collection in project {PROJECT_ID}.")

if __name__ == "__main__":
    seed_database()
