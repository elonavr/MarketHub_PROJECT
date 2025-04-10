from db import db


class Category(db.Model):
    __tablename__ = "category"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(128), unique=True, nullable=False)
    
    products = db.relationship('Product', back_populates='category', cascade="all, delete-orphan")

    subcategories = db.relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")




