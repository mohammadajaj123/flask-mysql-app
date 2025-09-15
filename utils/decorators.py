# utils/decorators.py
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError as MarshmallowValidationError

# Import from the same directory (utils folder)
from .exceptions import (
    CustomException, AppNotFoundException, ValidationException,
    AuthorizationException, AuthenticationException, InternalServerException
)

def route(bp, rule, methods=None, allow_only=None, validation=None, response_schema=None):
    """
    Custom decorator for:
    - Role checks
    - Input validation
    - Response serialization
    - Exception handling
    """

    def decorator(func):
        @bp.route(rule, methods=methods or ['GET'])
        @jwt_required(optional=True)
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Role restriction
                if allow_only:
                    claims = get_jwt() or {}
                    role = claims.get("role")
                    if role not in allow_only:
                        raise AuthorizationException()

                # Validation
                validated_data = None
                if validation:
                    schema = validation()
                    try:
                        validated_data = schema.load(request.json or {})
                    except MarshmallowValidationError as err:
                        raise ValidationException()

                # Run business logic
                result = func(validated_data, *args, **kwargs)

                # Serialization
                if response_schema and result:
                    schema = response_schema(many=isinstance(result, list))
                    return jsonify(schema.dump(result))

                return jsonify(result)
                
            except CustomException as e:
                # Print detailed error to terminal
                print(f"Custom Exception: {type(e).__name__} - {str(e)}")
                # Return default message to user
                return jsonify({"error": e.default_message}), e.status_code
            except Exception as e:
                # Print detailed error to terminal
                print(f"Unexpected Error: {type(e).__name__} - {str(e)}")
                # Return generic message to user
                return jsonify({"error": "An internal server error occurred"}), 500
                
        return wrapper
    return decorator