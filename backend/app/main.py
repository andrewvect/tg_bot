"""Main FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from idempotency_header_middleware import IdempotencyHeaderMiddleware
from idempotency_header_middleware.backends import MemoryBackend
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.scripts.set_up_bot import set_up_bot as set_telegram_bot
from app.states import get_users_states
from app.utils.logger import logger


@asynccontextmanager
async def set_up(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa
    """Set up user states."""
    await set_telegram_bot(mode=settings.ENVIRONMENT)
    await get_users_states()
    yield


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


def create_app() -> FastAPI:
    """Create FastAPI app instance with the current settings configuration."""
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=set_up,
    )

    # Add this function to customize the OpenAPI schema with security
    def custom_openapi() -> dict[str, Any] | None:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Add Bearer Authentication security scheme
        openapi_schema["components"] = openapi_schema.get("components", {})
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            }
        }

        # Add security requirement to all operations
        for path_key, path_item in openapi_schema["paths"].items():
            if path_key.startswith("/api/v1/cards"):  # Target only card endpoints
                for operation_key in path_item:
                    if operation_key in ["get", "post", "patch", "put", "delete"]:
                        path_item[operation_key]["security"] = [
                            {"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    # Use setattr to override the openapi method
    app.openapi = custom_openapi

    @app.exception_handler(Exception)
    async def generic_exception(
        request: Request, exc: Exception
    ):
        """Handle exceptions globally."""
        from fastapi.responses import JSONResponse

        logger.error(
            "Unhandled error: %s %s %s %s",
            exc,
            request.url,
            request.method,
            request.body,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

    # Set all CORS enabled origins
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add idempotency middleware with memory backend
    app.add_middleware(
        IdempotencyHeaderMiddleware,
        backend=MemoryBackend(),
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


# Create the default app instance
app = create_app()
