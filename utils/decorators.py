from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

def route(bp, rule, methods=None, allow_only=None, validation=None, response_schema=None):
    """
    Custom decorator for:
    - Role checks
    - Input validation
    - Response serialization
    """

    def decorator(func):
        @bp.route(rule, methods=methods or ['GET'])
        @jwt_required(optional=True)
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Role restriction
            if allow_only:
                claims = get_jwt() or {}
                role = claims.get("role")
                if role not in allow_only:
                    return jsonify({"error": "Not authorized"}), 403

            # Validation
            validated_data = None
            if validation:
                schema = validation()
                try:
                    validated_data = schema.load(request.json or {})
                except ValidationError as err:
                    return jsonify({"errors": err.messages}), 400

            # Run business logic
            result = func(validated_data, *args, **kwargs)

            # Serialization
            if response_schema and result:
                schema = response_schema(many=isinstance(result, list))
                return jsonify(schema.dump(result))

            return jsonify(result)
        return wrapper
    return decorator
