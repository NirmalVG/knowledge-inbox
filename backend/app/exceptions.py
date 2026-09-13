class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class EmptyContentError(AppError):
    def __init__(self):
        super().__init__("EMPTY_CONTENT", "Content cannot be empty.", 400)

class InvalidURLError(AppError):
    def __init__(self, url: str):
        super().__init__("INVALID_URL", f"'{url}' is not a valid URL.", 400)

class ContentTooLargeError(AppError):
    def __init__(self, max_len: int):
        super().__init__("CONTENT_TOO_LARGE", f"Content exceeds max length of {max_len} characters.", 413)

class EmptyQuestionError(AppError):
    def __init__(self):
        super().__init__("EMPTY_QUESTION", "Question cannot be empty.", 400)


class NoContentError(AppError):
    def __init__(self):
        super().__init__("NO_CONTENT", "Add a note or URL before asking questions.", 422)


class UpstreamUnavailableError(AppError):
    def __init__(self, detail: str):
        super().__init__("UPSTREAM_UNAVAILABLE", "The AI service is temporarily unavailable. Please try again.", 502, {"detail": detail})