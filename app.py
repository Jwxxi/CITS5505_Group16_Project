# Updated app.py with profile edit routing, flash messages, and dropdown support

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from model import db, preload_categories, User, Item, Category, SharedAnalysis
from datetime import datetime, date
import os
import csv
from io import StringIO
from flask import Response
import json
import traceback
from flask_wtf.csrf import CSRFProtect

# Backend functionality for CSV Export and Import
from flask import send_file
import csv
from io import StringIO


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense-tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.urandom(24)
csrf = CSRFProtect(app)

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
            return render_template(
                "sign-in.html", error="Incorrect email or password. Please try again."
            )
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

        new_user = User(
            name=name, email=email, password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        # Show success message on sign-up page, then auto-redirect
        return render_template(
            "sign-up.html",
            success="Sign up successful! Redirecting to sign in...",
            redirect_to_signin=True,
        )
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
    return render_template(
        "transactions.html", user=current_user, categories=categories
    )


@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html", current_date=date.today().isoformat(), current_user_email=current_user.email)


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
        transactions.append(
            {
                "id": item.id,
                "category": item.category.name,
                "category_id": item.category.id,
                "type": item.category.type,
                "amount": item.amount,
                "description": item.description,
                "date": item.created_at.strftime("%Y-%m-%d"),
            }
        )
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
        created_at = (
            datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
        )
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    item = Item(
        user_id=current_user.id,
        category_id=category.id,
        description=data.get("description"),
        amount=data.get("amount"),
        created_at=created_at,
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
    return jsonify(
        [
            {"id": c.id, "name": c.name, "type": c.type, "icon": c.icon}
            for c in categories
        ]
    )


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
            func.sum(Item.amount),
        )
        .join(Item.category)
        .filter(Item.user_id == current_user.id)
        .group_by("month", Category.type)
        .order_by("month")
        .all()
    )

    breakdown = {month: {"income": 0, "expense": 0} for month in range(1, 13)}

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
        cw.writerow(
            [
                item.created_at.strftime("%Y-%m-%d"),
                item.category.name,
                item.category.type,
                item.description,
                item.amount,
            ]
        )

    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="transactions.csv",
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
            category = Category.query.filter_by(
                name=row["Category"], type=row["Type"]
            ).first()
            if not category:
                continue  # Skip invalid categories

            item = Item(
                user_id=current_user.id,
                category_id=category.id,
                description=row["Description"],
                amount=float(row["Amount"]),
                created_at=datetime.strptime(row["Date"], "%Y-%m-%d"),
            )
            db.session.add(item)
        db.session.commit()
        return jsonify({"message": "Data imported successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# API: Share Analysis
# ==============================
@app.route("/api/share-analysis", methods=["POST"])
@login_required
def share_analysis():
    try:
        data = request.json
        recipient_email = data.get("recipient_email")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        data_type = data.get("data_type")

        # Validate required fields
        if not all([recipient_email, start_date, end_date, data_type]):
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        # Find recipient user
        recipient = User.query.filter_by(email=recipient_email).first()
        if not recipient:
            return jsonify({"success": False, "message": "Recipient not found."}), 404

        # Query items for the current user in the date range
        items_query = Item.query.filter(
            Item.user_id == current_user.id,
            Item.created_at >= datetime.strptime(start_date, "%Y-%m-%d"),
            Item.created_at <= datetime.strptime(end_date, "%Y-%m-%d"),
        )

        # Prepare snapshot
        snapshot = {}
        if data_type in ("expense", "both"):
            expenses = [item for item in items_query if item.category.type == "expense"]
            total_expense = sum(item.amount for item in expenses)
            expense_dist = {}
            for item in expenses:
                cat = item.category.name
                expense_dist[cat] = expense_dist.get(cat, 0) + item.amount
            # Convert to percentages with two decimal places
            expense_percent = {
                cat: round((amt / total_expense) * 100, 2)
                for cat, amt in expense_dist.items()
            } if total_expense > 0 else {}
            snapshot["expense"] = expense_percent

        if data_type in ("income", "both"):
            incomes = [item for item in items_query if item.category.type == "income"]
            total_income = sum(item.amount for item in incomes)
            income_dist = {}
            for item in incomes:
                cat = item.category.name
                income_dist[cat] = income_dist.get(cat, 0) + item.amount
            # Convert to percentages with two decimal places
            income_percent = {
                cat: round((amt / total_income) * 100, 2)
                for cat, amt in income_dist.items()
            } if total_income > 0 else {}
            snapshot["income"] = income_percent

        # Convert date strings to Python date objects
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Store snapshot as JSON
        shared = SharedAnalysis(
            sharer_id=current_user.id,
            recipient_id=recipient.id,
            start_date=start_date_obj,
            end_date=end_date_obj,
            data_type=data_type,
            snapshot_json=json.dumps(snapshot),
        )
        db.session.add(shared)
        db.session.commit()

        return jsonify({"success": True, "message": "Analysis shared successfully."})
    except Exception as e:
        print("Error in /api/share-analysis:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Internal server error."}), 500


@app.route("/shared-inbox")
@login_required
def shared_inbox():
    shared_items = SharedAnalysis.query.filter_by(recipient_id=current_user.id).order_by(SharedAnalysis.shared_at.desc()).all()
    # Parse snapshot_json for each item
    for item in shared_items:
        item.snapshot = json.loads(item.snapshot_json)
    return render_template("shared-inbox.html", shared_items=shared_items)


@app.route("/api/check-email", methods=["POST"])
@login_required
def check_email():
    data = request.json
    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})


@app.route("/api/check-items-exist", methods=["POST"])
@login_required
def check_items_exist():
    data = request.json
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    data_type = data.get("data_type")  # 'income', 'expense', or 'both'

    from datetime import datetime

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    query = Item.query.filter(
        Item.user_id == current_user.id,
        Item.created_at >= start_date_obj,
        Item.created_at <= end_date_obj
    )

    if data_type != "both":
        # Join with Category to filter by type
        query = query.join(Category).filter(Category.type == data_type)

    count = query.count()
    return jsonify({"count": count})


if __name__ == "__main__":
    app.run(debug=True)
