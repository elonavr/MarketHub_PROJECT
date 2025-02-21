from flask import Flask, request, jsonify, render_template, redirect, url_for
from db import db

# Flask app initialization
app = Flask(__name__)

# Database configuration for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/MarketHub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Import models after initializing db
with app.app_context():
    from models.user_model import User
    from models.product_model import Product
    from models.favorite_model import Favorite
    from models.cart_model import Cart
    from models.order_model import Order

# -------------------------
# 🔹 HOME & STATIC PAGES
# -------------------------

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Products Page (Display all products)
@app.route('/products', methods=['GET'])
def products():
    products_list = Product.query.all()
    return render_template('products.html', products=products_list)

# -------------------------
# 🔹 CRUD for Products
# -------------------------

# Create a new product (via API request)
@app.route('/products/add', methods=['POST'])
def add_product():
    data = request.get_json()  # Get JSON data from the request

    # Validate the input data
    if not data or 'supplier_id' not in data or 'product_name' not in data or 'price' not in data:
        return jsonify({'error': 'supplier_id, product_name, and price are required'}), 400

    # Create a new product
    new_product = Product(
        supplier_id=data['supplier_id'],
        product_name=data['product_name'],
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product created successfully'}), 201


# -------------------------
# 🔹 CRUD for Cart
# -------------------------

# Add product to cart
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json

    # Validate if the data contains the necessary fields
    if not data or 'user_id' not in data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'user_id, product_id, and quantity are required'}), 400

    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']

    # Check if user and product exist (optional, but safer)
    user = User.query.get(user_id)
    product = Product.query.get(product_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        

    # Add to cart
    cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({'message': 'Product added to cart successfully'}), 201

# View the cart items for a specific user
@app.route('/cart/<int:user_id>', methods=['GET'])
def view_cart(user_id):
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    result = [{'product_id': item.product_id, 'quantity': item.quantity} for item in cart_items]
    return jsonify(result), 200

# -------------------------
# 🔹 CRUD for Users (API)
# -------------------------

# Create a new user (API)
@app.route('/users', methods=['POST'])
def create_user():
    # Safely retrieve JSON data from the request
    data = request.get_json()

    # Validate if all required fields are present
    if not data or 'username' not in data or 'password' not in data or 'role' not in data:
        return jsonify({'error': 'username, password, and role are required'}), 400

    # Check if the username already exists in the database
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    # Create a new user with the provided data
    new_user = User(
        username=data['username'],
        role=data.get('role', 'customer')  # Default role is 'customer' if not provided
    )
    new_user.set_password(data['password'])  # Securely hash the password

    # Add the new user to the database and commit the changes
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{'user_id': u.user_id, 'username': u.username, 'role': u.role} for u in users]
    return jsonify(result), 200

# Get user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role
        }), 200
    return jsonify({'error': 'User not found'}), 404

# Update user details
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = User.query.get(user_id)

    if user:
        if 'username' in data:
            user.username = data['username']
        if 'password' in data:
            user.set_password(data['password'])
        if 'role' in data:
            user.role = data['role']

        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200

    return jsonify({'error': 'User not found'}), 404

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

# -------------------------
# 🔥 Running the Server
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

