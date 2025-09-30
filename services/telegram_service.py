import os
import requests
from models.user_credentials import UserCredential
from models.user import User
from models.transaction import Transaction
from utils.exceptions import AppException, NotFoundException, ValidationException

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot_username = None
        
        # Don't crash on initialization - just warn if token is missing
        if not self.bot_token:
            print("TELEGRAM_BOT_TOKEN not found. Telegram notifications will be disabled.")
        else:
            self._initialize_bot()
    
    def _initialize_bot(self):
        """Initialize and test the bot connection"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    self.bot_username = bot_info['result']['username']
                    print(f"Telegram bot initialized: @{self.bot_username}")
                else:
                    print("Failed to get bot info from Telegram API")
            else:
                print(f"Telegram API connection failed: {response.status_code}")
        except Exception as e:
            print(f"Telegram initialization error: {str(e)}")
    
    def send_notification(self, user_id, message):
        """Send notification to user's Telegram chat ID"""
        if not self.bot_token:
            print(f"Telegram disabled - would send to user {user_id}: {message}")
            return True
            
        try:
            creds = UserCredential.query.filter_by(user_id=user_id).first()
            if not creds or not creds.telegram_chat_id:
                print(f"No Telegram chat ID found for user {user_id}")
                return False
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': creds.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"Telegram notification sent to user {user_id}")
                return True
            else:
                print(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Telegram notification failed: {str(e)}")
            return False
    
    def send_income_notification(self, user_id, transaction_id):
        """Send dynamic income notification based on actual transaction"""
        if not self.bot_token:
            print(f"Telegram disabled - income notification for user {user_id}, transaction {transaction_id}")
            return True
            
        transaction = Transaction.query.get(transaction_id)
        user = User.query.get(user_id)
        
        if not transaction or not user:
            return False
        
        message = f"""
<b>Income Received</b>

Amount: <b>{transaction.amount} ILS</b>
Title: {transaction.title}
Description: {transaction.description or 'No description'}
Category: {transaction.category}
Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}

New Balance: <b>{user.balance} ILS</b>

Thank you for your business.
        """
        
        return self.send_notification(user_id, message)
    
    def send_expense_notification(self, user_id, transaction_id):
        """Send dynamic expense notification based on actual transaction"""
        if not self.bot_token:
            print(f"Telegram disabled - expense notification for user {user_id}, transaction {transaction_id}")
            return True
            
        transaction = Transaction.query.get(transaction_id)
        user = User.query.get(user_id)
        
        if not transaction or not user:
            return False
        
        message = f"""
<b>Expense Recorded</b>

Amount: <b>{transaction.amount} ILS</b>
Title: {transaction.title}
Description: {transaction.description or 'No description'}
Category: {transaction.category}
Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}

Remaining Balance: <b>{user.balance} ILS</b>

Keep tracking your expenses.
        """
        
        return self.send_notification(user_id, message)
    
    def send_transfer_notification(self, sender_id, receiver_id, amount, description=""):
        """Send dynamic transfer notifications to both users"""
        if not self.bot_token:
            print(f"Telegram disabled - transfer notification from {sender_id} to {receiver_id}")
            return True
            
        sender = User.query.get(sender_id)
        receiver = User.query.get(receiver_id)
        
        if not sender or not receiver:
            return False
        
        # Get the latest transaction for timestamp
        latest_transaction = Transaction.query.filter_by(user_id=sender_id).order_by(Transaction.created_at.desc()).first()
        timestamp = latest_transaction.created_at.strftime('%Y-%m-%d %H:%M') if latest_transaction else "Unknown"
        
        # Notification for sender
        sender_message = f"""
<b>Transfer Sent</b>

Amount: <b>{amount} ILS</b>
To: {receiver.name}
Description: {description or 'No description'}
Date: {timestamp}

Your New Balance: <b>{sender.balance} ILS</b>

Transfer completed successfully.
        """
        
        # Notification for receiver
        receiver_message = f"""
<b>Transfer Received</b>

Amount: <b>{amount} ILS</b>
From: {sender.name}
Description: {description or 'No description'}
Date: {timestamp}

Your New Balance: <b>{receiver.balance} ILS</b>

Money received successfully.
        """
        
        sender_success = self.send_notification(sender_id, sender_message)
        receiver_success = self.send_notification(receiver_id, receiver_message)
        
        return sender_success and receiver_success
    
    def send_salary_notification(self, user_id, transaction_id):
        """Send dynamic salary notification"""
        if not self.bot_token:
            print(f"Telegram disabled - salary notification for user {user_id}")
            return True
            
        transaction = Transaction.query.get(transaction_id)
        user = User.query.get(user_id)
        
        if not transaction or not user:
            return False
        
        message = f"""
<b>Salary Credited</b>

Amount: <b>{transaction.amount} ILS</b>
Type: {transaction.title}
Description: {transaction.description}
Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}

New Balance: <b>{user.balance} ILS</b>

Your salary has been deposited.
        """
        
        return self.send_notification(user_id, message)

telegram_service = TelegramService()