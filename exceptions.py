class AppException(Exception):
    """Base exception for all app exceptions"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundException(AppException):
    def __init__(self, user_id: int):
        super().__init__(f"User with ID {user_id} not found", status_code=404)

class InsufficientPermissionsException(AppException):
    def __init__(self, action: str):
        super().__init__(f"You don't have permission to {action}", status_code=403)

class PostNotFoundException(AppException):
    def __init__(self, post_id: int):
        super().__init__(f"Post with ID {post_id} not found", status_code=404)