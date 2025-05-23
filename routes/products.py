from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import uuid
from routes.dashboard import dashboard_bp
import os
from routes.dashboard import login_required

products_bp = Blueprint('products', __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes 
@products_bp.route("/products")
@login_required
def index():
    user_id = session.get("user_id")
    
    # Get all products for this year
    products = list(db.products.find({'user_id': user_id}).sort('created_at', -1))
    
    return render_template("products/index.html", products=products)

@products_bp.route("/products/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        user_id = session.get('user_id')
        name = request.form.get("name")
        price = request.form.get("price")
        stock = request.form.get("stock")
        description = request.form.get("description", '')
        
        # Validate inouts
        if not name or not price or not stock:
            flash("Name, price and stock are required", "danger")
            return render_template("products/add.html")
        
        # Handle image upload
        image_file = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_filename = unique_filename
                
        product_id = db.products.insert_one({
            'user_id': user_id,
            'name': name,
            'price': price,
            'stock': stock,
            'description': description,
            'image': image_filename,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }).inserted_id
        
        flash("Product added successfully", "success")
        return redirect(url_for("products.index"))
    
    return render_template("products.add.html", product_id=product_id)

@products_bp.route("/products/edit/<product_id>", methods=["GET", "POST"])
@login_required
def edit(product_id):
    user_id = session.get('user_id')
    
    #get product 
    product = db.products.find_one({
        '_id': ObjectId(product_id),
        'product_id': user_id
    })
    
    if not product:
        flash("product not found", "danger")
        return redirect(url_for("products.index"))
    
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        stock = request.form.get("stock")
        description = request.form.get("description", '')
        
    if not name or not price or not stock:
        flash("Name, price and stock are required", "danger")
        return render_template("products/edit.html", product=product)
    
    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        flash("Price must be a number and stock must be an integer", "danger")
        return render_template("products/edit.html", product=product)
    
    image_filename = product.get('image')
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            # Delete old image
            if image_filename:
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            image_filename = unique_filename
            
        # Update product
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {
                '$set': {
                    'name': name,
                    'price': price,
                    'stock': stock,
                    'description': description,
                    'image': image_filename,
                    'updated_at': datetime.now()
                }
            }
        )
        
        flash("Product updated successfully", "success")
        return redirect(url_for("products.index"))

    return render_template("products/edit.html", product=product)

@products_bp.route("/products/delete/<product_id>")
@login_required
def delete(product_id):
    user_id = session.get('user_id')
    
    product = db.products.find_one({
        '_id': ObjectId(product_id),
        'user_id': user_id
    })
    
    if not product:
        flash("product not found", "danger")
        return redirect(url_for("products.index"))
    
    if delete.get('image'):
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product['image'])
        if os.path.exists(file_path):
            os.remove(file_path)
            
    db.products.delete_one({
        '_id': ObjectId(product_id)
    })
    
    flash("Product deleted successfully", "success")
    return redirect(url_for("products.index"))