from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
import uuid

#create bp
cart_bp = Blueprint("cart", __name__)

# mongo will be passed from the main
db = None

def init_db(mongo_db):
    global db
    db = mongo_db

# Helper funtions to crate or pick up cart 
def get_or_create_cart():
    cart_id = session.get("card_id")
    
    # if no cart create new one 
    if not cart_id:
        cart_id = str(uuid())
        session["cart_id"] = cart_id
        db.carts.insert_one({
            "cart_id": cart_id,
            "user_id": session.get("user_id"),
            "items": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
    # get cart from db
    cart = db.carts.find_one({"cart_id": cart_id})
    
    # if cart doesnt exist in database (might have been cleared), create a new one 
    if not cart:
        db.carts.insert_one({
            "cart_id": cart_id,
            "user_id": session.get("user_id"),
            "items": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        cart = db.carts.find_one({"cart_id": cart_id})
        
    return cart

@cart_bp.route("/cart")
def view_cart():
    """View cart conetnts"""
    cart = get_or_create_cart()
    
    # get product details for each items in cart
    cart_items = []
    total = 0
    
    for item in cart.get('items', []):
        product = db.products.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            store = db.users.find_one(
                {"_id": ObjectId(product["user_id"])},
                {"store.name": 1, "store.slug": 1}
            )
            
            
            # calculate item total
            item_total = product["price"] * item["quantity"]
            total += item_total
            
            cart_items.append({
                "product": product,
                "store": store["store"] if store else {},
                "qauntity": item["quantity"],
                "item_total": item_total
            })
            
    return render_template(
        "cart/view_cart.html",
        cart_items=cart_items,
        total=total,
        now=datetime.now()
    )
    
@cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Add item to cart"""
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    
    if not product_id:
        flash("Product not found", "danger")
        return redirect(request.referrer or url_for("marketplace.home"))
    
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found", "danger")
        return redirect(request.referrer or url_for("marketplace.home"))
    
    if product["stock"] < quantity:
        flash(f"Sorry, only {product["stock"]} items available", "warning")
        return redirect(request.referrer or url_for("marketplace.home"))
    
    # Get or create cart
    cart = get_or_create_cart()
    
    # check is product is in cart
    items_exists = False
    for item in cart.get("items", []):
        if item["product_id"] == product_id:
            # Update quantity
            new_quantity = item["quantity"] + quantity
            if new_quantity > product["stock"]:
                flash(f"Sorry, only {product["stock"]} items available", "warning")
                return redirect(request.referrer or url_for("marketplace.home"))
            
            db.carts.update_one(
                {"cart_id": cart["cart_id"], "items.product_id":
                    product_id},
                {"$set": {"items.$.quantity": new_quantity}}
            )
            items_exists = True
            break
    
    # if product is not in cart, add it 
    if not items_exists:
        db.carts.update_one(
            {"cart_id": cart["cart_id"]},
            {
                "$push": {"items": {"product_id": product_id,
                "quantity": quantity}},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
    flash(f"Added {quantity} {product["name"]} ot your cart", "success")
    return redirect(request.referrer or url_for("cart.view_cart"))

@cart_bp.route("/cart/update", methods=["POST"])
def update_cart():
    """Update cart quantities"""
    product_id = request.form.get("product_id")
    qauntity = int(request.form.get("quantity", 1))
    
    if not product_id:  
        flash("Product not fount", "damger")
        return redirect(url_for("cart.view_cart"))
    
    # check if product exist and is in stock
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("cart.view_cart"))
    
    if qauntity <= 0:
        # remove item from cart
        db.carts.update_one(
            {"cart_id": session.get("cart_id")},
            {
                "$pull": {"items": {"product_id": product_id}},
                "$set": {"updated_at": datetime.now()}
            }
        )
        flash("item removed from cart", "ifo")
    else:
        # Check stock
        if product["stock"] < quantity:
            flash(f"Sorry, only {product["stock"]} items available", "warning")
            quantity = product["stock"]
            
        
        # Update quantity
        db.carts.upate_one(
            {"cart_id": session.get("cart_id"), "items.product_id": product_id},
            {"$set": {"items.$.quantity": quantity, "updated_at": datetime.now()}}
        )
        flash("Cart updated", "success")
        
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/cart/remove/<product_id>")
def remove_from_cart(product_id):
    """remove item from cart"""
    if not product_id:
        flash("Product not found", "danger")
        return redirect(url_for("cart.view_cart"))
    
    # remove item from cart
    db.carts.update_one(
        {"cart_id": session.get("cart_id")},
        {
            "$pull": {"items": {"product_id": product_id}},
            "$set": {"updated_at": datetime.now()}
        }
    )
    flash("Item removed from cart", "info")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/cart/clear")
def clear_cart():
    """Clear all items from cart"""
    db.carts.update_one(
        {"cart_id": session.get("cart_id")},
        {
            "$set": {
                "items": [],
                "updated_at": datetime.now()
            }
        }
    )
    
    flash("Cart cleared", "info")
    return redirect(url_for("cart.view_cart"))

# API endpoint to get cart count for header
@cart_bp.route("/api/cart.count")
def cart_count():
    """Get number of items in cart"""
    cart = get_or_create_cart()
    count = sum(item["quantity"] for item in cart.get("items", []))
    return jsonify({"count": count})