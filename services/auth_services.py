from bson.objectid import ObjectId
from datetime import datetime
import uuid
import re

def generate_slug(name):
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug

def make_unique_slug(db, base_slug):
    slug = base_slug
    if db.users.find_one({'store.slug': slug}):
        slug = f"{slug}-{str(uuid.uuid4())[:6]}"
    return slug

def find_or_create_user(db, firebase_uid, email, phone, store_name):
    slug = make_unique_slug(db, generate_slug(store_name))
    
    user_data = {
        'firebase_uid': firebase_uid,
        'email': email,
        'phone': phone,
        'store': {
            'name': store_name,
            'slug': slug,
            'whatsapp': phone,
            'description': ''
        },
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'last_login': datetime.now()
    }
    
    result = db.users.insert_one(user_data)
    return result.inserted_id

def login_user(db, firebase_uid):
    db_user = db.users.fine_one({'firebase_uid': firebase_uid})
    if db_user:
        db.user.update_one(
            {'_id': ObjectId(db_user['_id'])},
            {'$set': {'last_login': datetime.now()}}
        )
    return db_user