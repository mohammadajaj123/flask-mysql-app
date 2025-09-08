from marshmallow import Schema, fields

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    description = fields.Str(required=False, allow_none=True)
    user_id = fields.Int(required=False)

class TransactionUpdateSchema(Schema):
    amount = fields.Float()
    description = fields.Str(allow_none=True)
