from marshmallow import Schema, fields, validate

CATEGORIES = ['salary', 'food', 'rent', 'transport', 'entertainment', 'healthcare', 'shopping', 'utilities', 'other']

class IncomeSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False)
    user_id = fields.Int(required=False)
    category = fields.Str(required=False, validate=validate.OneOf(CATEGORIES), load_default='other')

class ExpenseSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False)
    user_id = fields.Int(required=False)
    category = fields.Str(required=False, validate=validate.OneOf(CATEGORIES), load_default='other')

class TransferSchema(Schema):
    receiver_id = fields.Int(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(required=False)
    category = fields.Str(required=False, validate=validate.OneOf(CATEGORIES), load_default='transfer')

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float()
    entry_type = fields.Str()
    category = fields.Str()
    title = fields.Str()
    description = fields.Str()
    user_id = fields.Int()
    related_user_id = fields.Int()
    created_at = fields.DateTime()

class ProfileSchema(Schema):
    user_id = fields.Int(dump_only=True)
    name = fields.Str()
    age = fields.Int()
    balance = fields.Float()

class SalarySchema(Schema):
    user_id = fields.Int(required=True)
    amount = fields.Float(required=False, validate=validate.Range(min=0.01))