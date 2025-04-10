from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


# Flask app initialization
app = Flask(__name__, template_folder="frontend/templates",
            static_folder="frontend/static")

# Management encryption key session
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Database configuration for PostgreSQL
# connecting address to the db
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# Disables tracking of object changes to improve performance and reduce memory usage
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize the database
db.init_app(app)
# Enables database migrations, allowing schema changes without losing data
migrate = Migrate(app, db)


# Import models after initializing db

with app.app_context():
    from models.user_model import User
    from models.product_model import Product
    from models.favorite_model import Favorite
    from models.cart_model import Cart
    from models.order_model import Order, OrderDetail
    from models.category_model import Category
    from models.subcategory_model import SubCategory

    db.create_all()  # Creates all database tables if they do not already exist

    @app.context_processor
    def inject_categories():
        from models.category_model import Category
        return dict(categories=Category.query.all())


# -------------------------
#  HOME & STATIC PAGES
# -------------------------

# Home Page

@app.route("/")
def index():
    from models.product_model import Product
    products_list = Product.query.filter_by(is_available=True).all()
    return render_template("index.html", products=products_list, page_title="Welcome to MarketHub")


# show category


@app.route("/category/<int:category_id>")
def show_category(category_id):
    from models.category_model import Category
    from models.product_model import Product

    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(
        category_id=category.category_id, is_available=True).all()

    return render_template("category.html", category=category, products=products)


@app.route('/subcategories/<int:category_id>')
def get_subcategories(category_id):
    from models.subcategory_model import SubCategory
    subcategories = SubCategory.query.filter_by(category_id=category_id).all()
    return jsonify([
        {'id': sub.subcategory_id, 'name': sub.subcategory_name}
        for sub in subcategories
    ])


@app.route('/subcategory/<int:subcategory_id>')
def show_subcategory(subcategory_id):
    subcategory = SubCategory.query.get_or_404(subcategory_id)
    category = subcategory.category
    products = Product.query.filter_by(
        subcategory_id=subcategory_id, is_available=True).all()
    return render_template("subcategory.html", subcategory=subcategory, category=category, products=products)


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
            return render_template("register.html", error="Username already exists,try something else")

        # Create a new user with hashed password
        new_user = User(username=username, role=role)
        # Encrypt the password using the set_password method
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # After registration, redirect to the login page
        return redirect(url_for("login"))

    return render_template("register.html")


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
        if user and password and user.password_hash and check_password_hash(user.password_hash, password):
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

# login AJAX


@app.route("/login_ajax", methods=["POST"])
def login_ajax():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if password is None or password == "":
        return jsonify({"status": "ask_password"}), 200

    if check_password_hash(user.password_hash, password):
        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "Incorrect password"}), 401


@app.route('/account')
def account():
    if not session.get("user_id"):
        return redirect(url_for('login'))
    return render_template('account.html')


# Logout
@app.route("/logout")
def logout():
    session.clear()  # מוחק את הנתונים של המשתמש המחובר
    return redirect(url_for("index"))


# Products Page

@app.route('/my_products')
def my_products():
    if "user_id" not in session or session["role"] != "supplier":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    products = Product.query.filter_by(supplier_id=session["user_id"], is_available=True).all()

    return render_template('index.html', products=products,  page_title="My Products")

@app.route('/products')
def products():
    if "user_id" not in session:
        flash("Please log in to view products.", "danger")
        return redirect(url_for("login"))

    products_list = Product.query.filter_by(is_available=True).all()
    return render_template('index.html', products=products_list, page_title="All Products")


# Form - Create a new product (for HTML form submission)


@app.route('/products/add_form', methods=['POST'])
def add_product_form():
    if "user_id" not in session or session["role"] not in ["supplier"]:
        flash("Only suppliers can add products.", "danger")
        return redirect(url_for("products"))
    breakpoint()

    # Getting data from the form
    product_name = request.form.get('product_name')
    price = request.form.get('price')
    stock = request.form.get('stock')
    category_id = request.form.get('category_id')
    category = request.form.get('category')
    image_url = request.form.get('image_url')

# Validates that the stock value is a valid integer; if invalid, defaults to 1 and flashes an error message
    try:
        stock = int(stock) if stock and stock.isdigit() else 1
    except ValueError:
        flash("Invalid stock value.", "danger")
        return redirect(url_for("products"))

# Validates that the price value is a valid integer; if invalid, flashes an error message
    try:
        price = int(price)
    except (ValueError, TypeError):
        flash("Invalid price value.", "danger")
        return redirect(url_for("products"))

    # Creating new Product with supplier_id
    new_product = Product(
        product_name=product_name,
        price=price,
        stock=stock,
        image_url=image_url,
        category_id=category_id,
        supplier_id=session["user_id"]
    )

    db.session.add(new_product)  # update to the DB
    db.session.commit()

    flash("Product added successfully!", "success")
    return redirect(url_for('products'))

# Add product to cart (via form submission)


@app.route('/cart/add_form', methods=['POST'])
def add_to_cart_form():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to add items to your cart.", "danger")
        return redirect(url_for("login"))

    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')

    if not product_id or not quantity:
        flash("Invalid product or quantity.", "danger")
        return redirect(url_for("products"))

    # Attempt to convert quantity to an integer and ensure it is greater than zero
    try:
        quantity = int(quantity)
        if quantity <= 0:
            flash("Quantity must be greater than zero.", "danger")
            return redirect(url_for("products"))
    except ValueError:
        flash("Invalid quantity. Please enter a valid number.", "danger")
        return redirect(url_for("products"))

    # Check if the product exists in the database
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    # Ensure requested quantity does not exceed available stock
    if quantity > product.stock:
        flash(f"Only {product.stock} units available!", "danger")
        return redirect(url_for("products"))

    # Check if the user is a supplier (suppliers cannot add products to cart)
    user = User.query.get(user_id)
    if user and user.role == 'supplier':
        flash("Suppliers cannot add products to cart.", "danger")
        return redirect(url_for("products"))

    # Check if the product is already in the user's cart
    cart_item = Cart.query.filter_by(
        user_id=user_id, product_id=product_id).first()

    if cart_item:
        if cart_item.quantity + quantity > product.stock:
            flash(
                f"Adding {quantity} exceeds stock limit. Only {product.stock - cart_item.quantity} more can be added.", "danger")
            return redirect(url_for("products"))

        cart_item.quantity += quantity
    else:
        cart_item = Cart(
            user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    flash("Product added to cart successfully!", "success")
    return redirect(url_for("view_cart"))

# "Deleting" a product from a supplier's cart (Actually we're just hiding the product)


@app.route('/products/delete', methods=['POST'])
def delete_product():
    if "user_id" not in session or session["role"] != "supplier":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("products"))

    product_id = request.form.get("product_id")

    # Search for the product that belongs to the connected seller
    product = Product.query.filter_by(
        product_id=product_id, supplier_id=session["user_id"]).first()

    if not product:
        flash("Product not found or you do not have permission to delete it.", "danger")
        return redirect(url_for("products"))

    product.is_available = False
    db.session.commit()

    flash("Product was deleted successfully!", "success")
    return redirect(url_for("my_products"))

# Update cart quantity


@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to update your cart.", "danger")
        return redirect(url_for("login"))

    product_id = request.form.get("product_id")
    action = request.form.get("action")  # 'increase' or 'decrease'

    with app.app_context():
        cart_item = Cart.query.filter_by(
            user_id=user_id, product_id=product_id).first()
        product = Product.query.get(product_id)

        if not cart_item or not product:
            flash("Item not found in cart.", "danger")
            return redirect(url_for("view_cart"))

        if action == "increase":
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
            else:
                flash("No more stock available.", "warning")

        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                flash("Minimum quantity is 1. To remove, click 'Remove'.", "warning")

        db.session.commit()

    return redirect(url_for("view_cart"))


#  Remove a product from the user's shopping cart


@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():

    product_id = request.form.get('product_id')
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to modify your cart.", "danger")
        return redirect(url_for("login"))

    # Delete product based on matched uesr_id & product_id
    db.session.query(Cart).filter_by(
        user_id=user_id, product_id=product_id).delete()
    db.session.commit()

    flash("Product removed from cart.", "success")
    return redirect(url_for("view_cart"))

#  Create a new order from the shopping cart


@app.route('/order', methods=['POST'])
def create_order():
    # Retrieve the user ID from the form submission
    user_id = request.form.get('user_id')

    # Fetch all cart items for the given user
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    # If the cart is empty, return an error response
    if not cart_items:
        return jsonify({'error': 'No items in cart'}), 400

    # Create a new order entry for the user
    new_order = Order(user_id=user_id)
    db.session.add(new_order)
    db.session.commit()  # Save to database

    #  Add each cart item to the Order Details table
    for item in cart_items:
        order_detail = OrderDetail(
            order_id=new_order.order_id, product_id=item.product_id, quantity=item.quantity)
        db.session.add(order_detail)

    #  Remove all cart items for the user after placing the order
    db.session.query(Cart).filter_by(user_id=user_id).delete()
    db.session.commit()  # Save changes to reflect the cleared cart

    #  Return a success message with the new order ID
    # HTTP 201 = Created
    return jsonify({'message': 'Order placed successfully', 'order_id': new_order.order_id}), 201


@app.route('/order/<int:order_id>', methods=['GET'])
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    order_details = OrderDetail.query.filter_by(order_id=order_id).all()
    total_amount = sum(detail.quantity *
                       detail.price for detail in order_details)

    # loads the order details page and provides all necessary data to display
    return render_template('order.html', order=order, order_details=order_details, total_amount=total_amount)


@app.route('/orders', methods=['GET'])
def view_orders():
    # Ensure the user is logged in before viewing orders
    if "user_id" not in session:
        flash("Please log in to view your orders.", "danger")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user_role = session["role"]

    # If the user is a customer, show all their orders
    if user_role == "customer":
        orders = Order.query.filter_by(user_id=user_id).all()
        return render_template('order_history.html', orders=orders)

    # If the user is a supplier, show only orders containing their products
    elif user_role == "supplier":
        supplier_orders = db.session.query(OrderDetail, Order, Product).join(
            Order, OrderDetail.order_id == Order.order_id
        ).join(
            Product, OrderDetail.product_id == Product.product_id
        ).filter(
            Product.supplier_id == user_id
        ).all()

        #  If no orders are found, show a warning message
        if not supplier_orders:
            flash("No orders found for your products.", "warning")

        #  Organizing the data: grouping orders and their corresponding order details
        supplier_order_dict = {}
        for order_detail, order, product in supplier_orders:
            if order.order_id not in supplier_order_dict:
                supplier_order_dict[order.order_id] = {
                    "order": order,
                    "order_details": []
                }
            supplier_order_dict[order.order_id]["order_details"].append(
                order_detail)

        return render_template("supplier_orders.html", supplier_orders=supplier_order_dict.values())

    else:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("index"))


@app.route('/supplier/orders')
def view_supplier_orders():
    if "user_id" not in session or session["role"] != "supplier":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("index"))

    supplier_id = session["user_id"]

    supplier_orders = db.session.query(OrderDetail, Order, Product).join(Order, OrderDetail.order_id == Order.order_id).join(
        Product, OrderDetail.product_id == Product.product_id).filter(Product.supplier_id == supplier_id).all()

    return render_template("supplier_orders.html", supplier_orders=supplier_orders)


@app.route('/products/update_stock', methods=['POST'])
def update_stock():
    if "user_id" not in session or session["role"] != "supplier":
        flash("Unauthorized action.", "danger")
        return redirect(url_for("products"))

    product_id = request.form.get("product_id")
    action = request.form.get("action")

    product = Product.query.filter_by(
        product_id=product_id, supplier_id=session["user_id"]).first()

    if not product:
        flash("Product not found or not owned by you.", "danger")
        return redirect(url_for("products"))

    if action == "increase":
        product.stock += 1
    elif action == "decrease" and product.stock > 0:
        product.stock -= 1

    db.session.commit()
    flash("Stock updated successfully!", "success")
    return redirect(url_for("my_products"))


@app.route('/checkout', methods=['GET'])
def checkout():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to proceed with checkout.", "danger")
        return redirect(url_for("login"))

    cart_items = db.session.query(Cart, Product).join(
        Product, Cart.product_id == Product.product_id).filter(Cart.user_id == user_id).all()

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))

    total_amount = sum(cart.quantity * product.price for cart,
                       product in cart_items)

    return render_template("checkout.html", cart_items=cart_items, total_amount=total_amount)


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to confirm your order.", "danger")
        return redirect(url_for("login"))

    cart_items = db.session.query(Cart, Product).join(
        Product, Cart.product_id == Product.product_id).filter(Cart.user_id == user_id).all()

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))

    new_order = Order(user_id=user_id, total_amount=0,
                      status="paid", created_at=datetime.utcnow())
    db.session.add(new_order)
    db.session.flush() 

    total_amount = 0

    #   Create records for purchased items
    for cart, product in cart_items:
        if cart.quantity > product.stock:
            flash(f"Insufficient stock for {product.product_name}.", "danger")
            return redirect(url_for("checkout"))

        # Inventory update
        product.stock -= cart.quantity

        # Adding the item to the table OrderDetails
        order_detail = OrderDetail(
            order_id=new_order.order_id,
            product_id=product.product_id,
            quantity=cart.quantity,
            price=product.price,
            total_price=cart.quantity * product.price
        )
        db.session.add(order_detail)

        total_amount += cart.quantity * product.price

    # Updating the order amount after calculating the total amount
    new_order.total_amount = total_amount

    # Clearing the user's cart
    Cart.query.filter_by(user_id=user_id).delete()

    db.session.commit()

    flash("Your order has been successfully placed!", "success")
    return redirect(url_for("order_confirmation"))


@app.route('/order-confirmation', methods=['GET'])
def order_confirmation():
    return render_template("order_confirmation.html")

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
        category_id = request.form.get("category_id")
        subcategory_id = request.form.get("subcategory_id")
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
            category_id=category_id,
            subcategory_id=subcategory_id,
            image_url=image_url
        )

        # Save to database
        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for("products"))

    else:
        from models.category_model import Category
        categories = Category.query.all()
        return render_template("add_product.html", categories=categories)


@app.route('/search')
def search():
    # Make sure this import is within app context
    from models.product_model import Product
    # get the query from URL param "?q="
    query = request.args.get('q', '').strip()
    results = []
    error = None

    if query:
        try:
            # ilike => case-insensitive partial matching
            # Use OR (|) to search both product_name AND description
            results = Product.query.filter(
                (
                    Product.product_name.ilike(f'%{query}%') |
                    Product.description.ilike(f'%{query}%')
                ) & (Product.is_available == True)
            ).all()
        except Exception as e:
            error = f"An error occurred while searching: {str(e)}"

    return render_template('search_results.html', query=query, results=results, error=error)


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

    # Adding the product to the cart in the database
    cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({'message': 'Product added to cart successfully'}), 201


# View the cart items for a specific user
@app.route('/cart', methods=['GET'])
def view_cart():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    cart_items = db.session.query(Cart, Product).join(
        Product, Cart.product_id == Product.product_id).filter(Cart.user_id == user_id).all()

    # Grouping products by product name
    grouped_cart = []

    for cart, product in cart_items:
        grouped_cart.append({
            'product_name': product.product_name,
            'quantity': cart.quantity,
            'price': product.price,
            'total': cart.quantity * product.price,
            'product_id': product.product_id  # נוסיף את ה-ID כדי לאפשר הסרה
        })

    total_amount = sum(cart.quantity * product.price for cart,
                       product in cart_items)

    return render_template("cart.html", cart_items=grouped_cart, total_amount=total_amount)
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

        return jsonify({'message': 'User updated successfully', 'redirect': '/my_products'}), 200

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


#  Running the Server

if __name__ == "__main__":
    app.run(debug=True)  # http://127.0.0.1:5000/
