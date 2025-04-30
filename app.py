from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# =======================
# Database Models
# =======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    expenses = db.relationship('Expense', backref='user', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# =======================
# User Loader
# =======================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =======================
# Routes
# =======================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('landing'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def landing():
    if request.method == 'POST':
        income = request.form.get('income')
        if income:
            session['income'] = float(income)
            flash('Income updated!', 'success')
            return redirect(url_for('landing'))

    selected_year = request.args.get('year')
    selected_month = request.args.get('month')
    search_query = request.args.get('search')

    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()

    if selected_year:
        expenses = [e for e in expenses if e.date.year == int(selected_year)]
    if selected_month:
        expenses = [e for e in expenses if e.date.strftime('%B') == selected_month]
    if search_query:
        expenses = [e for e in expenses if search_query.lower() in e.description.lower()]

    total_expense = sum(expense.amount for expense in expenses)
    monthly_income = session.get('income', 1000)

    all_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    years = sorted({expense.date.year for expense in all_expenses}, reverse=True)
    months = sorted({expense.date.strftime('%B') for expense in all_expenses})

    return render_template('landing.html',
                           expenses=expenses,
                           total_expense=total_expense,
                           monthly_income=monthly_income,
                           years=years,
                           months=months,
                           selected_year=int(selected_year) if selected_year else '',
                           selected_month=selected_month,
                           search_query=search_query)

@app.route('/analysis')
@login_required
def analysis():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    total_expense = sum(expense.amount for expense in expenses)
    monthly_income = session.get('income', 1000)

    monthly_totals = {}
    for expense in expenses:
        month = expense.date.strftime('%B')
        monthly_totals[month] = monthly_totals.get(month, 0) + expense.amount

    category_totals = {}
    for expense in expenses:
        category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount

    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_categories = sorted_categories[:3]

    highest_spend_month = max(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else ('None', 0)

    most_exp = max(expenses, key=lambda e: e.amount) if expenses else None

    trend_table = []
    month_names = list(monthly_totals.keys())
    for month in month_names:
        month_expenses = [e for e in expenses if e.date.strftime('%B') == month]
        top_cat = max(month_expenses, key=lambda e: e.amount).category if month_expenses else '-'
        trend_table.append({
            'month': month,
            'total': monthly_totals[month],
            'top_category': top_cat,
            'count': len(month_expenses)
        })

    return render_template('my_analysis.html',
                           total_expense=total_expense,
                           monthly_income=monthly_income,
                           balance=monthly_income - total_expense,
                           monthly_totals=monthly_totals,
                           category_totals=category_totals,
                           top_categories=top_categories,
                           highest_spend_month=highest_spend_month,
                           most_exp=most_exp,
                           trend_table=trend_table)

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    category = request.form['category']
    amount = float(request.form['amount'])
    description = request.form['description']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

    new_expense = Expense(category=category, amount=amount, description=description, date=date, user_id=current_user.id)
    db.session.add(new_expense)
    db.session.commit()

    flash('Expense added successfully!', 'success')
    return redirect(url_for('landing'))

@app.route('/delete_expense/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('landing'))

    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('landing'))

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('landing'))

    if request.method == 'POST':
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])
        expense.description = request.form['description']
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

        db.session.commit()
        flash('Expense updated.', 'success')
        return redirect(url_for('landing'))

    return render_template('edit.html', expense=expense)

# =======================
# Run
# =======================
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
