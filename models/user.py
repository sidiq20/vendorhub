from datetime import datetime
from typing import Optional
import uuid


class User:
    def __init__(self, firebase_uid: str, name: str, email: Optional[str] = None, phone: Optional[str] = None,
                 store_name: Optional[str] = None, store_slug: Optional[str] = None,
                 store_whatsapp: Optional[str] = None, store_description: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.firebase_uid = firebase_uid
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Store relationship
        self.store_name = store_name
        self.store_slug = store_slug
        self.store_whatsapp = store_whatsapp
        self.store_description = store_description

    def to_dict(self):
        return {
            'id': self.id,
            'firebase_uid': self.firebase_uid,
            'email': self.email,
            'phone': self.phone,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'store': {
                'name': self.store_name,
                'slug': self.store_slug,
                'whatsapp': self.store_whatsapp,
                'description': self.store_description
            }
        }
