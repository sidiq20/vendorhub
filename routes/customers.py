from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from routes.dashboard import login_required

customers_bp = Blueprint("customers", __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
@customers_bp.route("/customers")
@login_required
def index():
    user_id = session.get("user_id")
    
    customer = list(db.customers.find({"user_id": user_id}).sort('name', 1))
    
    return render_template("customers/index.html", customers=customer)

@customers_bp.route("/customers/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        user_id = session.get("user_id")
        name = request.form.get("name")
        phone = request.form.get("phone")
        notes = request.form.get("notes")
        
        # valide input
        if not name or not phone:
            flash("Name and phone are required.", "danger")
            return render_template("customers/add.html")
        
        # checkif customer is using the same phone
        existing = db.customers.find_one({
            'user_id': user_id,
            'phone': phone
        })
        
        if existing:
            flash("Customer with this phone number already exists.", "warning")
            return render_template("customers/add.html")
        
        customer_id = db.customer.insert_one({
            'user_id': user_id,
            'name': name,
            'phone': phone,
            'notes': notes,
            'order_count': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
        
        flash("Customer added successfully.", "success")
        return redirect(url_for("customers.index"))
    
    return render_template("customers/add.html", customer_id=customer_id)

@customers_bp.route("/customers/edit/<customer_id>", methods=["GET", "POST"])
@login_required
def edit(customer_id):
    user_id =  session.get("user_id")
    
    customer = db.customers.find_one({
        '_id': ObjectId(customer_id),
        'user_id': user_id
    })
    
    if not customer:
        flash("customer not found", "danger")
        return redirect(url_for("customers.index"))
    
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        notes = request.form.get("notes", '')
        
        # validate input
        if not name or not phone:
            flash("Name and phone are required.", "danger")
            return render_template("customers/edit.html", customer=customer)
        
        # check if customer is using the same phone
        exsisting = db.customers.fond_one({
            'user_id': user_id,
            '_id': {'$ne': ObjectId(customer_id)},
            'phone': phone
        })
        
        if exsisting:
            flash('Customer with phone number already exists.','warning')
            return render_template("customers/edit.html", customer=customer)
        
        #update customer 
        db.customers.update_one(
            {'_id': ObjectId(customer_id)},
            {
                '$set': {
                    'name': name,
                    'phone': phone,
                    'notes': notes,
                    'updated_at': datetime.now()
                }
            }
        )
        
        flash("Customer updated successfully.", "success")
        return redirect(url_for("customers.index"))
    
    return render_template("customers/edit.html", customer=customer)

@customers_bp.route("/customers/delete/<customer_id>")
@login_required
def view(customer_id):
    user_id = session.get('user_id')
    
    customer = db.customers.find_one({
        '_id': ObjectId(customer_id),
        'user_id': user_id
    })
    
    
    if not customer:
        flash("customer not found", "danger")
        return(url_for('customer.index'))
    
    #get customers order 
    orders = list(db.orders.find({
        '_id': user_id,
        'customer_id': customer_id
    }).sort('created_at', -1))
    
    return render_template('customers/view.html', customer, orders=orders)

@customers_bp.route('/costomer/delete/<customer_id>')
@login_required
def delete(customer_id):
    user_id = session.get('user_id')
    
    # get customer
    customer = db.customer.find_one({
        '_id': ObjectId(customer_id),
        'user_id': user_id
    })
    
    if not customer:
        flash('customer not found', 'danger')
        return redirect(url_for('customer.index'))
    
    #check if customer has orders 
    order_count = db.customer.count_documents({
        'user_id': user_id,
        'customer_id': customer_id
    })
    
    if order_count > 0:
        flash("Cannot delete customer with existing orders", "danger")
        return redirect(url_for('customer.view', customer_id=customer_id))
    
    # delete customer 
    db.customer.delete_one({
        '_id': ObjectId(customer_id)
    })
    flash("customer deleted successfully", "success")
    return redirect(url_for("customer.index"))