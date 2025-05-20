from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from datetime import datetime
from bson.onjectid import ObjectId
from werkzeug.utils import secure_filename
import uuid
from routes.dashboard import dashboard_bp