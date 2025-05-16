import random
from model import db, User, Category, Item
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app import app

def get_category(name, type_):
    return Category.query.filter_by(name=name, type=type_).first()

def seed_user(email, name, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
    return user

def seed_items_for_user(user, entries_per_month=3):
    income_cats = Category.query.filter_by(type="income").all()
    expense_cats = Category.query.filter_by(type="expense").all()
    today = datetime.today()
    start_year = today.year - 2  # 3 years including this year

    for year in range(start_year, today.year + 1):
        for month in range(1, 13):
            # Skip future months in the current year
            if year == today.year and month > today.month:
                continue
            for cat in income_cats:
                for entry in range(entries_per_month):
                    # Random day in month
                    day = random.randint(1, 28)
                    item_date = datetime(year, month, day)
                    amount = round(random.uniform(1000, 5000), 2)
                    item = Item(
                        user_id=user.id,
                        category_id=cat.id,
                        description=f"{cat.name} {year}-{month:02d} #{entry+1}",
                        amount=amount,
                        created_at=item_date
                    )
                    db.session.add(item)
            for cat in expense_cats:
                for entry in range(entries_per_month):
                    day = random.randint(1, 28)
                    item_date = datetime(year, month, day)
                    amount = round(random.uniform(50, 800), 2)
                    item = Item(
                        user_id=user.id,
                        category_id=cat.id,
                        description=f"{cat.name} {year}-{month:02d} #{entry+1}",
                        amount=amount,
                        created_at=item_date
                    )
                    db.session.add(item)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        user1 = seed_user("davema0522@gmail.com", "Dave Ma", "password123")
        user2 = seed_user("jaminma_0522@163.com", "Jamin Ma", "password123")
        seed_items_for_user(user1, entries_per_month=3)
        seed_items_for_user(user2, entries_per_month=3)
        print("Fake data seeded for both users, all categories, all months, last 3 years, multiple entries per month.")