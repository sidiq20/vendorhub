from datetime import datetime
import uuid
from typing import Optional

class Customer:
    def __init__(self, user_id, name, phone, notes: Optional[str] = None, order_count=0):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.name = name 
        self.phone = phone 
        self.notes = notes
        self.order_count = order_count
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'notes': self.notes,
            'order_count': self.order_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }