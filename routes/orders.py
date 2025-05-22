from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from datetime import datetime
from routes.dashboard import login_required

orders_bp = Blueprint('orders', __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
@orders_bp.route('/orders')
@login_required
def index():
    user_id = session.get("user_id")
    
    # get all orders for this user 
    orders = list(db.orders.find({
        'user_id': user_id
    }).sort('create_at', 1))
    
    return render_template("orders/index.html", orders=orders)

@orders_bp.route("/orders/addd", methods=["GET", "POST"])
@login_required
def add():
    user_id = session.get("user_id")
    
    #get all products
    products = list(db.products.find({'user_id': user_id}))
    
    # Get all customer for this selection
    customer = list(db.customers.find({'user_id': user_id}))
    
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        product_ids = request.form.getlist("product_ids")
        quantities = request.form.getlist("quantities")
        notes = request.form.get("notes", "")
        
        # Validate inputs
        if not customer_id or not product_ids or not quantities:
            flash("Customer, products and quantities are required", "danger")
            return render_template("orders/add.html", products=products, customer=customer)
        
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            flash("Customer not found", "danger")
            return render_template("orders/add.html", products=products, customer=customer)
        
        total = 0
        items = []
        
        for i, product_id in enumerate(product_ids):
            if i < len(quantities):
                try:
                    quantity = int(quantities[i])
                    if quantity <= 0:
                        continue
                    
                    product = db.products.find_one({"_id": ObjectId})
                    if not product:
                        continue
                    
                    # check if enough stock
                    if product["stock"] < qauntity:
                        flash(f"Not enough stock for {product["name"]}", "danger")
                        return render_template("orders/add.html", products=products, customer=customer)
                    
                    item_total = product["price"] * quantity
                    total += item_total
                    
                    items.append({
                        'product_id': str(product["_id"]),
                        'product_name': product["name"],
                        'price': product["price"],
                        'quantity': quantity,
                        'total': item_total
                    })
                    
                    # update stock
                    db.products.update_one(
                        {"_id": ObjectId(product_id)},
                        {"$inc": {"stock": -quantity}}
                    )
                    
                except ValueError and KeyError:
                    flash("Invalid quantity", "danger")
                    return render_template("orders/add.html", products=products, customer=customer)
            
        # create order
        order_id = db.orders.insert_one({
            'user_id': user_id,
            'customer_id': customer_id,
            'customer_name': customer["name"],
            'customer_phone': customer["phone"],
            'items': items,
            'total': total,
            'notes': notes,
            'status': 'pending',
            'create_at': datetime.now(),
            'update_at': datetime.now()
        })
        
        # Update customer
        db.customers.update_one(
            {'_id': ObjectId(customer_id)},
            {
                '$inc': {'order_count': 1},
                '$set': {'updated_at': datetime.now()}
            }
        )
        
        flash("Order created successfully", "success")
        return redirect(url_for("orders.index"))

    return render_template("orders/add.html", products=products, customer=customer)

@orders_bp.route("/orders/view/<order_id>")
@login_required
def view(order_id):
    user_id = session.get("user_id")
    
    # get order
    order = db.orders.find_one({
        '_id': ObjectId(order_id),
        'user_id': user_id
    })
    
    if not order:
        flash(("Order not founf", "danger"))
        return redirect(url_for("orders.index"))
    
    return render_template("orders/view.html", order=order)

@orders_bp.route("/orders/fullfill/<order_id>")