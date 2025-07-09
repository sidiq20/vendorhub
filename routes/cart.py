from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime, timezone
from services.cart_service import get_or_create_cart, calculate_cart_items

#create bp
cart_bp = Blueprint("cart", __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db


@cart_bp.route("/cart")
def view_cart():
    cart = get_or_create_cart(db, session)
    cart_items, total = calculate_cart_items(db, cart)
    
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
    
    cart = get_or_create_cart(db, session)
    
    # check is product is in cart
    for item in cart.get("items", []):
        if item["product_id"] == product_id:
            # Update quantity
            new_quantity = item["quantity"] + quantity
            if new_quantity > product["stock"]:
                flash(f"Sorry, only {product["stock"]} items available", "warning")
                return redirect(request.referrer or url_for("marketplace.home"))
            
            db.carts.update_one(
                {"cart_id": cart["cart_id"], "items.product_id": product_id},
                {"$set": {"items.$.quantity": new_quantity, "updated_at": datetime.now(timezone.utc)}}
            )

            break
    else:
        db.carts.update_one(
            {"cart_id": cart["cart_id"]},
            {
                "$push": {"items": {"product_id": product_id,
                "quantity": quantity}},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        
    flash(f"Added {quantity} {product["name"]} ot your cart", "success")
    return redirect(request.referrer or url_for("cart.view_cart"))

@cart_bp.route("/cart/update", methods=["POST"])
def update_cart():
    """Update cart quantities"""
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    
    if not product_id:  
        flash("Product not fount", "damger")
        return redirect(url_for("cart.view_cart"))
    
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("cart.view_cart"))
    
    if quantity <= 0:
        # remove item from cart
        db.carts.update_one(
            {"cart_id": session.get("cart_id")},
            {
                "$pull": {"items": {"product_id": product_id}},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        flash("item removed from cart", "ifo")
    else:
        # Check stock
        if product["stock"] < quantity:
            flash(f"Sorry, only {product["stock"]} items available", "warning")
            quantity = product["stock"]
            
        db.carts.upate_one(
            {"cart_id": session.get("cart_id"), "items.product_id": product_id},
            {"$set": {"items.$.quantity": quantity, "updated_at": datetime.now(timezone.utc)}}
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
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    flash("Item removed from cart", "info")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/cart/clear")
def clear_cart():
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

@cart_bp.route("/api/cart.count")
def cart_count():
    cart = get_or_create_cart(db, session)
    count = sum(item["quantity"] for item in cart.get("items", []))
    return jsonify({"count": count})