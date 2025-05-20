import os 
from dotenv import load_dotenv

load_dotenv()

# Firebase configuration
FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', 'AIzaSyD8UjMKoaOMNgaJx4sKn_VOAezdU_eNc2w')
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'vendorhub-b14ad')
FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', 'vendorhub-b14ad.firebaseapp.com')
FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', 'vendorhub-b14ad.firebasestorage.app')
FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID', '1:887510978000:web:bd9793a6e37471951dbdd5')
FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '887510978000')
FIREBASE_MEASUREMENT_ID = os.environ.get('FIREBASE_MEASUREMENT_ID', 'G-4WQC5MJMHF')

# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://sidiqolasode:6BLuUbubaw3PCp5X@vendorapp.a0phodn.mongodb.net/?retryWrites=true&w=majority&appName=vendorapp&tls=true&tlsAllowInvalidCertificates=true')

# Upload configurations
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

# Flask configuration
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

# Application configuration
APP_NAME = "VendorHub"
