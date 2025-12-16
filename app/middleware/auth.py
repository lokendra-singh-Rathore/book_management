from typing import Optional, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optional authentication middleware for validating JWT tokens globally.
    
    Note: This is a global middleware approach. For most use cases,
    using dependency injection (get_current_user) at the route level
    provides better flexibility.
    """
    
    # Paths that don't require authentication
    EXCLUDED_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Validate JWT token if present.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
        
        Returns:
            HTTP response
        """
        # Skip authentication for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            
            # Add user info to request state if token is valid
            if payload:
                request.state.user_email = payload.get("sub")
                request.state.user_id = payload.get("user_id")
        
        # Continue processing (authentication is enforced at route level via dependencies)
        return await call_next(request)
