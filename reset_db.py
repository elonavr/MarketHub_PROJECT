# we need to run on pwsh: python C:\Users\elona\Desktop\MarketHub_PROJECT\reset_db.py
from flask import Flask
from app import db
import os
import shutil
from sqlalchemy.sql import text  # נוסיף את text() כדי לטפל ב-RAW SQL

# יצירת אובייקט Flask לשימוש ב-SQLAlchemy
app = Flask(__name__)

# חיבור למסד הנתונים – ודא שזה תואם את ההגדרות שלך
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/MarketHub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# מחיקת כל הנתונים מהטבלאות מבלי למחוק את הטבלאות עצמן
def reset_database():
    with app.app_context():
        try:
            # מחיקת נתונים מכל הטבלאות
            db.session.execute(text("DELETE FROM cart;"))
            db.session.execute(text("DELETE FROM order_details;"))
            db.session.execute(text("DELETE FROM orders;"))
            db.session.execute(text("DELETE FROM products;"))
            db.session.execute(text("DELETE FROM users;"))  # מוחק את כל המשתמשים
            
            # מאפס את מוני ה-ID בטבלאות
            db.session.execute(text("ALTER SEQUENCE users_user_id_seq RESTART WITH 1;"))
            db.session.execute(text("ALTER SEQUENCE products_product_id_seq RESTART WITH 1;"))
            db.session.execute(text("ALTER SEQUENCE orders_order_id_seq RESTART WITH 1;"))

            db.session.commit()
            print("✅ Database reset successfully! All users and data deleted.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting database: {e}")


# מחיקת קבצי Session שנשמרו במערכת כדי לאלץ התנתקות של משתמשים
def clear_sessions():
    session_dir = "C:\\Users\\elona\\Desktop\\MarketHub_PROJECT\\instance"

    if os.path.exists(session_dir):
        try:
            shutil.rmtree(session_dir)  # מוחק את כל הקבצים בתיקייה
            os.makedirs(session_dir)  # יוצר מחדש את התיקייה כדי למנוע בעיות הרצה
            print("✅ Flask session data cleared!")
        except Exception as e:
            print(f"❌ Error clearing session data: {e}")

if __name__ == "__main__":
    reset_database()
    clear_sessions()
    print("🎯 Reset process completed successfully!")
