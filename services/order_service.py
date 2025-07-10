from bson.objectid import ObjectId
from datetime import datetime, timezone
import uuid

def build_cart_items(db , cart):
    cart_items = []
    total = 0 
    
    for item in cart.get("items", []):
        product = db.product.find_one({"_id": ObjectId(item["prodcut_id"])})
        if not product:
            continue
        
        store = db.users.find_one(
            {"_id": ObjectId(product["user_id"])},
            {"store.name": 1, "store.slug": 1}
        )
        
        item_total = product["price"] * item["quantity"]
        total += item_total
        
        cart_items.append({
            "product": product,
            "store": store["store"] if store else {},
            "quantity": item["qunatity"],
            "item_total": item_total
        })
    
    return cart_items, total

def create_orders_from_cart(db, session, cart_items, customer_info):
    order_ids = {}
    grouped = {}
    
    for item in cart_items:
        store_id = str(item["product"]["_id"])
        if store_id not in grouped:
            grouped[store_id] = {
                "items": [],
                "total": 0,
                "store": item["store"]
            }
        
        grouped[store_id]["items"].append({
            "product_id": str(item["product"]["_id"]),
            "quanity": item["quantity"],
            "item_total": item["item_total"],
            "price": item["product"]["price"],
            "name": item["product"]["name"]
        })
        grouped[store_id]["total"] += item["item_total"]
        
    for store_id, data in grouped.items():
        order_id = str(uuid.uuid4())
        db.client_orders.insert_one({
            "order_id": order_id,
            "user_id": session.get("user_id"),
            "store_id": store_id,
            "store_name": data["store"].get("name", "UnkownStore"),
            "customer": customer_info,
            "items": data["items"],
            "total": data["total"],
            "status": "pending",
            "status_next": "pending",
            "status_history": [
                {"status": "pending","date": datetime.now(timezone.utc), "note": "Order placed"}
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        order_ids[store_id] = order_id
    
    return list(order_ids.values())