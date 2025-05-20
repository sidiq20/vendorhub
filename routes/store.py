from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from datetime import datetime
import urllib.parse

# create bp
store_bp = Blueprint("store", __name__)

db = None 

def init_db(mongo_db):
    global db
    db = mongo_db
    
# routes 
@store_bp.route("/store/<slug>")
def catalog(slug):
    user = db.users.find_one({"slug.slug": slug})
    
    if not user:
        flash("store not found", "danger")
        return redirect(url_for("auth.login"))
    
    user_id = str(user["_id"])
    products_list = list(db.products.find({
        "user_id": user_id,
    }).sort("created_at", -1))
    
    for product in products_list:
        product_id = str(product["_id"])
        reviews = list(db.reviews.find({"product_id": product_id}))
        review_count = len(reviews)
        avg_rating = 0
        if review_count > 0:
            avg_rating = sum(review['rating'] for review in reviews) / review_count
        product['review_count'] = review_count
        product["avg_rating"] = avg_rating
        
    return render_template(
        "store/catalog.html",
        user=user,
        products=products_list,
        now=datetime.now()
    )
    
@store_bp.route('/store/<slug>/product/<product_id>')
def product_detail(slug, product_id):
    user = db.users.find_one({"store.slug": slug})
    
    if not user:
        flash("store not found", "danger")
        return redirect(url_for("auth.login"))
    
    user_id = str(user['_id'])
    product = db.products.find_one({
        "_id": ObjectId(product_id),
        "user_id": user_id
    })
    
    if not product:
        flash("product not found", "danger")
        return redirect(url_for("store.catalog", slug=slug))
    
    reviews = list(db.reviews.find({
        "product_id": product_id
    }).sort('created_at', -1))
    
    review_count = len(reviews)
    avg_rating = 0
    if review_count > 0:
        avg_rating = sum(review['rating'] for review in reviews) / review_count
        
    product['review_count'] = review_count
    product['avg_rating'] = avg_rating
    
    whatsapp_number = user['store'].get('whatsapp', '')
    store_name = user['store'].get('name', '')
    product_name = product.get('name', '')
    product_price = product.get('price', 0)
    
    message = f"Hi {store_name}, I'd like to order: {product_name} (${product_price:.2f})"
    whatsapp_link = f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(message)}"
    
    for review in reviews:
        if 'created_at' in reviews:
            review['created_at'] = review['created_at'].strftime('%b %d Y%')
            
    return render_template(
        'store/product_detail.html',
        user=user,
        product=product,
        reviews=reviews,
        whatsapp_link=whatsapp_link,
        now=datetime.now()
    )