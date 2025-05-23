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