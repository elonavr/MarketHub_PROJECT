from db import db

class OrderDetail(db.Model):
    __tablename__ = 'order_details'

    detail_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # קשר עם ההזמנה
    order = db.relationship('Order', back_populates='order_details')

    # קשר עם המוצר
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderDetail Order: {self.order_id}, Product: {self.product_id}>'
