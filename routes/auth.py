from flask import request_finished, globals, Blueprint, render_template, redirect, request, url_for, flash, session
from firebase_admin import auth 
from bson.objectid import ObjectId
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

db = None

def init_db(mongo_db):
    global db
    db = mongo_db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        id_token = request.form.get('id_toekn')

        if not email or not password:
            flash('Email and password are reqiured', 'danger')
            return render_template('auth/login.html')
        
        try:
            if id_token:
                decoded_token = auth.verify_id_token(id_token)
                firebase_uid = decoded_token['uid']

                db_user = db.users.find_one({'firebase_uid': firebase_uid})

                if not db_user:
                    flash('User not found. Please register first.', 'danger')
                    return render_template('auth/login.html')

                session['user_id'] = str(db_user['_id'])
                session['email'] = email
                session['frebase_uid'] = firebase_uid

                db.users.update_one(
                    {'_id': ObjectId(db_users['_id'])},
                    {'$set': {'last_login': datetime.now()}}
                )

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                # Fallback to direct firebase auth
                user = auth.get_user_by_email(email)

                # check if users exists in db
                db_user = db.users.find_one({'firebase_uid': user.uid})

                if not db_user:
                    flash('User not found. Please register first.', 'danger')
                    return render_template('auth/register.html')

                # set session variable
                session['user_id'] = str(db_user['_id'])
                session['email'] = email
                session['firebase_uid'] = user.uid

                # last login
                db.users.update_one(
                    {'_id': ObjectId(db_user['_id'])},
                    {'$set': {'last_login': datetime.now()}}
                )

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.index'))
        
        except Exception as e:
            flash(f"login failed: {str(e)}", "danger")
            return render_template('auth/login.html', config=firebase_config())

    return render_template("auth/login.html", config=firebase_config())


# Function to get Firebase config for templates
def firebase_config():
    return {
        'FIREBASE_API_KEY': 'AIzaSyD8UjMKoaOMNgaJx4sKn_VOAezdU_eNc2w',
        'FIREBASE_AUTH_DOMAIN': 'vendorhub-b14ad.firebaseapp.com',
        'FIREBASE_PROJECT_ID': 'vendorhub-b14ad',
        'FIREBASE_STORAGE_BUCKET': 'vendorhub-b14ad.firebasestorage.app',
        'FIREBASE_MESSAGING_SENDER_ID': '887510978000',
        'FIREBASE_APP_ID': '1:887510978000:web:bd9793a6e37471951dbdd5',
        'FIREBASE_MEASUREMENT_ID': 'G-4WQC5MJMHF'
    }

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        store_name = request.form.get("store_name")
        id_token = request.form.get("id_token") # get firebase token id here 

        if not email or not password or not phone or not store:
            flash("All fields are required", "danger")
            return render_template("auth/register.html", config=firebase-config())

        try:
            if id_token:
                # veryify the token with admin sdk
                decoded_token = auth.verify_id_token(id_token)
                firebase_uid = decoded_token["uid"]
            else:
                # Create user in Firebase directly if no token provided
                firebase_user = auth.create_user(
                    email=email,
                    password=password,
                    phone_number=phone
                )
                firebase_uid = firebase_user.uid

            # Slug for store name
            slug = re.sub(r'[^\w\s-]', '', store_name.lower())
            slug = re.sub(r'[\s_-]+', '-', slug)

            # checking for existing stor 
            existing_slug = db.users.find_one({'store.slug': slug})
            if existing_slug:
                # Add a random suffix to make it not clash with other store slugs 
                import uuid
                slug = f"{slug}-{str(uuid.uuid4())[:8]}"

            # create new uer
            user_id = db.users.insert_one({
                'firebase': firebase_uid,
                'email': email,
                "phone": phone,
                "store": {
                    "name": store_name,
                    "slug": slug,
                    "whatsapp": phone, # Default to register Phone so no panic
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
    sessions.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))