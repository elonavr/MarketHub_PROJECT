from app import db, app
from models.user_model import User
from models.product_model import Product
from models.cart_model import Cart
from models.favorite_model import Favorite
from models.order_model import Order, OrderDetail

with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")
