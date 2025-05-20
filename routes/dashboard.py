from flask import Blueprint, render_template, redirect, url_for, session
from bson.objectid import ObjectId
from functools import wraps

dashboard_bp = Blueprint("dashboard", __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# routes
@dashboard_bp.route("/dashboard")
@login_required
def index():
    user_id = session["user_id"]
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    
    products_count = db.products.count_documents({"user_id": user_id})
    orders_count = db.orders.count_documents({"user_id": user_id})
    customers_count = db.customers.count_documents({"user_id": user_id})
    
    low_stock_products = list(db.products.find({
        'user_id': user_id,
        'stock': {'$lt': 5, '$gt': 0}
    }).limit(5))
    
    # Get recent orders
    recent_orders = list(db.orders.find({
        'user_id': user_id
    }).sort('created_at', -1).limit(5))
    
    total_sales = 0
    orders = db.orders.find({"user_id": user_id, 'status': 'fulfilled'})
    for order in orders:
        total_sales += order.get("total", 0)
        
        
    return render_template(
        "dashboard/index.html",
        user=user,
        products_count=products_count,
        orders_count=orders_count,
        customers_count=customers_count,
        low_stock_products=low_stock_products,
        recent_orders=recent_orders,
        total_sales=total_sales
    )