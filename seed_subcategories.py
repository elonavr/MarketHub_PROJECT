from app import app
from db import db
from models.subcategory_model import SubCategory
from models.category_model import Category

with app.app_context():
    # שליפת הקטגוריות מה־DB לפי שם
    categories = {cat.category_name: cat.category_id for cat in Category.query.all()}

    subcategories = [
        # Electronics
        SubCategory(subcategory_name="Phones", category_id=categories.get("Electronics")),
        SubCategory(subcategory_name="Computers", category_id=categories.get("Electronics")),
        SubCategory(subcategory_name="TVs", category_id=categories.get("Electronics")),

        # Fashion
        SubCategory(subcategory_name="Men", category_id=categories.get("Fashion")),
        SubCategory(subcategory_name="Women", category_id=categories.get("Fashion")),
        SubCategory(subcategory_name="Accessories", category_id=categories.get("Fashion")),

        # Home & Garden
        SubCategory(subcategory_name="Furniture", category_id=categories.get("Home & Garden")),
        SubCategory(subcategory_name="Kitchen", category_id=categories.get("Home & Garden")),
        SubCategory(subcategory_name="Decor", category_id=categories.get("Home & Garden")),

        # Sports
        SubCategory(subcategory_name="Gym", category_id=categories.get("Sports")),
        SubCategory(subcategory_name="Running", category_id=categories.get("Sports")),
        SubCategory(subcategory_name="Outdoor", category_id=categories.get("Sports")),

        # Beauty
        SubCategory(subcategory_name="Makeup", category_id=categories.get("Beauty")),
        SubCategory(subcategory_name="Skincare", category_id=categories.get("Beauty")),
        SubCategory(subcategory_name="Haircare", category_id=categories.get("Beauty")),

        # Toys
        SubCategory(subcategory_name="Educational", category_id=categories.get("Toys")),
        SubCategory(subcategory_name="Action Figures", category_id=categories.get("Toys")),
        SubCategory(subcategory_name="Puzzles & Games", category_id=categories.get("Toys")),

        # Vehicles
        SubCategory(subcategory_name="Cars", category_id=categories.get("Vehicles")),
        SubCategory(subcategory_name="Motor Cycles", category_id=categories.get("Vehicles")),
        SubCategory(subcategory_name="Accessories", category_id=categories.get("Vehicles")),
    ]

    db.session.add_all(subcategories)
    db.session.commit()
    print("✅ Subcategories seeded successfully.")
