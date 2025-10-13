from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database.connection import initialize_database
from src.presentation.api.routes import credits, feedback, health, image_generation, payments, webhooks
from src.infrastructure.config.settings import get_settings, initialize_settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting AI Photo Generation Service...")

    # Initialize settings
    settings = initialize_settings()
    print(f"Environment: {settings.environment}")

    # Initialize database
    db = initialize_database(settings.database_url)
    await db.create_tables()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")


def create_application() -> FastAPI:
    """Factory function to create FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title="AI Photo Generation API",
        description="Clean Architecture implementation for AI-powered image generation with credit system",
        version="2.0.0",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router)
    app.include_router(feedback.router)
    app.include_router(credits.router)
    app.include_router(payments.router)
    app.include_router(webhooks.router)
    app.include_router(image_generation.router)

    return app


app = create_application()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
