from fastapi import FastAPI

from src.api.routers.accounts import router as accounts_router
from src.api.routers.movies import router as movies_router
from src.api.routers.cart import router as cart_router


def create_app() -> FastAPI:
    app = FastAPI(title="Online Cinema API", version="0.1.0")

    app.include_router(accounts_router)
    app.include_router(movies_router)
    app.include_router(cart_router)

    return app
