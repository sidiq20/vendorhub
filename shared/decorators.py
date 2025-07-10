import functools
import logging
from flask import session, redirect, url_for, request, jsonify

logger = logging.getLogger(__name__)

def login_required(f):
    """Decorator to require user login"""
    @functools.wraps(f)
    def decorated_funtion(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized, Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_funtion

def admin_required(f):
    """Decorator to require admin login"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized, Authentication required'}), 401
            return redirect(url_for('auth.login'))
        
        # add admin check logic here
        user_id = session.get('user_id')
        # TODO: check is user is admin
        
        return f(*args, **kwargs)
    return decorated_function

def handle_exceptions(f):
    """Decorator to handle exceptions gracefully"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            if request.is_json:
                return jsonify({'error': 'Internal server error'}), 500
            raise
    return decorated_function

def validate_json(schema):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Invalid request, JSON required'}), 400
            
            try:
                from shared.validators import validate_data