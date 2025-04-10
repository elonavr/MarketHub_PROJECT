# seed.py
from app import app
from db import db
from models.category_model import Category

with app.app_context():
    if Category.query.count() == 0:
        categories = [
            Category(category_name="Electronics"),
            Category(category_name="Fashion"),
            Category(category_name="Home & Garden"),
            Category(category_name="Toys"),
            Category(category_name="Sports"),
            Category(category_name="Beauty"),
        ]
        db.session.add_all(categories)
        db.session.commit()
        print("✅ Categories seeded successfully.")
    else:
        print("ℹ️ Categories already exist. Skipping seeding.")


from app import app
from db import db
from models.category_model import Category
from models.subcategory_model import SubCategory  

with app.app_context():
    if Category.query.count() == 0:
        categories_data = {
            "Electronics": ["Phones", "Computers", "TVs"],
            "Fashion": ["Men", "Women", "Accessories"],
            "Home & Garden": ["Furniture", "Kitchen", "Decor"],
            "Toys": ["Educational", "Action Figures", "Puzzles & Games"],
            "Sports": ["Gym", "Running", "Outdoor"],
            "Beauty": ["Makeup", "Skincare", "Haircare"],
        }

        all_categories = []
        all_subcategories = []

        for category_name, sub_list in categories_data.items():
            category = Category(category_name=category_name)
            db.session.add(category)
            db.session.flush()

            for sub_name in sub_list:
                subcategory = SubCategory(subcategory_name=sub_name, category_id=category.category_id)
                all_subcategories.append(subcategory)

            all_categories.append(category)

        db.session.add_all(all_subcategories)
        db.session.commit()
        print("✅ Categories and Subcategories seeded successfully.")
    else:
        print("ℹ️ Categories already exist. Skipping seeding.")
