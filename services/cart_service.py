from datetime import datetime
from bson.objectid import ObjectId
import uuid


def generate_cart_id():
    return str(uuid.uuid4())

def get_or_create_cart(db, session):
    cart_id = session.get("cart_id")
    
    if not cart_id:
        cart_id = generate_cart_id()
        session["cart_id"] = cart_id
        db.carts.insert_one({
            "cart_id": cart_id,
            "user_id": session,
            "items": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        
    cart = db.carts.find_one({"cart_id": cart_id})
    if not cart:
        db.carts.insert_one({
            "carts_id": cart_id,
            "user_id": session.get("user_id"),
            "items": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        cart = db.carts.find_one({"cart_id": cart_id})
    
    return cart

def calculate_cart_items(db, cart):
    cart_items = []
    total = 0
    
    for item in cart.get('items', []):
        product = db.products.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            store = db.users.find_one(
                {"_id": ObjectId(product["user_id"])},
                {
                    "store.name":1,
                    "store.slug": 1
                }
            )
            item_total = product["price"] * item["quantity"]
            total += item_total
            
            cart_items.append({
                "product": product,
                "store": store["store"] if store else {},
                "quantity": item["quantity"],
                "item_total": item_total
            })
            
        return cart_items, total