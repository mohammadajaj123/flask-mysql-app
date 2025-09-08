from flask import Blueprint
from utils.decorators import route
from validation.transaction_schema import TransactionSchema, TransactionUpdateSchema
from business_logic.transaction_logic import (
    create_transaction_logic, get_transactions_logic,
    update_transaction_logic, delete_transaction_logic
)

bp = Blueprint("transactions", __name__)

@route(bp, "/", methods=["POST"], validation=TransactionSchema, response_schema=TransactionSchema)
def create_transaction(validated_data):
    return create_transaction_logic(validated_data)

@route(bp, "/", methods=["GET"], response_schema=TransactionSchema)
def get_transactions(validated_data):
    return get_transactions_logic()

@route(bp, "/<int:transaction_id>", methods=["PUT"], validation=TransactionUpdateSchema, response_schema=TransactionSchema)
def update_transaction(validated_data, transaction_id):
    return update_transaction_logic(transaction_id, validated_data)

@route(bp, "/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(validated_data, transaction_id):
    return delete_transaction_logic(transaction_id)
