# Book Management API

A production-ready FastAPI application for managing books with user authentication, built with modern Python best practices.

## Features

✨ **Modern Stack**
- FastAPI with async/await support
- SQLAlchemy 2.0 with latest features (MappedAsDataclass, Mapped types)
- PostgreSQL with async driver (asyncpg)
- Pydantic v2 for data validation
- Alembic for database migrations

🔐 **Authentication & Security**
- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Token expiration and validation
- Protected endpoints with dependency injection

📚 **Book Management**
- Full CRUD operations for books
- Many-to-many relationship between users and books
- Share books with other users
- **Pagination** - Control page size and navigate through results
- **Searching** - Search across title, author, and description
- **Filtering** - Filter by author
- **Sorting** - Sort by title, author, published_date, or created_at (asc/desc)

🏗️ **Clean Architecture**
- Repository pattern for database abstraction
- Service layer for business logic
- Middleware for logging and authentication
- Clear separation of concerns

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy 2.0.25
- **Async Driver**: asyncpg 0.29.0
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic v2.5.3
- **Authentication**: python-jose, passlib
- **Server**: Uvicorn with standard extras

## Project Structure

```
book_management/
├── app/
│   ├── api/                    # API routes
│   │   ├── deps.py            # Dependencies (DB session, auth)
│   │   └── v1/
│   │       ├── auth.py        # Authentication endpoints
│   │       └── books.py       # Book CRUD endpoints
│   │
│   ├── core/                   # Core functionality
│   │   ├── database.py        # Database session management
│   │   ├── security.py        # JWT, password hashing
│   │   └── exceptions.py      # Custom exceptions
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── base.py            # Base model with MappedAsDataclass
│   │   ├── user.py            # User model
│   │   └── book.py            # Book model
│   │
│   ├── repositories/           # Repository layer
│   │   ├── base.py            # Generic base repository
│   │   ├── user.py            # User repository
│   │   └── book.py            # Book repository
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py            # User schemas
│   │   ├── book.py            # Book schemas
│   │   └── token.py           # Token schemas
│   │
│   ├── services/               # Business logic layer
│   │   ├── auth.py            # Authentication service
│   │   └── book.py            # Book service
│   │
│   ├── middleware/             # Custom middleware
│   │   ├── auth.py            # Authentication middleware
│   │   └── logging.py         # Request/response logging
│   │
│   ├── config.py              # Configuration management
│   └── main.py                # FastAPI application
│
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
│
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file
├── alembic.ini                # Alembic configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## SQLAlchemy 2.0 Modern Features

This project leverages SQLAlchemy 2.0's latest features to reduce boilerplate code:

### MappedAsDataclass

Automatically generates `__init__()`, `__repr__()`, and `__eq__()` methods:

```python
class Base(DeclarativeBase, MappedAsDataclass):
    """Base class with automatic dataclass generation"""
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

### Mapped Types

Provides type safety and excellent IDE support:

```python
# Type-safe column definitions
email: Mapped[str]                    # Non-nullable string
full_name: Mapped[Optional[str]]      # Nullable string
is_active: Mapped[bool]               # Boolean
created_at: Mapped[datetime]          # Datetime
```

### mapped_column()

Infers SQL types from Python type hints:

```python
# Old way (SQLAlchemy 1.x)
email = Column(String(255), unique=True, index=True)

# New way (SQLAlchemy 2.0)
email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
```

### Many-to-Many Relationships

Clean definition of association tables:

```python
user_books = Table(
    "user_books",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)

class Book(Base):
    users: Mapped[List["User"]] = relationship(
        secondary=user_books,
        back_populates="books",
    )
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip or poetry

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd book_management
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env and update with your values
   # Especially DATABASE_URL and SECRET_KEY
   ```

   Example `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/book_management
   SECRET_KEY=your-very-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

5. **Create PostgreSQL database**:
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE book_management;
   ```

6. **Run database migrations**:
   ```bash
   # Create initial migration (already done, but for reference)
   # alembic revision --autogenerate -m "Initial migration"
   
   # Apply migrations
   alembic upgrade head
   ```

7. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

8. **Access API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Usage Examples

### Authentication

#### Register a new user

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

#### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Refresh token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Book Management

#### Create a book

```bash
curl -X POST "http://localhost:8000/api/v1/books/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "published_date": "2008-08-01",
    "description": "A handbook of agile software craftsmanship"
  }'
```

#### Get your books with pagination, search, filtering, and sorting

**Basic pagination:**
```bash
curl -X GET "http://localhost:8000/api/v1/books/?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Search in title, author, or description:**
```bash
curl -X GET "http://localhost:8000/api/v1/books/?search=clean%20code" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Filter by author:**
```bash
curl -X GET "http://localhost:8000/api/v1/books/?author=martin" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Sort by title (ascending):**
```bash
curl -X GET "http://localhost:8000/api/v1/books/?sort_by=title&sort_order=asc" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Sort by publish date (most recent first):**
```bash
curl -X GET "http://localhost:8000/api/v1/books/?sort_by=published_date&sort_order=desc" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Combining multiple filters:**
```bash
curl -X GET "http://localhost:8000/api/v1/books/?search=python&author=guido&sort_by=published_date&sort_order=desc&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Available sort fields:**
- `title` - Book title
- `author` - Author name
- `published_date` - Publication date
- `created_at` - When the book was added (default)

**Sort orders:**
- `asc` - Ascending (A-Z, oldest first)
- `desc` - Descending (Z-A, newest first) - **default**

#### Get a specific book

```bash
curl -X GET "http://localhost:8000/api/v1/books/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update a book

```bash
curl -X PUT "http://localhost:8000/api/v1/books/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

#### Delete a book

```bash
curl -X DELETE "http://localhost:8000/api/v1/books/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Share a book with another user

```bash
curl -X POST "http://localhost:8000/api/v1/books/1/users/2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Remove a user from a book

```bash
curl -X DELETE "http://localhost:8000/api/v1/books/1/users/2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to base
alembic downgrade base
```

### View migration history

```bash
alembic history

alembic current
```

## Architecture Patterns

### Repository Pattern

Provides a clean abstraction over database operations:

```python
# Repository layer handles database queries
class BookRepository(BaseRepository[Book]):
    async def get_books_for_user(self, user_id: int) -> List[Book]:
        # Database logic here
        ...

# Service layer uses repositories
class BookService:
    def __init__(self, db: AsyncSession):
        self.book_repo = BookRepository(db)
    
    async def get_user_books(self, user: User) -> List[Book]:
        return await self.book_repo.get_books_for_user(user.id)
```

### Service Layer

Handles business logic and orchestrates repositories:

```python
class BookService:
    async def create_book(self, book_data: BookCreate, user: User) -> Book:
        # Business logic
        book = Book(**book_data.dict())
        book.users.append(user)
        return await self.book_repo.create(book)
```

### Dependency Injection

FastAPI's dependency system for clean code:

```python
# Define dependencies
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    # Auth logic
    ...

# Use in routes
@router.get("/books/")
async def get_books(current_user: CurrentUser, db: DatabaseSession):
    # Access authenticated user and database session
    ...
```

## Middleware

### Logging Middleware

Automatically logs all requests with timing information:

```
2024-01-15 10:30:45 - INFO - Request: GET /api/v1/books/
2024-01-15 10:30:45 - INFO - Response: GET /api/v1/books/ Status: 200 Duration: 0.123s
```

### Authentication Middleware

Optional global token validation (route-level auth is recommended):

```python
# Token validation happens at middleware level
# User info is added to request.state
```

## Production Considerations

### Security

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure CORS for specific origins
- [ ] Implement rate limiting (e.g., with slowapi)
- [ ] Add input sanitization

### Performance

- [ ] Use connection pooling
- [ ] Enable database query caching (Redis)
- [ ] Add database indexes for frequently queried fields
- [ ] Implement pagination for all list endpoints
- [ ] Use async operations consistently
- [ ] Configure Uvicorn with multiple workers

### Monitoring

- [ ] Add application logging (e.g., to files or external service)
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Monitor database performance
- [ ] Track API metrics (response times, error rates)
- [ ] Set up health check monitoring

### Deployment

```bash
# Using Uvicorn with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn + Uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Running with Docker

This application is fully containerized and easy to run with Docker Compose.

1. **Install Docker and Docker Compose** if you haven't already.

2. **Configure Environment**:
   Ensure you have a `.env` file created from `.env.example` (or just use the example for development).
   ```bash
   cp .env.example .env
   ```
   *Note: For Docker, the `DATABASE_URL` in `.env` should ideally use `postgres` as the host (e.g., `postgres:5432`), which matches the internal service name. If you are running the app locally (outside Docker), use `localhost`.*

3. **Start the Application**:
   ```bash
   docker-compose up --build
   ```

   This command will start the following services:
   - **api**: The FastAPI application (Port 8000)
   - **postgres**: PostgreSQL database (External Port 5435, Internal 5432)
   - **kafka & zookeeper**: Message queue services
   - **redis**: Cache for chat features

4. **Automatic Migrations**:
   The Docker container is configured to **automatically run database migrations** (`alembic upgrade head`) every time it starts. You do not need to run them manually.

5. **Access the App**:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - Database (External): localhost:5435

## Testing (Setup Ready)

Project structure supports easy testing:

```python
# Example test structure
tests/
├── conftest.py              # Pytest fixtures
├── test_auth.py             # Auth endpoint tests
└── test_books.py            # Book endpoint tests
```

Install testing dependencies:

```bash
pip install pytest pytest-asyncio httpx
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (when implemented)
5. Submit a pull request

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

---

**Built with ❤️ using FastAPI, SQLAlchemy 2.0, and modern Python best practices.**
