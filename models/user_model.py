from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='customer')  # customer or supplier

    # Method to set the password (it will hash the password)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Method to check if the provided password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
