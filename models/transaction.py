from extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    entry_type = db.Column(db.Enum('credit', 'debit', name='entry_types'), nullable=False)
    category = db.Column(db.Enum('salary', 'transfer', 'payment', 'expense', 'income', name='transaction_categories'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='positive_amount'),
    )