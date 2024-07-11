from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class ExpenseLog(db.Model):
    __tablename__ = 'ExpenseLog'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    products_id = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables created successfully!")