# exceptions.py
class CustomException(Exception):
    pass

class AppNotFoundException(CustomException):
    status_code = 404
    default_message = "Not found Error!"

class ValidationException(CustomException):
    status_code = 400
    default_message = "Validation Error!"

class AuthorizationException(CustomException):
    status_code = 403
    default_message = "Authorization Error!"

class AuthenticationException(CustomException):
    status_code = 401
    default_message = "Authentication Error!"

class InternalServerException(CustomException):
    status_code = 500
    default_message = "Internal Server Error!"