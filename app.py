import os 
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, session, send_from_directory, request
from pymongo import MongoClient
import firebase_admin
from firebase_admin import credentials
from werkzeug.utils import secure_filename
import uuid
import json 
from io import StringIO
from dotenv import load_dotenv

from routes.auth import auth_bp
from routes.cart import cart_bp
from routes.dashboard import dashboard_bp
from routes.marketplace import marketplace_bp
from routes.products import products_bp
from routes.store import store_bp
from routes.customers import customers_bp
from routes.client_orders import client_orders_bp
from routes.reviews import reviews_bp
from routes.settings import settings_bp
from routes.orders import orders_bp

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.permanent_session_lifetime = timedelta(days=7)

# configure
MONGO_URI = os.environ.get('MONGO_URI')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initalize Firebase Admin SDK
try:
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if service_account_json:
        cred = credentials.Certificate(json.load(StringIO(service_account_json)))
        firebase_admin.initialize_app(cred)
        logger.info("firebase initailzed with service account from evvironemt variable")
    # Fall back to file-based config
    elif os.path.exists("firebase-service-account.json"):
        try:
            cred = credentials.Certificate("firebase-service-account.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initailzed account with service account from file")
        except Exception as file_error:
            logger.error(f"Firebase service account file error: {file_error}")
            # initialze without credentails 
            firebase_admin.initialize_app()
            logger.info("Firebase initalized without credentials (limited fucntionality)")
    # try applications credentials
    else:
        firebase_admin.initialize_app()
        logger.info("Firebase initalized with application default credentials")

except Exception as e:
    logger.error(f"Firebase initailzed error: {e}")
    logger.warning("Using Firebase web SDK for authentication only.")

# MongoDB Connection
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db_name = 'vendorapp'
    db = mongo_client[db_name]
    mongo_client.admin.command('ping')
    logger.info(f"Connected to MongoDB successfully ({db_name})")
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    logger.error("Cannot continue without MongoDB connection")
    raise

# initailze routes with databse connection
from routes import auth, cart , dashboard, marketplace, products, store, customers, client_orders, reviews, settings, orders


auth.init_db(db)
dashboard.init_db(db)
cart.init_db(db)
marketplace.init_db(db)
products.init_db(db)
store.init_db(db)
customers.init_db(db)
client_orders.init_db(db)
reviews.init_db(db)
settings.init_db(db)
orders.init_db(db)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(marketplace_bp)
app.register_blueprint(products_bp)
app.register_blueprint(store_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(client_orders_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(orders_bp)


@app.after_request
def log_request_info(response):
    logger.info(f"Request: {request.method} {request.path} => Status: {response.status_code}")
    return response

@app.template_filter("format_currency")
def format_currency(amount):
    return f"${amount:.2f}" if amount else "$0.00"

@app.template_filter("format_datetime")
def format_datetime(date):
    if not date:
        return ""
    return date.strftime("%b %d, %Y %I:%M %p")

@app.template_filter("format_date")
def format_date(date):
    if not date:
        return ""
    return date.strftime("%Y-%m-%d")

# File serving route
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Root route
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("marketplace.home"))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
