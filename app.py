from flask import Flask, render_template
from model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense-tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize the database tables
with app.app_context():
    db.create_all()

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
