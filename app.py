# Updated app.py with profile edit routing, flash messages, and dropdown support

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from model import db, preload_categories, User, Item, Category
from datetime import datetime
import os
import csv
from io import StringIO
from flask import Response
# Backend functionality for CSV Export and Import
from flask import send_file
import csv
from io import StringIO



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense-tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.urandom(24)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "signin"

# Create tables and preload categories
with app.app_context():
    db.create_all()
    preload_categories()

# =====================
# User Loader
# =====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================
# Error Handlers
# =====================
@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    return jsonify({"error": "A database error occurred"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# =====================
# Routes
# =====================
@app.route("/")
def home():
    return render_template("sign-up.html")

@app.route("/sign-in", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("transactions"))
        else:
            return render_template("sign-in.html", error="Invalid credentials")
    return render_template("sign-in.html")

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template("sign-up.html", error="Email already registered")

        new_user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("signin"))
    return render_template("sign-up.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("signin"))

@app.route("/transactions")
@login_required
def transactions():
    categories = Category.query.all()
    return render_template("transactions.html", user=current_user, categories=categories)

@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html", user=current_user)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if email != current_user.email and User.query.filter_by(email=email).first():
            flash("Email is already in use.", "danger")
        else:
            current_user.name = name
            current_user.email = email
            if password:
                current_user.password = generate_password_hash(password)
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("edit_profile"))

    return render_template("edit_profile.html", user=current_user)


# =====================
# API: Transactions
# =====================
@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    items = Item.query.filter_by(user_id=current_user.id).all()
    transactions = []
    for item in items:
        transactions.append({
            "id": item.id,
            "category": item.category.name,
            "category_id": item.category.id,
            "type": item.category.type,
            "amount": item.amount,
            "description": item.description,
            "date": item.created_at.strftime("%Y-%m-%d")
        })
    return jsonify(transactions)

@app.route("/api/transactions", methods=["POST"])
@login_required
def add_transaction():
    data = request.json
    category_id = data.get("category_id")
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Invalid category"}), 400

    try:
        date_str = data.get("date")
        created_at = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    item = Item(
        user_id=current_user.id,
        category_id=category.id,
        description=data.get("description"),
        amount=data.get("amount"),
        created_at=created_at
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Transaction added"}), 201

@app.route("/api/transactions/<int:transaction_id>", methods=["PUT"])
@login_required
def update_transaction(transaction_id):
    data = request.get_json()
    item = Item.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not item:
        return jsonify({"error": "Transaction not found"}), 404

    category_id = data.get("category_id")
    if category_id:
        category = Category.query.get(category_id)
        if category:
            item.category_id = category.id

    item.description = data.get("description", item.description)
    item.amount = data.get("amount", item.amount)
    try:
        if "date" in data:
            item.created_at = datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    db.session.commit()
    return jsonify({"message": "Transaction updated"})

@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id):
    item = Item.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not item:
        return jsonify({"error": "Transaction not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"})

@app.route("/api/categories")
@login_required
def get_categories():
    categories = Category.query.all()
    return jsonify([
        {"id": c.id, "name": c.name, "type": c.type, "icon": c.icon}
        for c in categories
    ])

from sqlalchemy import extract, func

# =====================
# API: Analysis - Category Breakdown
# =====================
@app.route("/api/analysis", methods=["GET"])
@login_required
def get_analysis_by_type():
    type_filter = request.args.get("type", "expense")
    results = (
        db.session.query(Category.name, func.sum(Item.amount))
        .join(Item.category)
        .filter(Item.user_id == current_user.id, Category.type == type_filter)
        .group_by(Category.name)
        .all()
    )
    data = {name: float(total) for name, total in results}
    return jsonify({"categories": data})

# =====================
# API: Analysis - Monthly Income vs Expense
# =====================
@app.route("/api/monthly-breakdown", methods=["GET"])
@login_required
def get_monthly_income_expense():
    results = (
        db.session.query(
            extract("month", Item.created_at).label("month"),
            Category.type,
            func.sum(Item.amount)
        )
        .join(Item.category)
        .filter(Item.user_id == current_user.id)
        .group_by("month", Category.type)
        .order_by("month")
        .all()
    )

    breakdown = {
        month: {"income": 0, "expense": 0}
        for month in range(1, 13)
    }

    for month, ttype, total in results:
        if ttype in breakdown[month]:
            breakdown[month][ttype] = float(total)

    return jsonify(breakdown)



# ==============================
# Export Transactions as CSV
# ==============================
@app.route("/api/export", methods=["GET"])
@login_required
def export_transactions():
    items = Item.query.filter_by(user_id=current_user.id).all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Date", "Category", "Type", "Description", "Amount"])

    for item in items:
        cw.writerow([
            item.created_at.strftime("%Y-%m-%d"),
            item.category.name,
            item.category.type,
            item.description,
            item.amount
        ])

    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="transactions.csv"
    )

# ==============================
# Import Transactions from CSV
# ==============================
@app.route("/api/import", methods=["POST"])
@login_required
def import_transactions():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".csv"):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        stream = StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        for row in reader:
            category = Category.query.filter_by(name=row["Category"], type=row["Type"]).first()
            if not category:
                continue  # Skip invalid categories

            item = Item(
                user_id=current_user.id,
                category_id=category.id,
                description=row["Description"],
                amount=float(row["Amount"]),
                created_at=datetime.strptime(row["Date"], "%Y-%m-%d")
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({"message": "Data imported successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
