from extensions import db
from werkzeug.security import generate_password_hash
from models.user import User
from models.user_credentials import UserCredential
from utils.exceptions import ValidationException, AppNotFoundException

def create_user_logic(data):
    if User.query.filter_by(email=data['email']).first():
        raise ValidationException("Email already exists")
    if UserCredential.query.filter_by(username=data['username']).first():
        raise ValidationException("Username already exists")

    # Create user
    new_user = User(
        name=data['name'],
        email=data['email'],
        age=data.get('age'),
        role=data.get('role', 'user')
    )
    db.session.add(new_user)
    db.session.commit()

    # Create credentials
    creds = UserCredential(
        user_id=new_user.id,
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        telegram_chat_id=data.get('telegram_chat_id')
    )
    db.session.add(creds)
    db.session.commit()

    return new_user

def update_user_logic(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundException("User not found")

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.age = data.get('age', user.age)
    if 'role' in data:
        user.role = data['role']
    
    # Update credentials if provided
    if 'username' in data or 'password' in data or 'telegram_chat_id' in data:
        creds = UserCredential.query.filter_by(user_id=user_id).first()
        if not creds:
            raise NotFoundException("User credentials not found")
        
        if 'username' in data:
            # Check if username is already taken by another user
            existing = UserCredential.query.filter(
                UserCredential.username == data['username'],
                UserCredential.user_id != user_id
            ).first()
            if existing:
                raise ValidationException("Username already taken")
            creds.username = data['username']
        
        if 'password' in data:
            creds.password_hash = generate_password_hash(data['password'])
        
        if 'telegram_chat_id' in data:
            creds.telegram_chat_id = data['telegram_chat_id']

    db.session.commit()
    return user

def get_users_logic():
    return User.query.all()

def delete_user_logic(user_id):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundException("User not found")
    
    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted"}