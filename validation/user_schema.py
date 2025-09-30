from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    age = fields.Int(validate=validate.Range(min=1, max=120))
    role = fields.Str(validate=validate.OneOf(["admin", "user"]), load_default="user")
    balance = fields.Float(dump_only=True)
    
class UserCreateSchema(UserSchema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    telegram_chat_id = fields.Str(required=False)

class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=100))
    email = fields.Email()
    age = fields.Int(validate=validate.Range(min=1, max=120))
    role = fields.Str(validate=validate.OneOf(["admin", "user"]))
    username = fields.Str(validate=validate.Length(min=3, max=50))
    password = fields.Str(validate=validate.Length(min=6))
    telegram_chat_id = fields.Str()