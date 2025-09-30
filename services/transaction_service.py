from extensions import db
from models.transaction import Transaction
from models.user import User
from utils.exceptions import ValidationException, AppNotFoundException
from services.telegram_service import telegram_service

class TransactionService:
    @staticmethod
    def create_transaction(user_id, amount, entry_type, category, title, description="", related_user_id=None):
        """Create transaction and update user balance"""
        user = User.query.get(user_id)
        if not user:
            raise AppNotFoundException("User not found")
        
        transaction = Transaction(
            amount=amount,
            entry_type=entry_type,
            category=category,
            title=title,
            description=description,
            user_id=user_id,
            related_user_id=related_user_id
        )
        
        if entry_type == 'credit':
            user.balance += amount
        elif entry_type == 'debit':
            if user.balance < amount:
                raise ValidationException("Insufficient balance")
            user.balance -= amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return transaction
    
    @staticmethod
    def transfer_money(sender_id, receiver_id, amount, description=""):
        """Transfer money between users"""
        receiver = User.query.get(receiver_id)
        if not receiver:
            raise AppNotFoundException("Receiver not found")
        
        sender = User.query.get(sender_id)
        if not sender:
            raise AppNotFoundException("Sender not found")
        
        debit_transaction = TransactionService.create_transaction(
            sender_id, amount, 'debit', 'transfer', 
            f"Transfer to {receiver.name}", description, receiver_id
        )
        
        credit_transaction = TransactionService.create_transaction(
            receiver_id, amount, 'credit', 'transfer',
            f"Transfer from {sender.name}", description, sender_id
        )
        
        try:
            telegram_service.send_transfer_notification(sender_id, receiver_id, amount, description)
        except AppException as e:
            print(f"Telegram notification failed but transaction completed: {e}")
        
        return debit_transaction, credit_transaction

transaction_service = TransactionService()