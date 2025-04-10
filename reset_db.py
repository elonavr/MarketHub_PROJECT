from flask import Flask
from app import db
import os
import shutil
from sqlalchemy.sql import text

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/MarketHub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def reset_database():
    with app.app_context():
        try:
            db.session.execute(text("DELETE FROM cart;"))
            db.session.execute(text("DELETE FROM order_details;"))
            db.session.execute(text("DELETE FROM orders;"))
            db.session.execute(text("DELETE FROM products;"))
            db.session.execute(text("DELETE FROM users;"))

            db.session.execute(text("ALTER SEQUENCE users_user_id_seq RESTART WITH 1;"))
            db.session.execute(text("ALTER SEQUENCE products_product_id_seq RESTART WITH 1;"))
            db.session.execute(text("ALTER SEQUENCE orders_order_id_seq RESTART WITH 1;"))

            db.session.commit()
            print(" Database reset successfully.")
        except Exception as e:
            db.session.rollback()
            print(f" Error resetting database: {e}")

def clear_sessions():
    session_dir = "C:\\Users\\elona\\Desktop\\MarketHub_PROJECT\\instance"

    if os.path.exists(session_dir):
        try:
            shutil.rmtree(session_dir)
            os.makedirs(session_dir)
            print(" Flask session data cleared.")
        except Exception as e:
            print(f" Error clearing session data: {e}")

if __name__ == "__main__":
    reset_database()
    clear_sessions()
    print("🎯 Reset process completed.")
