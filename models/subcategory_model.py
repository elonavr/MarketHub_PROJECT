from db import db

class SubCategory(db.Model):
    __tablename__ = 'subcategories'

    subcategory_id = db.Column(db.Integer, primary_key=True)
    subcategory_name = db.Column(db.String(80), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)

    category = db.relationship("Category", back_populates="subcategories")

    def __repr__(self):
        return f"<SubCategory {self.subcategory_name}>"
