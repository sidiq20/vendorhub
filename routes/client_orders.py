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
            
            db.client_orders.insert_one({
                'order_id': order_id,
                'user_id': session.get('user_id'),
                'store_id': store_id,
                'store_name': store_data['store'].get('name', 'UnknownStore'),
                'customer': {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                },
                'items': store_data['items'],
                'total': store_data['total'],
                'status': 'pending',
                'status_text': 'Pending',
                'status_history': [
                    {'status': 'pending', 'date': datetime.now(),
                     'note': 'Order placed'}
                ],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),    
            })
            
            order_ids.append(order_id)
            
            
            db.carts.update_one(
                {'cart_id': cart_id},
                {
                    '$set': {
                        'items': [],
                        'updated_at': datetime.now()
                    }
                }
            )
            
            session.pop['recent_orders'] = order_ids
            
            return redirect(
                url_for('client_orders.confirmation')
            )
            
    return render_template(
        'orders/checkout.html',
        cart_items=cart_items,
        total=total,
        now=datetime.now(),
    )
    
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