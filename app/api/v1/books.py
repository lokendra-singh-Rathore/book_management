from typing import Optional
from fastapi import APIRouter, status, Query
from app.schemas.book import BookCreate, BookUpdate, BookResponse, PaginatedBooksResponse
from app.services.book import BookService
from app.api.deps import DatabaseSession, CurrentUser

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Create a new book.
    
    The book will be automatically associated with the current user.
    
    Args:
        book_data: Book creation data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created book information
    """
    book_service = BookService(db)
    book = await book_service.create_book(book_data, current_user)
    return BookResponse.model_validate(book)


@router.get("/", response_model=PaginatedBooksResponse)
async def get_books(
    current_user: CurrentUser,
    db: DatabaseSession,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in title, author, or description"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    sort_by: str = Query("created_at", description="Sort by field (title, author, published_date, created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
):
    """
    Get paginated list of books for the current user with advanced filtering.
    
    **Features:**
    - **Pagination**: Control page number and items per page
    - **Search**: Search across title, author, and description
    - **Filter**: Filter by specific author
    - **Sort**: Sort by title, author, published_date, or created_at
    
    **Examples:**
    - Get first page: `?page=1&page_size=10`
    - Search: `?search=clean code`
    - Filter by author: `?author=martin`
    - Sort by title ascending: `?sort_by=title&sort_order=asc`
    - Combined: `?search=python&author=guido&sort_by=published_date&sort_order=desc`
    
    Args:
        current_user: Authenticated user
        db: Database session
        page: Page number (default: 1)
        page_size: Number of items per page (default: 10, max: 100)
        search: Search query for title, author, or description
        author: Filter by specific author
        sort_by: Field to sort by (title, author, published_date, created_at)
        sort_order: Sort order (asc or desc)
    
    Returns:
        Paginated list of books with metadata
    """
    book_service = BookService(db)
    return await book_service.get_user_books(
        current_user,
        page,
        page_size,
        search=search,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Get a specific book by ID.
    
    Args:
        book_id: Book's ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Book information
    
    Raises:
        404: If book not found
    """
    book_service = BookService(db)
    book = await book_service.get_book(book_id)
    return BookResponse.model_validate(book)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Update a book.
    
    Only users associated with the book can update it.
    
    Args:
        book_id: Book's ID
        book_data: Update data (all fields optional)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated book information
    
    Raises:
        404: If book not found
        403: If user doesn't have access
    """
    book_service = BookService(db)
    book = await book_service.update_book(book_id, book_data, current_user)
    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Delete a book.
    
    Only users associated with the book can delete it.
    
    Args:
        book_id: Book's ID
        current_user: Authenticated user
        db: Database session
    
    Raises:
        404: If book not found
        403: If user doesn't have access
    """
    book_service = BookService(db)
    await book_service.delete_book(book_id, current_user)


@router.post("/{book_id}/users/{user_id}", response_model=BookResponse)
async def add_user_to_book(
    book_id: int,
    user_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Add a user to a book (share book with another user).
    
    Only users already associated with the book can share it.
    
    Args:
        book_id: Book's ID
        user_id: ID of user to add
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated book information
    
    Raises:
        404: If book or user not found
        403: If current user doesn't have access
    """
    book_service = BookService(db)
    book = await book_service.add_user_to_book(book_id, user_id, current_user)
    return BookResponse.model_validate(book)


@router.delete("/{book_id}/users/{user_id}", response_model=BookResponse)
async def remove_user_from_book(
    book_id: int,
    user_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Remove a user from a book.
    
    Only users already associated with the book can remove others.
    
    Args:
        book_id: Book's ID
        user_id: ID of user to remove
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated book information
    
    Raises:
        404: If book or user not found
        403: If current user doesn't have access
    """
    book_service = BookService(db)
    book = await book_service.remove_user_from_book(book_id, user_id, current_user)
    return BookResponse.model_validate(book)
