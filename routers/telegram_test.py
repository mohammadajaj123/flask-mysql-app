from flask import Blueprint, request
from utils.decorators import route
from services.telegram_service import telegram_service
from models.user_credentials import UserCredential
from models.user import User
from models.transaction import Transaction
from extensions import db
from utils.exceptions import ValidationException, NotFoundException, AppException
import os

bp = Blueprint("telegram_test", __name__)

@route(
    bp, "/test-connection", 
    methods=["GET"]
)
def test_telegram_connection(validated_data):
    """Test Telegram bot connection"""
    return {
        "bot_username": telegram_service.bot_username,
        "status": "connected" if telegram_service.bot_username else "disconnected",
        "environment_chat_id": bool(os.getenv('TELEGRAM_CHAT_ID'))
    }

@route(
    bp, "/setup", 
    methods=["POST"]
)
def setup_telegram(validated_data):
    """Set Telegram chat ID for current user"""
    from flask_jwt_extended import get_jwt_identity
    
    user_id = int(get_jwt_identity())
    chat_id = request.json.get('chat_id')
    
    if not chat_id:
        raise ValidationException("chat_id is required")
    
    creds = UserCredential.query.filter_by(user_id=user_id).first()
    if not creds:
        raise NotFoundException("User credentials not found")
    
    creds.telegram_chat_id = chat_id
    db.session.commit()
    
    user = User.query.get(user_id)
    confirmation_message = f"""
<b>Telegram Setup Complete</b>

User: {user.name}
Current Balance: {user.balance} ILS
Chat ID: {chat_id}

You will now receive real-time notifications for all transactions.
    """
    
    telegram_service.send_notification(user_id, confirmation_message)
    
    return {"message": "Telegram chat ID set successfully"}

@route(
    bp, "/test-real-notification", 
    methods=["POST"]
)
def test_real_notification(validated_data):
    """Send test notification with actual user data"""
    from flask_jwt_extended import get_jwt_identity
    
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        raise NotFoundException("User not found")
    
    recent_transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.created_at.desc())\
        .limit(3)\
        .all()
    
    transaction_summary = "\n".join([
        f"- {t.title}: {t.amount} ILS ({t.created_at.strftime('%m/%d')})"
        for t in recent_transactions
    ]) if recent_transactions else "No recent transactions"
    
    message = f"""
<b>Real Data Test</b>

User: {user.name}
Current Balance: <b>{user.balance} ILS</b>

Recent Transactions:
{transaction_summary}

This notification shows your actual account data.
    """
    
    telegram_service.send_notification(user_id, message)
    
    return {"message": "Real data notification sent successfully"}

@route(
    bp, "/test-error-handling", 
    methods=["POST"]
)
def test_error_handling(validated_data):
    """Test exception handling for Telegram service"""
    from flask_jwt_extended import get_jwt_identity
    
    user_id = int(get_jwt_identity())
    
    try:
        telegram_service.send_notification(99999, "This should fail")
        return {"message": "Unexpected success"}
    except NotFoundException as e:
        return {"error": f"NotFoundException correctly caught: {e.message}"}, 400
    except AppException as e:
        return {"error": f"AppException caught: {e.message}"}, 400