import os
from firebase_admin import auth

def firebase_config():
    return {
        'FIREBASE_API_KEY': os.environ.get('FIREBASE_API_KEY'),
        'FIREBASE_AUTH_DOMAIN': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'FIREBASE_PROJECT_ID': os.environ.get('FIREBASE_PROJECT_ID'),
        'FIREBASE_STORAGE_BUCKET': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'FIREBASE_MESSAGING_SENDER_ID': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'FIREBASE_APP_ID': os.environ.get('FIREBASE_APP_ID'),
        'FIREBASE_MEASUREMENT_ID': os.environ.get('FIREBASE_MEASUREMENT_ID')
    }

def verify_firebase_token(id_token):
    return auth.verify_id_token(id_token)
