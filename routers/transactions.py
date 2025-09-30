from flask import Blueprint
from utils.decorators import route
from validation.transaction_schema import (
    IncomeSchema, ExpenseSchema, TransferSchema, 
    ProfileSchema, SalarySchema
)
from business_logic.transaction_logic import (
    create_income_logic, create_expense_logic,
    transfer_money_logic, get_user_balance_logic,
    get_user_transactions_logic
)
from services.salary_service import salary_service

bp = Blueprint("transactions", __name__)

@route(
    bp, "/categories", 
    methods=["GET"]
)
def get_categories(validated_data):
    """Get available transaction categories"""
    return {
        'categories': [
            'salary', 'food', 'rent', 'transport', 
            'entertainment', 'healthcare', 'shopping', 
            'utilities', 'transfer', 'other'
        ]
    }

@route(
    bp, "/reports/category-summary", 
    methods=["GET"]
)
def get_category_summary(validated_data):
    """Get spending summary by category for current user"""
    from flask_jwt_extended import get_jwt_identity
    from sqlalchemy import func
    from models.transaction import Transaction
    
    user_id = int(get_jwt_identity())
    
    category_totals = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.entry_type == 'debit'  
    ).group_by(Transaction.category).all()
    
    return {
        'user_id': user_id,
        'summary': [
            {
                'category': category,
                'total_spent': float(total_amount),
                'transaction_count': transaction_count
            }
            for category, total_amount, transaction_count in category_totals
        ]
    }

@route(
    bp, "/reports/date-summary", 
    methods=["POST"]
)
def get_date_summary(validated_data):
    """Get transaction summary by date range"""
    from flask_jwt_extended import get_jwt_identity
    from sqlalchemy import func, Date
    from datetime import datetime
    from models.transaction import Transaction
    
    user_id = int(get_jwt_identity())
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.now().replace(day=1)
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()
    
    daily_totals = db.session.query(
        func.date(Transaction.created_at).label('transaction_date'),
        Transaction.entry_type,
        func.sum(Transaction.amount).label('daily_total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date
    ).group_by(
        func.date(Transaction.created_at),
        Transaction.entry_type
    ).all()
    
    return {
        'user_id': user_id,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'daily_summary': [
            {
                'date': date.strftime('%Y-%m-%d'),
                'entry_type': entry_type,
                'daily_total': float(daily_total)
            }
            for date, entry_type, daily_total in daily_totals
        ]
    }

@route(
    bp, "/reports/spending-analytics", 
    methods=["GET"]
)
def get_spending_analytics(validated_data):
    """Get comprehensive spending analytics"""
    from flask_jwt_extended import get_jwt_identity
    from sqlalchemy import func, extract
    from models.transaction import Transaction
    
    user_id = int(get_jwt_identity())
    
    monthly_spending = db.session.query(
        extract('year', Transaction.created_at).label('year'),
        extract('month', Transaction.created_at).label('month'),
        func.sum(Transaction.amount).label('monthly_total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.entry_type == 'debit'
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    top_categories = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('category_total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.entry_type == 'debit'
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).limit(5).all()
    
    return {
        'user_id': user_id,
        'monthly_trends': [
            {
                'year': int(year),
                'month': int(month),
                'total_spent': float(monthly_total)
            }
            for year, month, monthly_total in monthly_spending
        ],
        'top_categories': [
            {
                'category': category,
                'total_spent': float(category_total)
            }
            for category, category_total in top_categories
        ]
    }