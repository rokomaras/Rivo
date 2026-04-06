from fastapi import Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for domain errors that map to HTTP responses."""

    def __init__(self, code: str, message: str, status_code: int, fields: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.fields = fields
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(code="not_found", message=message, status_code=404)


class ForbiddenError(DomainError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(code="forbidden", message=message, status_code=403)


class UnauthorizedError(DomainError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(code="unauthorized", message=message, status_code=401)


class DuplicateItemError(DomainError):
    def __init__(self, message: str = "Item already exists"):
        super().__init__(code="duplicate_item", message=message, status_code=409)


class OrderLockedError(DomainError):
    def __init__(self, message: str = "Order is locked and cannot be modified"):
        super().__init__(code="order_locked", message=message, status_code=400)


class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(code="conflict", message=message, status_code=409)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    body: dict = {"code": exc.code, "message": exc.message}
    if exc.fields:
        body["fields"] = exc.fields
    return JSONResponse(status_code=exc.status_code, content=body)
