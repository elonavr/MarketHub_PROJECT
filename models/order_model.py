from db import db
from datetime import datetime, timezone

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", backref="orders")
    order_details = db.relationship('OrderDetail', back_populates='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.order_id}>'


class OrderDetail(db.Model):
    __tablename__ = 'order_details'

    detail_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False) 
    order = db.relationship('Order', back_populates='order_details')
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderDetail Order: {self.order_id}, Product: {self.product_id}>'
