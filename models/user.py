from extensions import db
from sqlalchemy import Numeric

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)
    role = db.Column(db.Enum('admin', 'user', name='user_roles'),
                     nullable=False, server_default='user')
    balance = db.Column(Numeric(10, 2), default=0.00)

    transactions = db.relationship('Transaction', backref='user', cascade="all, delete-orphan")