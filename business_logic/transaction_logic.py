from flask_jwt_extended import get_jwt_identity
from utils.helpers import can_act_on_user, is_admin
from utils.exceptions import AuthorizationException, NotFoundException, AppException
from services.transaction_service import transaction_service
from services.telegram_service import telegram_service
from models.transaction import Transaction
from models.user import User


def transfer_money_logic(data):
    current_user_id = int(get_jwt_identity())
    receiver_id = data['receiver_id']
    amount = data['amount']
    
    if not can_act_on_user(current_user_id):
        raise AuthorizationException()
    
    return transaction_service.transfer_money(
        current_user_id, receiver_id, amount, data.get('description', '')
    )

def get_user_balance_logic(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundException("User not found")
    
    return {
        'user_id': user.id,
        'name': user.name,
        'age': user.age,
        'balance': float(user.balance)
    }

def get_user_transactions_logic(user_id):
    current_user_id = int(get_jwt_identity())
    
    if user_id != current_user_id and not is_admin():
        raise AuthorizationException()
    
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    return transactions


def create_income_logic(data):
    current_user_id = int(get_jwt_identity())
    if not can_act_on_user(data.get('user_id', current_user_id)):
        raise AuthorizationException()
    
    transaction = transaction_service.create_transaction(
        data.get('user_id', current_user_id),
        data['amount'], 'credit', data.get('category', 'other'),
        data['title'], data.get('description', '')
    )
    
    try:
        telegram_service.send_income_notification(current_user_id, transaction.id)
    except AppException as e:
        print(f"Income Telegram notification failed: {e}")
    
    return transaction

def create_expense_logic(data):
    current_user_id = int(get_jwt_identity())
    if not can_act_on_user(data.get('user_id', current_user_id)):
        raise AuthorizationException()
    
    transaction = transaction_service.create_transaction(
        data.get('user_id', current_user_id),
        data['amount'], 'debit', data.get('category', 'other'),
        data['title'], data.get('description', '')
    )
    
    try:
        telegram_service.send_expense_notification(current_user_id, transaction.id)
    except AppException as e:
        print(f"Expense Telegram notification failed: {e}")
    
    return transaction