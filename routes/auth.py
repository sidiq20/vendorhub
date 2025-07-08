from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from bson.objectid import ObjectId
from services.auth_services import find_or_create_user, login_user
from utils.firebase import firebase_config, verify_firebase_token
from datetime import datetime

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
            decoded_token = verify_firebase_token(id_token)
            firebase_uid = decoded_token['uid']
            db_user = login_user(db, firebase_uid)

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
            decoded_token = verify_firebase_token(id_token)
            firebase_uid = decoded_token["uid"]
            
            existing_user = db.users.find_one({'firebase_uid': firebase_uid})
            if existing_user:
                flash("User already exists. Please login instead.", "warning")
                return redirect(url_for("auth.login"))

            user_id = find_or_create_user(db, firebase_uid, email, phone, store_name)

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