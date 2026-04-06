from fastapi import FastAPI

from app.routers import auth, categories, products


def create_app() -> FastAPI:
    app = FastAPI(title="Rivo API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(categories.router)

    return app


app = create_app()
