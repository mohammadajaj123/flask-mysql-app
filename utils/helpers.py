from flask_jwt_extended import get_jwt, get_jwt_identity

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

def can_act_on_user(target_user_id: int) -> bool:
    """Allow if admin OR the token's user_id matches target_user_id"""
    if is_admin():
        return True
    current_user_id = int(get_jwt_identity())
    return current_user_id == int(target_user_id)
