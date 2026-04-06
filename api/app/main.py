from fastapi import FastAPI

from app.core.errors import DomainError, domain_error_handler
from app.routers import auth, categories, orders, products


def create_app() -> FastAPI:
    app = FastAPI(title="Rivo API")

    app.add_exception_handler(DomainError, domain_error_handler)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(categories.router)
    app.include_router(orders.router)

    return app


app = create_app()
