import re
from typing import Dict, List, Any, Optional
from marshmallow import Schema, fields, validate, ValidationError as MarshmallowValidationError


class BaseValidator:
    """Base validator class"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's between 10-15 digits
        return 10 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate URL slug format"""
        pattern = r'^[a-zA-Z0-9-_]+$'
        return bool(re.match(pattern, slug))
    
class UserRegisterationSchema(Schema):
    """Schema for user registration validation """
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    store_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    id_token = fields.Str(required=True)
    
class ProductSchema(Schema):
    """Schema for product validation """
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Int(required=True, validate=validate.Range(min=0))
    description = fields.Str(validate=validate.Length(max=1000))
    category = fields.Str(validate=validate.Length(max=100))
    
class OrderSchema(Schema):
    """Schema for order validation"""
    customer_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    customer_phone = fields.Str(required=True, validate=validate.Length(min=10, max=20))
    items = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))
    notes = fields.Str(validate=validate.Length(max=500))
    
def validate_data(schema: Schema, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data againt schema"""