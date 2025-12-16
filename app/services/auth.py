from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.token import Token
from app.repositories.user import UserRepository
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import UnauthorizedError, ConflictError, ValidationError


class AuthService:
    """Service for handling authentication and user management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
        
        Returns:
            Created user instance
        
        Raises:
            ConflictError: If email already exists
        """
        # Check if email exists
        if await self.user_repo.email_exists(user_data.email):
            raise ConflictError(detail="Email already registered")
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )
        
        return await self.user_repo.create(user)
    
    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email
            password: Plain text password
        
        Returns:
            Authenticated user instance
        
        Raises:
            UnauthorizedError: If credentials are invalid
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise UnauthorizedError(detail="Incorrect email or password")
        
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError(detail="Incorrect email or password")
        
        if not user.is_active:
            raise UnauthorizedError(detail="User account is inactive")
        
        return user
    
    def create_user_tokens(self, user: User) -> Token:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: User instance
        
        Returns:
            Token object with access and refresh tokens
        """
        token_data = {"sub": user.email, "user_id": user.id}
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Create new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New token object
        
        Raises:
            UnauthorizedError: If refresh token is invalid
        """
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError(detail="Invalid refresh token")
        
        email = payload.get("sub")
        if not email:
            raise UnauthorizedError(detail="Invalid refresh token")
        
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError(detail="User not found")
        
        return self.create_user_tokens(user)
    
    async def get_current_user(self, token: str) -> User:
        """
        Get current user from access token.
        
        Args:
            token: JWT access token
        
        Returns:
            Current user instance
        
        Raises:
            UnauthorizedError: If token is invalid
        """
        payload = decode_token(token)
        
        if not payload:
            raise UnauthorizedError(detail="Could not validate credentials")
        
        email = payload.get("sub")
        if not email:
            raise UnauthorizedError(detail="Could not validate credentials")
        
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError(detail="User not found")
        
        return user
