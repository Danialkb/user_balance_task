import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from resources.config import settings
from resources.logs.config import logging_config
from routers import user_balance

logging.config.dictConfig(logging_config)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Zimran User Balance",
        version="1.0.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(user_balance.router)

    return app


app = create_app()
