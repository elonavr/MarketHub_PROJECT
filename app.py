from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import db

# Flask app initialization
app = Flask(__name__, template_folder="frontend/templates")

app.secret_key = "your_secret_key"  # מפתח הצפנה לניהול session


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


@app.route("/")
def index():
    return render_template("index.html")

# login


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Retrieving the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password")

        # Query the database to find the user by username
        user = User.query.filter_by(username=username).first()

        # Check if user exists and if the password matches
        if user and check_password_hash(user.password_hash, password):
            # If valid, store user info in session
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["role"] = user.role

            # Redirect to the home page after successful login
            return redirect(url_for("index"))

        # If credentials are invalid, show an error message
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))  # Redirect back to the login page

    # If the request method is GET, render the login page
    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()  # מוחק את הנתונים של המשתמש המחובר
    return redirect(url_for("index"))

# register


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", error="Username already exists")

        # Create a new user with hashed password
        new_user = User(
            username=username,
            role=role
        )
        # Encrypt the password using the set_password method
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # After registration, redirect to the login page
        return redirect(url_for("login"))

    return render_template("register.html")

# מסלול להציג את כל המוצרים


@app.route('/products', methods=['GET'])
def products():
    if "user_id" not in session:
        flash("Please log in to view products.", "danger")
        return redirect(url_for("login"))

    if session["role"] == "supplier":
        # Retrieve only products added by the logged-in supplier
        products_list = Product.query.filter_by(
            supplier_id=session["user_id"]).all()
    else:
        # Retrieve all products for customers
        products_list = Product.query.all()

    return render_template('products.html', products=products_list)

# Form - Create a new product (for HTML form submission)
@app.route('/products/add_form', methods=['POST'])
def add_product_form():
    if "user_id" not in session or session["role"] not in ["supplier"]:
        flash("Only suppliers can add products.", "danger")
        return redirect(url_for("products"))

    product_name = request.form.get('product_name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock')
    category = request.form.get('category')

    try:
        stock = int(stock) if stock and stock.isdigit() else 1
    except ValueError:
        flash("Invalid stock value.", "danger")
        return redirect(url_for("products"))


    # יצירת מוצר חדש עם supplier_id
    new_product = Product(
        product_name=product_name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        supplier_id=session["user_id"]  # חשוב! משייך את המוצר למוכר
    )

    db.session.add(new_product)
    db.session.commit()

    flash("Product added successfully!", "success")
    return redirect(url_for('products'))  # לאחר הוספת המוצר, מפנה לדף המוצרים

# Add product to cart (via form submission)


@app.route('/cart/add_form', methods=['POST'])  # Endpoint חדש עבור הטופס
def add_to_cart_form():
    # קבלת נתונים מהטופס
    user_id = request.form.get('user_id')
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')

    product = Product.query.get(product_id)
    
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    if quantity > product.stock:
        flash(f"Only {product.stock} units available!", "danger")
        return redirect(url_for("products"))
    

    # testing if the user is a supplier
    user = User.query.get(user_id)
    if user and user.role == 'supplier':
        flash("Suppliers cannot add products to cart.", "danger")
        return redirect(url_for('products'))  # מחזיר את המשתמש לדף המוצרים

    # יצירת אובייקט Cart ויישום הנתונים
    cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)

    # הוספת המוצר לעגלה במסד הנתונים
    db.session.add(cart_item)
    db.session.commit()

    flash("Product added to cart successfully!", "success")
    return redirect(url_for('products'))  # מחזיר את המשתמש לדף המוצרים

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    cart_item = Cart.query.get(cart_id)

    if not cart_item:
        flash("Item not found in cart.", "danger")
        return redirect(url_for("view_cart"))

    db.session.delete(cart_item)
    db.session.commit()

    flash("Item removed from cart.", "success")
    return redirect(url_for("view_cart"))


@app.route('/order', methods=['POST'])
def create_order():
    user_id = request.form.get('user_id')

    # קבלת כל המוצרים מהעגלה עבור המשתמש
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        # אם אין מוצרים בעגלה
        return jsonify({'error': 'No items in cart'}), 400

    # יצירת הזמנה חדשה
    new_order = Order(user_id=user_id)
    db.session.add(new_order)
    db.session.commit()  # נשמור את ההזמנה במסד הנתונים

    # הוספת כל המוצרים לעסקה בטבלת ההזמנות
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.order_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.session.add(order_item)

    # נמחק את המוצרים מהעגלה לאחר ביצוע ההזמנה
    db.session.query(Cart).filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({'message': 'Order placed successfully', 'order_id': new_order.order_id}), 201


@app.route('/order/<int:order_id>', methods=['GET'])
def view_order(order_id):
    # שליפת ההזמנה על פי מזהה ההזמנה
    order = Order.query.get_or_404(order_id)

    # שליפת פרטי ההזמנה
    order_details = OrderDetail.query.filter_by(order_id=order_id).all()

    # סך ההזמנה (אם רוצים לחשב אותו)
    total_amount = sum(item.quantity * item.price for item in order_details)

    # שלח את הנתונים לדף HTML
    return render_template('order.html', order=order, order_details=order_details, total_amount=total_amount)


@app.route('/orders', methods=['GET'])
def view_orders():
    user_id = 1  # לדוגמה, זה יכול להיות מזהה המשתמש המחובר
    orders = Order.query.filter_by(user_id=user_id).all()
    return render_template('order_history.html', orders=orders)


@app.route('/products/update_stock', methods=['POST'])
def update_stock():
    if "user_id" not in session or session["role"] != "supplier":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("products"))

    product_id = request.form.get("product_id")
    action = request.form.get("action")

    product = Product.query.filter_by(product_id=product_id, supplier_id=session["user_id"]).first()

    if not product:
        flash("Product not found or not owned by you.", "danger")
        return redirect(url_for("products"))

    if action == "increase":
        product.stock += 1
    elif action == "decrease" and product.stock > 0:
        product.stock -= 1

    db.session.commit()
    flash("Stock updated successfully!", "success")
    return redirect(url_for("products"))



# -------------------------
# 🔹 CRUD for Products
# -------------------------

# Create a new product (via API request)
@app.route('/products/add', methods=['GET', 'POST'])
def add_product_api():
    if request.method == "POST":
        # Get form data
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        image_url = request.form.get('image_url', '')

        # Ensure the user is logged in as a supplier
        supplier_id = session.get("user_id")
        if not supplier_id:
            flash("Error: You must be logged in!", "danger")
            return redirect(url_for("add_product_api"))

        # Create new product
        new_product = Product(
            supplier_id=supplier_id,  # Ensure supplier ID is saved
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            image_url=image_url
        )

        # Save to database
        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for("products"))

    # If GET request, render the add_product.html page
    return render_template("add_product.html")


# -------------------------
# 🔹 CRUD for Cart
# -------------------------

# Add product to cart (via API request)
@app.route('/cart/add', methods=['POST'])  # Endpoint נפרד עבור ה-API
def add_to_cart_api():
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

        # avoiding add products to the cart by suppliers
    if user.role == 'supplier':
        return jsonify({'error': 'Suppliers cannot add products to cart'}), 403

    # הוספת המוצר לעגלה במסד הנתונים
    cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({'message': 'Product added to cart successfully'}), 201


# View the cart items for a specific user
@app.route('/cart', methods=['GET'])
def view_cart():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your cart.", "danger")
        return redirect(url_for("login"))

    cart_items = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.product_id).filter(Cart.user_id == user_id).all()
    
    total_amount = sum(cart.quantity * product.price for cart, product in cart_items)
        
    print("🔍 Debug - Cart Items:")
    for item in cart_items:
        print("Type of item:", type(item))
        print("Content of item:", item)


    
    return render_template("cart.html", cart_items=cart_items, total_amount=total_amount)
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
        # Default role is 'customer' if not provided
        role=data.get('role', 'customer')
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
    result = [{'user_id': u.user_id, 'username': u.username, 'role': u.role}
              for u in users]
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
    app.run(debug=True)  # http://127.0.0.1:5000/
