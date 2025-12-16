from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.middleware.logging import LoggingMiddleware
from app.api.v1 import api_router
from app.events.producer import kafka_producer
from app.chat.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📊 Debug mode: {settings.DEBUG}")
    print(f"🔗 Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    
    # Initialize Kafka producer
    if settings.KAFKA_ENABLE:
        try:
            await kafka_producer.start()
            print(f"✅ Kafka producer connected: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            print(f"⚠️ Kafka producer failed to start: {e}")
            print("   Application will continue without Kafka messaging")
    else:
        print("ℹ️  Kafka messaging is disabled")
    
    # Initialize Redis client
    if settings.REDIS_ENABLE:
        try:
            await redis_client.connect()
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("   Chat features may be limited")
    else:
        print("ℹ️  Redis is disabled")
    
    yield
    
    # Shutdown
    if settings.KAFKA_ENABLE:
        await kafka_producer.stop()
        print("🛑 Kafka producer stopped")
    
    if settings.REDIS_ENABLE:
        await redis_client.disconnect()
        print("🛑 Redis disconnected")
    
    print(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready Book Management API with SQLAlchemy 2.0 and Kafka Messaging",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include API routers
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "kafka_enabled": settings.KAFKA_ENABLE,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "kafka_enabled": settings.KAFKA_ENABLE,
        "kafka_connected": kafka_producer._producer is not None if settings.KAFKA_ENABLE else False,
    }
