import unittest
import json
import os
from datetime import datetime
from app import app, db
from model import User, Category, Item
from werkzeug.security import generate_password_hash
from io import BytesIO


class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        # Configure test environment
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test-expense-tracker.db"
        app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF protection for testing
        self.app = app.test_client()
        
        # Create test database and tables
        with app.app_context():
            db.create_all()
            
            # Create test user
            test_user = User(
                name="Test User",
                email="test@example.com",
                password=generate_password_hash("password123")
            )
            db.session.add(test_user)
            
            # Create test categories
            income_category = Category(
                name="Test Income",
                type="income",
                icon="fas fa-money-bill"
            )
            expense_category = Category(
                name="Test Expense",
                type="expense",
                icon="fas fa-shopping-cart"
            )
            db.session.add(income_category)
            db.session.add(expense_category)
            db.session.commit()
            
            # Save test data IDs
            self.user_id = test_user.id
            self.income_category_id = income_category.id
            self.expense_category_id = expense_category.id
    
    def tearDown(self):
        # Clean up test database
        with app.app_context():
            db.session.remove()
            db.drop_all()
        # Delete test database file
        if os.path.exists("test-expense-tracker.db"):
            os.remove("test-expense-tracker.db")
    
    def login(self, email="test@example.com", password="password123"):
        # Helper method: login test user
        return self.app.post(
            "/sign-in",
            data=dict(email=email, password=password),
            follow_redirects=True
        )
    
    def logout(self):
        # Helper method: logout
        return self.app.get("/logout", follow_redirects=True)
    
    # Test user authentication related functions
    def test_home_page(self):
        # Test homepage access
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
    
    def test_signup(self):
        # Test user registration
        response = self.app.post(
            "/sign-up",
            data=dict(
                name="New User",
                email="new@example.com",
                password="newpassword123"
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # Verify if user is created successfully
        with app.app_context():
            user = User.query.filter_by(email="new@example.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, "New User")
    
    def test_login_logout(self):
        # Test login functionality
        response = self.login()
        self.assertEqual(response.status_code, 200)
        
        # Test logout functionality
        response = self.logout()
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_login(self):
        # Test invalid login
        response = self.app.post(
            "/sign-in",
            data=dict(email="wrong@example.com", password="wrongpassword"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Incorrect email or password", response.data)
    
    # Test transaction management API
    def test_get_transactions(self):
        # Login
        self.login()
        
        # Test getting transaction list
        response = self.app.get("/api/transactions")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_add_transaction(self):
        # Login
        self.login()
        
        # Add transaction
        transaction_data = {
            "category_id": self.income_category_id,
            "description": "Test Income",
            "amount": 1000.0,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        response = self.app.post(
            "/api/transactions",
            json=transaction_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify if transaction is added successfully
        with app.app_context():
            item = Item.query.filter_by(user_id=self.user_id).first()
            self.assertIsNotNone(item)
            self.assertEqual(item.description, "Test Income")
            self.assertEqual(item.amount, 1000.0)
    
    def test_update_transaction(self):
        # Login
        self.login()
        
        # First add a transaction
        with app.app_context():
            item = Item(
                user_id=self.user_id,
                category_id=self.income_category_id,
                description="Original Description",
                amount=500.0,
                created_at=datetime.now()
            )
            db.session.add(item)
            db.session.commit()
            transaction_id = item.id
        
        # Update transaction
        update_data = {
            "description": "Updated Description",
            "amount": 600.0
        }
        response = self.app.put(
            f"/api/transactions/{transaction_id}",
            json=update_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify if update is successful
        with app.app_context():
            updated_item = Item.query.get(transaction_id)
            self.assertEqual(updated_item.description, "Updated Description")
            self.assertEqual(updated_item.amount, 600.0)
    
    def test_delete_transaction(self):
        # Login
        self.login()
        
        # First add a transaction
        with app.app_context():
            item = Item(
                user_id=self.user_id,
                category_id=self.expense_category_id,
                description="To Be Deleted",
                amount=300.0,
                created_at=datetime.now()
            )
            db.session.add(item)
            db.session.commit()
            transaction_id = item.id
        
        # Delete transaction
        response = self.app.delete(f"/api/transactions/{transaction_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify if deletion is successful
        with app.app_context():
            deleted_item = Item.query.get(transaction_id)
            self.assertIsNone(deleted_item)
    
    # Test analysis functionality
    def test_get_analysis(self):
        # Login
        self.login()
        
        # Add test transaction data
        with app.app_context():
            # Add income
            income_item = Item(
                user_id=self.user_id,
                category_id=self.income_category_id,
                description="Test Income",
                amount=1000.0,
                created_at=datetime.now()
            )
            # Add expense
            expense_item = Item(
                user_id=self.user_id,
                category_id=self.expense_category_id,
                description="Test Expense",
                amount=500.0,
                created_at=datetime.now()
            )
            db.session.add(income_item)
            db.session.add(expense_item)
            db.session.commit()
        
        # Test income analysis
        response = self.app.get("/api/analysis?type=income")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("categories", data)
        self.assertIn("Test Income", data["categories"])
        self.assertEqual(data["categories"]["Test Income"], 1000.0)
        
        # Test expense analysis
        response = self.app.get("/api/analysis?type=expense")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("categories", data)
        self.assertIn("Test Expense", data["categories"])
        self.assertEqual(data["categories"]["Test Expense"], 500.0)
    
    def test_monthly_breakdown(self):
        # Login
        self.login()
        
        # Add test transaction data
        with app.app_context():
            # Add income and expense
            income_item = Item(
                user_id=self.user_id,
                category_id=self.income_category_id,
                description="Monthly Income",
                amount=2000.0,
                created_at=datetime.now()
            )
            expense_item = Item(
                user_id=self.user_id,
                category_id=self.expense_category_id,
                description="Monthly Expense",
                amount=1000.0,
                created_at=datetime.now()
            )
            db.session.add(income_item)
            db.session.add(expense_item)
            db.session.commit()
        
        # Test monthly income/expense analysis
        response = self.app.get("/api/monthly-breakdown")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Get current month
        current_month = str(datetime.now().month)
        
        # Verify current month data
        self.assertIn(current_month, data)
        month_data = data[current_month]
        self.assertEqual(month_data["income"], 2000.0)
        self.assertEqual(month_data["expense"], 1000.0)
    
    # Test CSV import/export functionality
    def test_export_transactions(self):
        # Login
        self.login()
        
        # Add test transaction data
        with app.app_context():
            item = Item(
                user_id=self.user_id,
                category_id=self.income_category_id,
                description="Export Test",
                amount=1500.0,
                created_at=datetime.now()
            )
            db.session.add(item)
            db.session.commit()
        
        # Test export functionality
        response = self.app.get("/api/export")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn("attachment", response.headers["Content-Disposition"])
    
    def test_import_transactions(self):
        # Login
        self.login()
        
        # Create test CSV data
        csv_data = "Date,Category,Type,Description,Amount\n"
        csv_data += f"{datetime.now().strftime('%Y-%m-%d')},Test Income,income,Import Test,2500.0"
        
        # Test import functionality
        response = self.app.post(
            "/api/import",
            data={
                "file": (BytesIO(csv_data.encode()), "transactions.csv")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify if import is successful
        with app.app_context():
            imported_item = Item.query.filter_by(description="Import Test").first()
            self.assertIsNotNone(imported_item)
            self.assertEqual(imported_item.amount, 2500.0)
    
    # Test user profile editing functionality
    def test_edit_profile(self):
        # Login
        self.login()
        
        # Test getting edit page
        response = self.app.get("/profile")
        self.assertEqual(response.status_code, 200)
        
        # Test updating user profile
        response = self.app.post(
            "/profile",
            data=dict(
                name="Updated Name",
                email="test@example.com",  # Keep the same email
                password="newpassword456"
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify if update is successful
        with app.app_context():
            updated_user = User.query.get(self.user_id)
            self.assertEqual(updated_user.name, "Updated Name")


if __name__ == "__main__":
    unittest.main()