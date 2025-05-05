from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)  # 'income' or 'expense'
    icon = db.Column(db.String, nullable=False)


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    description = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(), nullable=False
    )

    user = db.relationship("User", backref="items")
    category = db.relationship("Category", backref="items")


def preload_categories():
    """Preload default categories into the database."""
    default_categories = [
        # Income Categories
        {"name": "Salary & Wages", "type": "income", "icon": "fas fa-money-bill"},
        {"name": "Bonuses & Commissions", "type": "income", "icon": "fas fa-gift"},
        {
            "name": "Business or Freelance Income",
            "type": "income",
            "icon": "fas fa-briefcase",
        },
        {"name": "Rental & Property Income", "type": "income", "icon": "fas fa-home"},
        {"name": "Investment Income", "type": "income", "icon": "fas fa-chart-line"},
        {"name": "Other Income", "type": "income", "icon": "fas fa-coins"},
        # Expense Categories
        {"name": "Housing", "type": "expense", "icon": "fas fa-building"},
        {"name": "Utilities & Services", "type": "expense", "icon": "fas fa-lightbulb"},
        {"name": "Food & Groceries", "type": "expense", "icon": "fas fa-utensils"},
        {"name": "Transportation", "type": "expense", "icon": "fas fa-bus"},
        {"name": "Insurance", "type": "expense", "icon": "fas fa-shield-alt"},
        {"name": "Healthcare & Medical", "type": "expense", "icon": "fas fa-heartbeat"},
        {"name": "Debt Payments", "type": "expense", "icon": "fas fa-credit-card"},
        {
            "name": "Savings & Investments",
            "type": "expense",
            "icon": "fas fa-piggy-bank",
        },
        {"name": "Personal & Discretionary", "type": "expense", "icon": "fas fa-user"},
        {"name": "Entertainment & Leisure", "type": "expense", "icon": "fas fa-film"},
        {"name": "Education & Development", "type": "expense", "icon": "fas fa-book"},
        {
            "name": "Household Supplies & Maintenance",
            "type": "expense",
            "icon": "fas fa-tools",
        },
        {
            "name": "Taxes & Fees",
            "type": "expense",
            "icon": "fas fa-file-invoice-dollar",
        },
        {"name": "Miscellaneous", "type": "expense", "icon": "fas fa-ellipsis-h"},
    ]

    for category in default_categories:
        # Check if the category already exists
        existing = Category.query.filter_by(name=category["name"]).first()
        if not existing:
            new_category = Category(**category)
            db.session.add(new_category)
    db.session.commit()
