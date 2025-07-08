import uuid

class OrderItem:
    def __init__(self, order_id, product_id, name, price, quantity=1):
        self.id = str(uuid.uuid4())
        self.order_id = order_id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'project_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'qauntity': self.quantity,
            'total': self.price * self.quantity
        }