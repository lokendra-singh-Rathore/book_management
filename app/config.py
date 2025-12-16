from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration using Pydantic v2 BaseSettings."""
    
    # Database
    DATABASE_URL: str
    
    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application
    APP_NAME: str = "Book Management API"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ENABLE: bool = True
    
    # Kafka Topics
    KAFKA_TOPIC_BOOK_EVENTS: str = "book.events"
    KAFKA_TOPIC_USER_EVENTS: str = "user.events"
    KAFKA_TOPIC_NOTIFICATIONS: str = "notifications"
    KAFKA_TOPIC_AUDIT_LOG: str = "audit.log"
    
    # Kafka Consumer Groups
    KAFKA_GROUP_EMAIL: str = "email-notification-group"
    KAFKA_GROUP_AUDIT: str = "audit-log-group"
    KAFKA_GROUP_ANALYTICS: str = "analytics-group"
    KAFKA_GROUP_NOTIFICATION: str = "notification-group"
    
    # Kafka Settings
    KAFKA_AUTO_OFFSET_RESET: str = "latest"  # latest or earliest
    KAFKA_ENABLE_AUTO_COMMIT: bool = True
    KAFKA_COMPRESSION_TYPE: str = "gzip"  # none, gzip, snappy, lz4
    
    # Redis Configuration (for Chat)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_ENABLE: bool = True
    
    # Redis Chat Settings
    REDIS_CHAT_MESSAGE_TTL: int = 604800  # 7 days in seconds
    REDIS_MAX_MESSAGES_PER_ROOM: int = 10000  # Keep recent 10k messages
    REDIS_TYPING_INDICATOR_TTL: int = 5  # 5 seconds
    REDIS_PRESENCE_TTL: int = 300  # 5 minutes
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def kafka_bootstrap_servers_list(self) -> List[str]:
        """Parse KAFKA_BOOTSTRAP_SERVERS into a list."""
        return [server.strip() for server in self.KAFKA_BOOTSTRAP_SERVERS.split(",")]
    
    @property
    def redis_url(self) -> str:
        """Build Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


# Global settings instance
settings = Settings()
