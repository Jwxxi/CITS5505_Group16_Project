import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from model import db, preload_categories, Item, Category, User
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import re
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense-tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_COOKIE_SECURE"] = True  # Use HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Prevent CSRF

db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"  # Redirect to sign-in page if not logged in


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Use Session.get() instead of Query.get()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("signin", message="Session expired. Please log in again."))


# Initialize the database tables and preload categories
with app.app_context():
    db.create_all()
    preload_categories()


@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    return jsonify({"error": "A database error occurred"}), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def home():
    return render_template("sign-up.html")


@app.route("/sign-in", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid email or password"}), 401

        login_user(user, remember=remember)
        return jsonify({"success": "Login successful"}), 200  # Return JSON response

    return render_template("sign-in.html")


@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate email format
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password strength
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*\W)[A-Za-z\d\W]{8,}$"
        if not re.match(password_regex, password):
            return (
                jsonify(
                    {
                        "error": "Password must be at least 8 characters long, include one letter, one number, and one special character."
                    }
                ),
                400,
            )

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Return success message
        return (
            jsonify(
                {"success": "Registration successful! Redirecting to Sign-In page..."}
            ),
            200,
        )

    return render_template("sign-up.html")


@app.route("/transactions")
@login_required
def transactions():
    return render_template("transactions.html")


@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("signin"))


@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    month = request.args.get("month")  # Optional query parameter

  
    query = Item.query.filter_by(user_id=current_user.id)

    if month:
        start_date = f"{month}-01"
        end_date = f"{month}-31"
        query = query.filter(Item.created_at.between(start_date, end_date))

    transactions = query.paginate(page=page, per_page=limit, error_out=False).items
   

    return jsonify(
        [
            {
                "id": t.id,
                "category": t.category.name,
                "icon": t.category.icon,
                "description": t.description,
                "amount": t.amount,
                "date": t.created_at.strftime("%Y-%m-%d"),
                "type": t.category.type,
            }
            for t in transactions
        ]
    )


@app.route("/api/transactions", methods=["POST"])
@login_required
def add_transaction():
    try:
        

        category_id = request.form.get("category_id")
        description = request.form.get("description")
        amount = request.form.get("amount")
        date = request.form.get("date")

       

        # Validate input
        if not category_id or not description or not amount or not date:
            return jsonify({"error": "All fields are required"}), 400

        try:
            amount = float(amount)
        except ValueError:
            return jsonify({"error": "Invalid amount"}), 400

        # Convert the date string to a datetime object
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD."}), 400

        # Validate that the category exists
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return jsonify({"error": "Invalid category"}), 400

        new_transaction = Item(
            user_id=current_user.id,
            category_id=category_id,
            description=description,
            amount=amount,
            created_at=parsed_date,  # Pass the datetime object here
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"success": "Transaction added successfully"}), 201
    except Exception as e:
     
        return jsonify({"error": "Failed to add transaction"}), 400


@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id):
    transaction = Item.query.filter_by(
        id=transaction_id, user_id=current_user.id
    ).first()
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"success": "Transaction deleted successfully"}), 200


@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    category_type = request.args.get("type")  # 'income' or 'expense'
    if category_type not in ["income", "expense"]:
        return jsonify({"error": "Invalid category type"}), 400

    categories = Category.query.filter_by(type=category_type).all()
    return jsonify(
        [{"id": c.id, "name": c.name, "icon": c.icon} for c in categories]
    )


if __name__ == "__main__":
    app.run(debug=True)
