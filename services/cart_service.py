from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
import uuid

CART_EXPIRY_DAYS = 7

def generate_cart_id():
    return str(uuid.uuid4())

def is_cart_expired(cart):
   return cart.get("expires_at") and cart["expires_at"] < datetime.now(timezone.utc)

def get_or_create_cart(db, session):
    user_id = session.get("user_id")
    cart = None
    
    if user_id:
        cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    else:
        cart_id = session.get("cart_id")
        if cart_id:
            cart = db.carts.find_one({"cart_id": cart_id})
            
    if cart and is_cart_expired(cart):
        db.carts.delete_one({"_id": cart["_id"]})
        cart = None
        
    if not cart:
        new_cart = {
            "cart_id": generate_cart_id(),
            "user_id": ObjectId(user_id) if user_id else None,
            "items": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=CART_EXPIRY_DAYS)
        }
        db.insert_one(new_cart)
        cart = new_cart
        if not user_id:
            session["cart_id"] = new_cart["cart_id"]
    
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
    
def merge_guest_cart_to_user_cart(db, session):
    guest_cart_id = session.get("cart_id")
    user_id = session.get("user_id")
    
    if not guest_cart_id or not user_id:
        return 
    
    guest_cart = db.carts.find_one({"cart_id": guest_cart_id})
    user_cart = db.carts.find_one({"user_id": ObjectId(user_id)})
    
    if not guest_cart:
        return
    
    if not user_cart:
        db.carts.update_one(
            {"cart_id": guest_cart_id},
            {
                "$set": {
                    "user_id": ObjectId(user_id),
                    "updated_at": datetime.now(timezone.utc),
                    "expires_at": datetime.now(timezone.utc) + timedelta(days=CART_EXPIRY_DAYS)
                }
            }
        )
        session.pop("cart_id", None)
        return
    
    for item in guest_cart.get("items", []):
        existing = next((i for i in user_cart["items"] if i["product_id"] == item["product_id"]), None)
        if existing:
            product = db.products.find_one({"_id": ObjectId(item["product_id"])})
            if product:
                new_qty = min(existing["quantity"] + item["quantity"], product["stock"])
                db.carts.update_one(
                    {"_id": user_cart["_id"], "items.product_id": item["product_id"]},
                    {"$set": {"items.$.quantity": new_qty}}
                )
            else:
                db.carts.update_one(
                    {"_id": user_cart["_id"]},
                    {"$push": {"items": item}}
                )
                
    db.carts.update_one({"_id": user_cart["_id"]}, {"$set": {"updated_at": datetime.utcnow()}})
    db.carts.delete_one({"_id": guest_cart["_id"]})
    session.pop("cart_id", None)