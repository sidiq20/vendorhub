from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from bson.objectid import ObjectId
from datetime import datetime
import re 
from routes.dashboard import login_required

# Create Blueprint
settings_bp = Blueprint("settings", __name__)

db = None
def init_db(mongo_db):
    global db
    db = mongo_db
    
    
# omo i'll fix it later how do i get the regex to work
def validate_slug(slug):
    return bool(re.match(r'^[a-zA-Z0-9-_]+$', slug)) # only alphanumeric, hyphen and underscore are allowed 
# i don't understand the regex but it works
# thank you claude and chatgpt

#routes 
@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id")
    user  = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        session.clear()
        flash("User not found, Please log in again", "danger")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        store_name = request.form.get("store_name")
        whatsapp = request.form.get("whatsapp")
        slug = request.form.get("slug")
        description = request.form.get("description")
        
        # validate inputs
        if not store_name or not whatsapp:
            flash("Store name and whatsapp are required", "danger")
            return redirect("settings.index")
        
        if not validate_slug(slug):
            flash("Slug can only contain alphanumeric characters, hyphens and underscores", "danger")
            return redirect("settings.index")
        
        # check if slug already exists
        existing_slug = db.users.find_one({
            '_id': {'$ne': ObjectId(user_id)},
            'store.slug': slug
        })
        
        if existing_slug:
            flash("This store URL is already taken, please choose another one", "danger")
            return redirect("settings.index")
        
        # update user
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "store.name": store_name,
                    "store.slug": slug,
                    "store.description": description,
                    "store.whatsapp": whatsapp,
                    "updated_at": datetime.now()
                }
            }
        )
        
        flash("Store settings updated successfully", "success")
        return redirect(url_for("settings.index"))
    
    return render_template("settings/index.html", user=user)