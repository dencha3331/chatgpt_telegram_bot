from __future__ import annotations


class UserNotRegistration(Exception):
    """Not register user"""

    def __init__(self, message: str | None = None):
        self.message = "Not register user" if not message else message

    def __str__(self):
        return self.message


class MessageFromUserIsNone(Exception):
    """Message.from_user is None"""

    def __init__(self, message: str | None = None):
        self.message = "Message.from_user is None" if not message else message

    def __str__(self):
        return self.message
