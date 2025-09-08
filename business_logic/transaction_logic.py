from extensions import db
from models.transaction import Transaction
from utils.helpers import can_act_on_user, is_admin
from flask_jwt_extended import get_jwt_identity

def create_transaction_logic(data):
    current_user_id = int(get_jwt_identity())
    target_user_id = data.get('user_id', current_user_id)
    if not can_act_on_user(target_user_id):
        return {"error": "Not authorized"}, 403

    new_transaction = Transaction(
        amount=data['amount'],
        description=data.get('description', ''),
        user_id=target_user_id
    )
    db.session.add(new_transaction)
    db.session.commit()
    return new_transaction

def get_transactions_logic():
    current_user_id = int(get_jwt_identity())
    if is_admin():
        return Transaction.query.all()
    return Transaction.query.filter_by(user_id=current_user_id).all()

def update_transaction_logic(transaction_id, data):
    txn = Transaction.query.get(transaction_id)
    if not txn:
        return {"error": "Transaction not found"}, 404
    if not can_act_on_user(txn.user_id):
        return {"error": "Not authorized"}, 403

    txn.amount = data.get('amount', txn.amount)
    txn.description = data.get('description', txn.description)
    db.session.commit()
    return txn

def delete_transaction_logic(transaction_id):
    txn = Transaction.query.get(transaction_id)
    if not txn:
        return {"error": "Transaction not found"}, 404
    if not can_act_on_user(txn.user_id):
        return {"error": "Not authorized"}, 403
    db.session.delete(txn)
    db.session.commit()
    return {"message": "Transaction deleted"}
