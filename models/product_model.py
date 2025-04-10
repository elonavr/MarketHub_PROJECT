from db import db


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable = False, default=0)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    image_url = db.Column(db.String(500), nullable=True) 
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    category = db.relationship("Category", back_populates="products")
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.subcategory_id'))
    subcategory = db.relationship("SubCategory", backref="products")

    __table_args__ = (
        db.UniqueConstraint('product_name', 'supplier_id', name='uix_product_supplier'),
    )


    def __repr__(self):
        return f'<Product {self.product_name}>'
 

  

    

