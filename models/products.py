from datetime import datetime
import uuid
from typing import Optional

class Product:
    def __init__(self, user_id, name = None, price = None, stock=0, description: Optional[str] = None, image = None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description
        self.image = image
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'description': self.description,
            'image': self.image,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }