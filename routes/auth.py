from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from firebase_admin import auth, credentials
from bson.objectid import ObjectId
from datetime import datetime
import re
import os

auth_bp = Blueprint('auth', __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        id_token = request.form.get('id_token')

        if not id_token:
            flash('Authentication token is required', 'danger')
            return render_template('auth/login.html', config=firebase_config())
        
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']

            # Check if user exists in database
            db_user = db.users.find_one({'firebase_uid': firebase_uid})

            if not db_user:
                flash('User not found. Please register first.', 'danger')
                return render_template('auth/login.html', config=firebase_config())

            # Set session variables
            session['user_id'] = str(db_user['_id'])
            session['email'] = email or decoded_token.get('email')
            session['firebase_uid'] = firebase_uid

            # Update last login time
            db.users.update_one(
                {'_id': ObjectId(db_user['_id'])},
                {'$set': {'last_login': datetime.now()}}
            )

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.index'))
        
        except Exception as e:
            flash(f"Login failed: {str(e)}", "danger")
            return render_template('auth/login.html', config=firebase_config())

    return render_template("auth/login.html", config=firebase_config())

# Function to get Firebase config for templates
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

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone")
        store_name = request.form.get("store_name")
        id_token = request.form.get("id_token")

        if not email or not phone or not store_name or not id_token:
            flash("All fields are required", "danger")
            return render_template("auth/register.html", config=firebase_config())

        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            firebase_uid = decoded_token["uid"]
            
            # Check if user already exists
            existing_user = db.users.find_one({'firebase_uid': firebase_uid})
            if existing_user:
                flash("User already exists. Please login instead.", "warning")
                return redirect(url_for("auth.login"))

            # Create slug for store name
            slug = re.sub(r'[^\w\s-]', '', store_name.lower())
            slug = re.sub(r'[\s_-]+', '-', slug)

            # Check for existing store with same slug
            existing_slug = db.users.find_one({'store.slug': slug})
            if existing_slug:
                # Add a random suffix to make it unique
                import uuid
                slug = f"{slug}-{str(uuid.uuid4())[:8]}"

            # Create new user
            user_id = db.users.insert_one({
                'firebase_uid': firebase_uid,
                'email': email,
                "phone": phone,
                "store": {
                    "name": store_name,
                    "slug": slug,
                    "whatsapp": phone,  # Default to registered phone
                    "description": ""
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "last_login": datetime.now()
            }).inserted_id

            # Set session variables
            session['user_id'] = str(user_id)
            session['email'] = email
            session['firebase_uid'] = firebase_uid

            flash('Registration successful!', "success")
            return redirect(url_for("dashboard.index"))

        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")
            return render_template("auth/register.html", config=firebase_config())

    return render_template("auth/register.html", config=firebase_config())

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))