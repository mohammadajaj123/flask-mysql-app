from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from models.user import UserCredential

def login_logic(username, password):
    creds = UserCredential.query.filter_by(username=username).first()
    if not creds or not check_password_hash(creds.password_hash, password):
        return None, "Invalid username or password"

    user = creds.user
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return {
        "message": "Login successful",
        "access_token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
    }, None
