from __future__ import annotations


class ChatgptAnswerErrors(Exception):
    """Error in chatgpt.py in chatgpt_answer"""

    def __init__(self, message: str | None = None):
        self.message = "Error in chatgpt.py in chatgpt_answer" if not message else message

    def __str__(self):
        return self.message






