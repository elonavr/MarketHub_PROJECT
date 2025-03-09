from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# כעת אנו מייבאים את המודלים אחרי שהגדרנו את `db`
from .user_model import User
from .product_model import Product
from .cart_model import Cart
from .favorite_model import Favorite
from .order_model import Order, OrderDetail

# חשיפת כל המודלים כאשר מייבאים `models`
__all__ = ["db", "User", "Product", "Cart", "Favorite", "Order", "OrderDetail"]
