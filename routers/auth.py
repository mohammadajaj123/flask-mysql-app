from flask import Blueprint
from utils.decorators import route
from validation.auth_schema import LoginSchema
from business_logic.auth_logic import login_logic

bp = Blueprint("auth", __name__)

@route(bp, "/login", methods=["POST"], validation=LoginSchema)
def login(validated_data):
    return login_logic(**validated_data)