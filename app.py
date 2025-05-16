from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from model import db, preload_categories, User, Item, Category
from datetime import datetime
import os, csv
from io import StringIO
from flask import send_file
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from dotenv import load_dotenv
from forms import SignUpForm, SignInForm, EditProfileForm, TransactionForm, ImportCsvForm

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense-tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY")

csrf = CSRFProtect(app)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template("error.html", message=e.description), 400

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "signin"

with app.app_context():
    db.create_all()
    preload_categories()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    return jsonify({"error": "A database error occurred"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/")
def home():
    form = SignUpForm()
    return render_template("sign-up.html", form=form)

@app.route("/sign-in", methods=["GET", "POST"])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("transactions"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("sign-in.html", form=form)

@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists", "danger")
            return render_template("sign-up.html", form=form)
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created!", "success")
        return redirect(url_for("signin"))
    return render_template("sign-up.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("signin"))

@app.route("/transactions")
@login_required
def transactions():
    form = TransactionForm()
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    import_form = ImportCsvForm()
    return render_template("transactions.html", user=current_user, form=form, import_form=import_form)

@app.route("/add-transaction", methods=["POST"])
@login_required
def add_transaction_form():
    form = TransactionForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        tx_id = form.transaction_id.data
        if tx_id:
            # Editing existing transaction
            item = Item.query.filter_by(id=tx_id, user_id=current_user.id).first()
            if not item:
                flash("Transaction not found.", "danger")
                return redirect(url_for("transactions"))
        else:
            item = Item(user_id=current_user.id)

        item.description = form.description.data
        item.amount = form.amount.data
        item.category_id = form.category_id.data
        item.created_at = form.date.data

        db.session.add(item)
        db.session.commit()
        flash("Transaction saved successfully!", "success")
    else:
        flash("Validation failed. Check your form.", "danger")

    return redirect(url_for("transactions"))

@app.route("/delete-transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction_route(transaction_id):
    item = Item.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not item:
        flash("Transaction not found.", "danger")
    else:
        db.session.delete(item)
        db.session.commit()
        flash("Transaction deleted!", "success")

    return redirect(url_for("transactions"))

@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html", user=current_user)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        if form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash("Email already exists", "danger")
        else:
            current_user.name = form.name.data
            current_user.email = form.email.data
            if form.password.data:
                current_user.password = generate_password_hash(form.password.data)
            db.session.commit()
            flash("Profile updated!", "success")
            return redirect(url_for("edit_profile"))
    return render_template("edit_profile.html", form=form)

# ========== API ROUTES (for JS to fetch data) ==========

@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    items = Item.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {
            "id": item.id,
            "category": item.category.name,
            "category_id": item.category.id,
            "type": item.category.type,
            "amount": item.amount,
            "description": item.description,
            "date": item.created_at.strftime("%Y-%m-%d")
        }
        for item in items
    ])

@app.route("/api/categories")
@login_required
def get_categories():
    categories = Category.query.all()
    return jsonify([
        {"id": c.id, "name": c.name, "type": c.type, "icon": c.icon}
        for c in categories
    ])

from sqlalchemy import extract, func

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
    breakdown = {month: {"income": 0, "expense": 0} for month in range(1, 13)}
    for month, ttype, total in results:
        if ttype in breakdown[month]:
            breakdown[month][ttype] = float(total)
    return jsonify(breakdown)

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

@app.route("/import-csv", methods=["POST"])
@login_required
def import_csv():
    form = ImportCsvForm()
    if form.validate_on_submit():
        file = form.file.data
        try:
            stream = StringIO(file.stream.read().decode("utf-8"))
            reader = csv.DictReader(stream)
            for row in reader:
                category = Category.query.filter_by(name=row["Category"], type=row["Type"]).first()
                if not category:
                    continue
                item = Item(
                    user_id=current_user.id,
                    category_id=category.id,
                    description=row["Description"],
                    amount=float(row["Amount"]),
                    created_at=datetime.strptime(row["Date"], "%Y-%m-%d")
                )
                db.session.add(item)
            db.session.commit()
            flash("CSV imported successfully.", "success")
        except Exception as e:
            flash(f"Import failed: {str(e)}", "danger")
    else:
        flash("Invalid file submission.", "danger")
    return redirect(url_for("transactions"))

if __name__ == "__main__":
    app.run(debug=True)
