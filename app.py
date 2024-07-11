from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# MySQL Veritabanı bağlantı bilgileri
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://newuser:password@localhost/cartdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExpenseLog(db.Model):
    __tablename__ = 'ExpenseLog'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    products_id = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    if not data or 'user_id' not in data or 'products_id' not in data or 'total_amount' not in data or 'category' not in data:
        return jsonify({"error": "Invalid data"}), 400

    user_id = data['user_id']
    products_id = data['products_id']
    total_amount = data['total_amount']
    category = data['category']

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.balance < total_amount:
        return jsonify({"error": "Insufficient balance"}), 400

    user.balance -= total_amount

    new_expense = ExpenseLog(user_id=user_id, products_id=products_id, total_amount=total_amount, category=category)
    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "Expense added to log", "remaining_balance": user.balance}), 201

@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = ExpenseLog.query.all()
    result = []
    for expense in expenses:
        result.append({
            "id": expense.id,
            "user_id": expense.user_id,
            "products_id": expense.products_id,
            "total_amount": expense.total_amount,
            "category": expense.category,
            "created_at": expense.created_at
        })
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)