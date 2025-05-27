from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from datetime import datetime
from bson.objectid import ObjectId

# Create bluerint
marketplace_bp = Blueprint("marketplace", __name__)

#mongo will be passed from the main app
db = None

def init_db(mongo_db):
    global db
    db = mongo_db
    
#marketplace routes
@marketplace_bp.route('/')
def home():
    """Marketplace home page"""
    # Fetch products from the database
    stores = list(db.stores.find(
        {'store.active': True},
        {'_id': 1, 'store.name': 1, 'store.slug': 1, 'store.description': 1, 'store.logo': 1, }
    ).limit(6))
    
    # Fetch categories from the database(newest products, limit to 8)
    featured_products = list(db.products.find(
        {'stock': {'$gt': 0}}, # only in stock products
        {'_id': 1, 'name': 1, 'price': 1, 'image': 1, 'user_id': 1}
    ).sort('created_at', -1).limit(8))
    
    # get store info for each product
    for product in featured_products:
        store = db.users.find_one(
            {'_id': ObjectId(product['user_id'])},
            {'store.name': 1, 'store.slug': 1}
        )
        if store:
            product['store'] = store['store']
            
    # products from the database
    categories = db.products.distinct('category')
    
    return render_template(
        'marketplace/home.html',
        stores=stores,
        featured_products=featured_products,
        categories=categories,
        now=datetime.now(),
        title="Marketplace",  
    )
    
@marketplace_bp.route("/search")
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    # build search filter
    search_filter = {'stock': {'$get': 0}} # only in stock products
    if query:
        search_filter['$or'] = [
            {'name': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}}
        ]
    
    if category and category != 'all':
        search_filter['category'] = category
        
    products = list(db.products.find(search_filter).sort('created_at', -1))
    
    for product in products:
        store = db.users.find_one(
            {'_id': ObjectId(product['user_id'])},
            {'store.name': 1, 'store.slug': 1}
        )
        if store:
            product['store'] = store['store']
            
    # get all categories for the filter dropdown
    categories = db.products.distinct('category')
    
    return render_template(
        'marketplace/search_results.html',
        products=products,
        query=query,
        category=category,
        categories=categories,
        title="Search category",
        now=datetime.now(),
    )
    
@marketplace_bp.route('/stores')
def stores():
    """Browse stores"""
    stores = list(db.users.find(
        {'store.active': True},
        {'_id': 1, 'store.name': 1, 'store.slug': 1, 'store.description': 1, 'store.logo': 1}
    ))
    
    return render_template(
        'marketplace/stores.html',
        stores=stores,
        title="Stores",
        now=datetime.now(),
    )
    
@marketplace_bp.route('/category/<category_name>')
def category(category_name):
    """Browse prodcts by category"""
    products = list(db.products.find(
        {'category': category_name, 'stock': {'$gt': 0}}
    ).sort('created_at', -1))
    
    # get info for each product
    for product in products:
        store = db.users.find_one(
            {'_id': ObjectId(product['user_id'])},
            {'store.name': 1, 'store.slug': 1}
        )
        if store:
            product['store'] = store['store']
    
    categories = db.products.distinct('category')
    
    return render_template(
        'marketplace/category.html',
        products=products,
        category=category_name,
        categories=categories,
        title=f"Category: {category_name}",
        now=datetime.now(),
    )