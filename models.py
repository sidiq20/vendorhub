# from enum import unique
# from itertools import product
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# import json
# from dataclasses import dataclass, field
# import uuid
# from typing import Optional, List


# class User:
#     def __init__(self, firebase_uid, name, email=None, phone=None, store_name=None,
#                 store_slug=None, store_whatsapp=None, store_description=None):
#         self.firebase_uid = firebase_uid
#         self.email = email
#         self.phone = phone
#         self.name = name
#         self.created_at = datetime.utcnow()
#         self.updated_at = datetime.utcnow()

#         # Store relationship
#         self.store_name = store_name
#         self.store_slug = store_slug
#         self.store_whatsapp = store_whatsapp
#         self.store_description = store_description
    

#     def to_dict(self):
#         return{
#             'id': self.id,
#             'firebase_uid': self.firebase_uid,
#             'email': self.email,
#             'phone': self.phone,
#             'name': self.name,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None,
#             'store': {
#                 'name': self.store_name,
#                 'slug': self.store_slug,
#                 'whatsapp': self.store_whatsapp,
#                 'description': self.store_description
#             }
#         }    
        
# class Product:
#     def __init__(self, user_id, name, price, stock=0, description=None, image=None):
#         self.user_id = user_id
#         self.name = name
#         self.price = price
#         self.stock = stock
#         self.description = description
#         self.image = image
#         self.created_at = datetime.utcnow()
#         self.updated_at = datetime.utcnow()


#     def to_dict(self):
#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'name': self.name,
#             'price': self.price,
#             'stock': self.stock,
#             'description': self.description,
#             'image': self.image,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.upload_at.isoformat() if self.updated_at else None
#         } 

# class Customer:
#     def __init__(self, user_id, name, phone, notes=None, order_count=0):
#         self.user_id = user_id
#         self.name = name
#         self.phone = phone
#         self.notes = notes
#         self.order_count = order_count
#         self.created_at = datetime.utcnow
#         self.updated_at = datetime.utcnow

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'name': self.name,
#             'phone': self.phone,
#             'notes': self.notes,
#             'order_count': self.order_count,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.created_at.isoformat() if self.updated_at else None
#         }

# class Order:
#     def __init__(self, user_id, customer_name, customer_phone, total, customer_id=None, 
#                     status='pending', notes=None, items=None):
#         self.user_id = user_id
#         self.customer_id = customer_id
#         self.customer_name = customer_name
#         self.customer_phone = customer_phone
#         self.total = total
#         self.status = status
#         self.notes = notes
#         self.created_at = datetime.utcnow()
#         self.updated_at = datetime.utcnow()
#         self.items = items or []

#     def to_dict(self):
#         items_list = [item.to_dict() for item in self.items] if self.items else []

#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'customer_id': self.customer_id,
#             'customer_phone': self.customer_name,
#             'total': self.total,
#             'status': self.status,
#             'notes': self.notes,
#             'items': items_list,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None
#         }

# class OrderItem:
#     def __init__(self, order_id, product_id, name, price, quantity=1):
#         self.order_id = order_id
#         self.product_id = product_id
#         self.name = name
#         self.price = price
#         self.quantity = quantity

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'order_id': self.order_id,
#             'product_id': self.product_id,
#             'name': self.name,
#             'price': self.price,
#             'quantity': self.quantity,
#             'total': self.price * self.quantity
#         }