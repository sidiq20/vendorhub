from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
import uuid

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
    """Checkout process"""
    # Check if cart exist and has items
    cart_id = session.get('cart_id')
    if not cart_id:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("marketplace.home"))