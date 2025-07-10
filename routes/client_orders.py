from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
import uuid
from utils.validators import validate_checkout_form
from services.order_service import build_cart_items, create_orders_from_cart

# Create Blueprint
client_orders_bp = Blueprint("client_orders", __name__)

# Initialize database connection
db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
#  Order status
ORDER_STATUS = {
    "pending": "Pending",
    "processing": "Processing",
    "shipped": "Shipped",
    "delivered": "Delivered",
    "cancelled": "Cancelled"
}

# order routes
@client_orders_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_id = session.get("cart_id")
    cart = db.carts.find_one({"cart_id": cart_id}) if cart_id else None
    
    if not cart or not cart.get("items"):
        flash("Your cart is empty", "waring")
        return redirect(url_for("marketplace.home"))
    
    cart_items, total = build_cart_items(db, cart)
    
    if request.method == "POST":
        missing = validate_checkout_form(request.form)
        if missing:
            flash(f"Missing fields: {', '.join(missing)}")
    
    
@client_orders_bp.route("/orders/confirmation")
def confirmation():
    order_ids = session.get('recent_orders', [])
    if not order_ids:
        flash("No recent orders found", "warning")
        return redirect(url_for('marketplace.home'))
    
    orders = list(db.client_orders.find({'order_id': {'$in': order_ids}}))
    
    session.pop('recent_orders', None)
    
    return render_template(
        'orders/confirmation.html',
        orders=orders,
        now=datetime.now(),
    )
    
@client_orders_bp.route("/orders")
def orders_history():
    if session.get('user_id'):
        orders = list(db.client_orders.find(
            {'user_id': session.get('user_id')},
        ).sort('created_at', -1))
        
    elif session.get('email'):
        orders = list(db.client_orders.find(
            {'customer.email': session.get('email')},
        ).sort('created_at', -1))
    else:
        flash("Please login to view your orders", "info")
        return redirect(url_for('auth.login'))
    
    return render_template(
        'orders/orders.html',
        orders=orders,
        now=datetime.now(),
    )
    
@client_orders_bp.route("/orders/<order_id>")
def order_details(order_id):
    order = db.client_orders.find_one({'order_id': order_id})
    if not order:
        flash("order not found", "danger")
        return redirect(url_for('client_orders.orders_history'))
    
    if order.get('user_id') and order['user_id'] != session.get('user_id'):
        if order.get('customer', {}).get('email') != session.get('email'):
            flash("You are not authorized to view this order", "danger")
            return redirect(url_for('client_orders.orders_history'))
        
    store = db.users.find_one(
        {'_id': ObjectId(order['store_id'])},
        {'store.name': 1, 'store.slug': 1, 'store.logo': 1, 'store.whats_app': 1}
    )
    
    return render_template(
        'orders/details.html',
        order=order,
        store=store['store'] if store else {},
        statuses=ORDER_STATUS,
        now=datetime.now()
    )
    
@client_orders_bp.route("/orders/track/<order_id>")
def track_order(order_id):
    order = db.client_orders.find_one({'order_id': order_id})
    if not order:
        flash("Order not found", "danger")
        return redirect(url_for("matketplace.home"))
    
    store = db.users.find_one(
        {"_id": ObjectId(order['store_id'])},
        {"store.name": 1, "store.slug": 1}
    )
    
    return render_template(
        'orders/track.html',
        order=order,
        store=store['store'] if store else {},
        statuses=ORDER_STATUS,
        now=datetime.now()
    )