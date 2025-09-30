from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError as MarshmallowValidationError
from .exceptions import (
    CustomException, AppNotFoundException, ValidationException,
    AuthorizationException, AuthenticationException, InternalServerException
)

def route(bp, rule, methods=None, allow_only=None, validation=None, response_schema=None):
    """
    Enhanced decorator for structured API routes
    
    Args:
        bp: Blueprint instance
        rule: URL rule
        methods: HTTP methods
        allow_only: List of allowed roles (e.g., ["admin"])
        validation: Marshmallow schema for request validation
        response_schema: Marshmallow schema for response serialization
    """

    def decorator(func):
        @bp.route(rule, methods=methods or ['GET'])
        @jwt_required(optional=True)
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if allow_only:
                    claims = get_jwt() or {}
                    role = claims.get("role")
                    if role not in allow_only:
                        raise AuthorizationException(
                            f"Required roles: {allow_only}. Your role: {role}"
                        )

                validated_data = None
                if validation:
                    schema = validation()
                    try:
                        validated_data = schema.load(request.json or {})
                    except MarshmallowValidationError as err:
                        print(f"Validation Error: {err.messages}")
                        raise ValidationException(str(err.messages))

                result = func(validated_data, *args, **kwargs)

                if response_schema and result:
                    schema = response_schema(many=isinstance(result, list))
                    return jsonify(schema.dump(result))

                return jsonify(result)
                
            except CustomException as e:
                print(f"Custom Exception [{e.status_code}]: {type(e).__name__} - {e.message}")
                return jsonify({"error": e.default_message}), e.status_code
                
            except Exception as e:
                print(f"Unexpected Error [500]: {type(e).__name__} - {str(e)}")
                return jsonify({"error": "An internal server error occurred"}), 500
                
        return wrapper
    return decorator