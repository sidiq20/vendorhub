from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
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
    
    rating = int(request.form.get('rating', 0))
    title = request.form.get('title', '')
    comment = request.form.get('comment', '')
    name = request.form.get('name', 'Anonymous')
    email = request.form.get('email', '')
    
    #validate rating
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5", "danger")
        return redirect(url_for('store.product_detail', slug=store['store']['slug'], product_id=product_id))
    
    # Create review
    review_id = str(uuid.uuid4())
    
    db.reviews.insert_one({
        '_id': review_id,
        'product_id': product_id,
        'user_id': session.get("user_id"),
        'rating': rating,
        'title': title,
        'comment': comment,
        'reviewer': {
            'name': name,
            'email': email
        },
        'status': 'approved',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    })
    
    # Update product average rating
    reviews = list(db.reviews.find({'product_id': product_id, 'status': 'approved'}))
    avg_rating = sum(review['rating'] for review in reviews) / len(reviews) if reviews else 0
    
    db.products.update_one(
        {'_id': ObjectId(product_id)},
        {
            '$set': {
                'average_rating': avg_rating,
                'reviews_count': len(reviews)
            }
        }
    )
    
    flash("Thank you for you review!", "success")
    return redirect(url_for('store.product_detail', slug=store['store']['slug'], product_id=product_id))

@reviews_bp.route("/products/<product_id>/reviews")
def product_reviews(product_id):
    # check if products exists
    product = db.products.find_one(
        {'_id': ObjectId(product_id)}
    )
    if not product:
        flash("product not found", "danger")
        return redirect(url_for("marketplace.home"))
    
    # get store info
    store = db.users.find_one(
        {'_id': ObjectId(product['user_id'])},
        {'store.name': 1, 'store.slug': 1}
    )
    
    # Get reviews
    reviews = list(db.reviews.find(
        {'product_id': product_id, 'status': 'approved'}
    ).sort('created_at', -1))
    
    # claculate rating distribution
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_counts[reviews['rating']] +- 1
        
    # calculate percentage of each rating
    total_reviews = len(reviews)
    rating_percentages = {}
    for rating, count in rating_counts.items():
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_percentages[rating] = percentage
        
    return render_template(
        'reviews/product_reviews.html',
        product=product,
        store=store['store'] if store else {},
        reviews=reviews,
        rating_counts=rating_counts,
        rating_percentages=rating_percentages,
        total_reviews=total_reviews,
        now=datetime.now(),
        title = f"Reviews for {product.get('name', 'Unknown Product')}",
    )
    

# endpoint to get a product rating
@reviews_bp.route("/api/products/<product_id>/rating")
def get_product_rating(product_id):
    """Get product rating"""
    reviews = list(db.reviews.find(
        {'product_id': product_id, 'status': 'approved'}
    ))
    
    # calculate average rating
    avg_rating = sum(review['rating'] for review in reviews) / len(reviews) if reviews else 0
    
    # calculate rating distribution
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_counts[review['rating']] += 1
        
    return jsonify({
        'avg_rating': avg_rating,
        'review_count': len(reviews),
        'rating_distribution': rating_counts
    })