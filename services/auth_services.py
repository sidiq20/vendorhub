from bson.objectid import ObjectId
from datetime import datetime
import uuid
import re

def generate_slug(name):
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug

