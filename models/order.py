from datetime import datetime 
import uuid
from models.order_item import OrderItem

class Order:
    def __init__(self, user_id, customer_name, customer_phone, total, customer_id=None, status='pending', notes=None, items=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.total = total
        self.status = status
        self.notes = notes
        self.items = items or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'total': self.total,
            'status': self.status,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }