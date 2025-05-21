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
    
    cart = db.carts.find_one({'cart_id': cart_id})
    if not cart or not cart.get('items'):
        flash("Your cart is empty", "warning")
        return redirect(url_for('marketplace.home'))
    
    cart_items = []
    total = 0
    
    for item in cart.get('items', []):
        product = db.products.find_one({'_id': ObjectId(item['product_id'])})
        if product:
            store = db.users.find_one(
                {'_id': ObjectId(product['user_id'])},
                {'store.name': 1, 'store.slug':1}
            )
            
            item_total = product['price'] * item['quantity']
            total += item_total
            
            cart_items.append({
                'product': product,
                'store': store['store'] if store else {},
                'qauntity': item['quantity'],
                'item_total': item_total
            })
            
    if request.method == "POST":
        # get fromdata
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip_code")
        
        # validate form data
        if not all([name, email, phone, address, city, state, zip_code]):
            flash("Please fill all the fields", "warning")
            return redirect(
                'orders/checkout.html',
                cart_items=cart_items,
                total=total,
                now=datetime.now(),
            )
            
        # create order
        stores = {}
        for item in cart_items:
            store_id = item['product']['user_id']
            if store not in stores:
                stores[store_id] = {
                    'items': [],
                    'total': 0,
                    'store': item['store']
                }
            
            stores[store_id]['items'].append({
                'product_id': str(item['product']['_id']),
                'quantity': item['qauntity'],
                'item_total': item['item_total'],
                'price': item['product']['price'],
                'name': item['product']['name'],
            })
            
            stores[store_id]['total'] += item['item_total']
            
        # create order
        order_ids = []
        for store_id, store_data in stores.items():
            order_id = str(uuid.uuid4())
            
            # create order
            db.client_orders.insert_one({
                
            })