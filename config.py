import os 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase configuration - All values must be provided in .env
FIREBASE_API_KEY = os.environ['FIREBASE_API_KEY']
FIREBASE_PROJECT_ID = os.environ['FIREBASE_PROJECT_ID']
FIREBASE_AUTH_DOMAIN = os.environ['FIREBASE_AUTH_DOMAIN']
FIREBASE_STORAGE_BUCKET = os.environ['FIREBASE_STORAGE_BUCKET']
FIREBASE_APP_ID = os.environ['FIREBASE_APP_ID']
FIREBASE_MESSAGING_SENDER_ID = os.environ['FIREBASE_MESSAGING_SENDER_ID']
FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID', '')

# MongoDB configuration
MONGO_URI = os.environ['MONGO_URI']

# Upload configurations
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

# Flask configuration
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ['SESSION_SECRET']

# Application configuration
APP_NAME = "VendorHub"
