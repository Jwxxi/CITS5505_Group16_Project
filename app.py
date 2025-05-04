from flask import Flask, render_template, jsonify
from model import db, preload_categories
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense-tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Initialize the database tables and preload categories
with app.app_context():
    db.create_all()
    preload_categories()


@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    return jsonify({"error": "A database error occurred"}), 500


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/transactions")
def transactions():
    return render_template("transactions.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


if __name__ == "__main__":
    app.run(debug=True)
