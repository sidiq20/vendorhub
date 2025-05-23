from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from bson.objectid import ObjectId
from datetime import datetime
import uuid

reviews_bp = Blueprint('reviews', __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
# Routes
@reviews_bp.route("/reviews")
def index():
    """View all reviews"""
    if session.get("user_id"):
        products = list(db.products.find({
            'user_id': session.get("user_id")
        }))
        products_ids = [str(products['_id']) for products in products]
        
        reviews = list(db.reviews.find(
            {'product_id': {'$in': products_ids}},
        ).sort('created_at', -1))
        
        # Add product info to each review
        product_map = {str(product['_id']): product for product in products}
        for review in reviews:
            review["product"] = product_map.get(review['product_id'], {})
            
        return render_template(
            "revies/index.html",
            reviews=reviews,
            now=datetime.now(),
        )
    else:
        flash("You must be logged in to view your reviews.", "danger")
        return redirect(url_for("auth.login"))
    
@reviews_bp.route("/reviews/<product_id>/review", methods=["POST"])
def add_review(product_id):
    # check if products exists
    product = db.products.find_one({'_id': ObjectId(product_id)})
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("marketplace.home"))
    
    # get store info
    store = db.users.find_one(
        {'_id': ObjectId(product['user_id'])},
        {'store.name': 1, 'store.slug': 1}
    )
    
    if not store:
        flash("Store not found", "danger")
        return redirect(url_for("marketplace.home"))
    
    