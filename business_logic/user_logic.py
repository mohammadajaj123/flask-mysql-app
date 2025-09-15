from extensions import db
from werkzeug.security import generate_password_hash
from models.user import User, UserCredential
from utils.exceptions import ValidationException, AppNotFoundException  

def create_user_logic(data):
    if User.query.filter_by(email=data['email']).first():
        raise ValidationException()
    if UserCredential.query.filter_by(username=data['username']).first():
        raise ValidationException()

    new_user = User(name=data['name'], email=data['email'], role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()

    creds = UserCredential(
        user_id=new_user.id,
        username=data['username'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(creds)
    db.session.commit()

    return new_user

def get_users_logic():
    return User.query.all()

def update_user_logic(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise AppNotFoundException()

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    if 'role' in data:
        user.role = data['role']
    db.session.commit()
    return user

def delete_user_logic(user_id):
    user = User.query.get(user_id)
    if not user:
        raise AppNotFoundException()
    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted"}