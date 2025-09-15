from flask import Blueprint
from utils.decorators import route
from validation.user_schema import UserCreateSchema, UserSchema, UserUpdateSchema
from business_logic.user_logic import create_user_logic, get_users_logic, update_user_logic, delete_user_logic

bp = Blueprint("users", __name__)

@route(bp, "/", methods=["POST"], allow_only=["admin"], validation=UserCreateSchema, response_schema=UserSchema)
def create_user(validated_data):
    return create_user_logic(validated_data)

@route(bp, "/", methods=["GET"], allow_only=["admin"], response_schema=UserSchema)
def get_users(validated_data):
    return get_users_logic()

@route(bp, "/<int:user_id>", methods=["PUT"], validation=UserUpdateSchema, response_schema=UserSchema)
def update_user(validated_data, user_id):
    return update_user_logic(user_id, validated_data)

@route(bp, "/<int:user_id>", methods=["DELETE"], allow_only=["admin"])
def delete_user(validated_data, user_id):
    return delete_user_logic(user_id)