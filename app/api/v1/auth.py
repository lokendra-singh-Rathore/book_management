from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token, RefreshTokenRequest
from app.services.auth import AuthService
from app.api.deps import DatabaseSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DatabaseSession,
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data (email, password, full_name)
        db: Database session
    
    Returns:
        Created user information
    
    Raises:
        409: If email already exists
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: DatabaseSession,
):
    """
    Login with email and password.
    
    Args:
        login_data: Login credentials (email, password)
        db: Database session
    
    Returns:
        Access and refresh tokens
    
    Raises:
        401: If credentials are invalid
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    tokens = auth_service.create_user_tokens(user)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: DatabaseSession,
):
    """
    Refresh access token using refresh token.
    
    Args:
        token_data: Refresh token
        db: Database session
    
    Returns:
        New access and refresh tokens
    
    Raises:
        401: If refresh token is invalid
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_access_token(token_data.refresh_token)
    return tokens
