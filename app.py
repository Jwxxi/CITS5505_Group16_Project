from flask import Flask, render_template, jsonify, request, redirect, url_for
from model import db, preload_categories, Item, Category
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def home():
    return render_template("sign-up.html")


@app.route("/sign-in")
def signin():
    return render_template("sign-in.html")


@app.route("/sign-up")
def signup():
    return render_template("sign-up.html")


@app.route("/transactions")
def transactions():
    return render_template("transactions.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/logout")
def logout():
    # Add logout logic here
    return redirect(url_for("login"))


# Add api endpoints below

if __name__ == "__main__":
    app.run(debug=True)
