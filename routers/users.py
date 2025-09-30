from flask import Blueprint
from utils.decorators import route
from validation.user_schema import UserCreateSchema, UserSchema, UserUpdateSchema
from business_logic.user_logic import create_user_logic, get_users_logic, update_user_logic, delete_user_logic

bp = Blueprint("users", __name__)

@route(
    bp, "/", 
    methods=["POST"], 
    validation=UserCreateSchema, 
    response_schema=UserSchema,
    allow_only=["admin"]
)
def create_user(validated_data):
    """Create new user (Admin only)"""
    return create_user_logic(validated_data)

@route(
    bp, "/", 
    methods=["GET"], 
    response_schema=UserSchema,
    allow_only=["admin"]
)
def get_users(validated_data):
    """Get all users (Admin only)"""
    return get_users_logic()

@route(
    bp, "/<int:user_id>", 
    methods=["PUT"], 
    validation=UserUpdateSchema, 
    response_schema=UserSchema
)
def update_user(validated_data, user_id):
    """Update user profile (User can update own, Admin can update any)"""
    return update_user_logic(user_id, validated_data)

@route(
    bp, "/<int:user_id>", 
    methods=["DELETE"], 
    allow_only=["admin"]
)
def delete_user(validated_data, user_id):
    """Delete user (Admin only)"""
    return delete_user_logic(user_id)

@route(
    bp, "/my-profile", 
    methods=["GET"], 
    response_schema=UserSchema
)
def get_my_profile(validated_data):
    """Get current user's profile"""
    from flask_jwt_extended import get_jwt_identity
    from business_logic.user_logic import get_users_logic
    user_id = int(get_jwt_identity())
    users = get_users_logic()
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        from utils.exceptions import NotFoundException
        raise NotFoundException("User not found")
    return user