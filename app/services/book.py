from typing import List, Optional, Dict, Any
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, PaginatedBooksResponse, BookResponse
from app.repositories.book import BookRepository
from app.repositories.user import UserRepository
from app.core.exceptions import NotFoundError, ForbiddenError
from app.services.event_service import event_service


class BookService:
    """Service for handling book business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.book_repo = BookRepository(db)
        self.user_repo = UserRepository(db)
    
    async def create_book(self, book_data: BookCreate, user: User) -> Book:
        """
        Create a new book and associate it with the user.
        
        Args:
            book_data: Book creation data
            user: User creating the book
        
        Returns:
            Created book instance
        """
        book = Book(
            title=book_data.title,
            author=book_data.author,
            isbn=book_data.isbn,
            published_date=book_data.published_date,
            description=book_data.description,
        )
        
        # Add user to book's users
        book.users.append(user)
        
        book = await self.book_repo.create(book)
        
        # Publish event
        await event_service.publish_book_created(
            book_id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            user_id=user.id
        )
        
        return book
    
    async def get_book(self, book_id: int) -> Book:
        """
        Get a book by ID.
        
        Args:
            book_id: Book's ID
        
        Returns:
            Book instance
        
        Raises:
            NotFoundError: If book not found
        """
        book = await self.book_repo.get(book_id)
        if not book:
            raise NotFoundError(detail="Book not found")
        return book
    
    async def get_user_books(
        self,
        user: User,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginatedBooksResponse:
        """
        Get paginated list of books for a user with advanced filtering.
        
        Args:
            user: User instance
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Search query for title, author, or description
            author: Filter by specific author
            sort_by: Field to sort by (title, author, published_date, created_at)
            sort_order: Sort order (asc or desc)
        
        Returns:
            Paginated book response
        """
        skip = (page - 1) * page_size
        
        books = await self.book_repo.get_books_for_user(
            user_id=user.id,
            skip=skip,
            limit=page_size,
            search=search,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        total = await self.book_repo.count_books_for_user(
            user.id,
            search=search,
            author=author,
        )
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        
        return PaginatedBooksResponse(
            items=[BookResponse.model_validate(book) for book in books],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    
    async def update_book(
        self,
        book_id: int,
        book_data: BookUpdate,
        user: User,
    ) -> Book:
        """
        Update a book.
        
        Args:
            book_id: Book's ID
            book_data: Update data
            user: User performing the update
        
        Returns:
            Updated book instance
        
        Raises:
            NotFoundError: If book not found
            ForbiddenError: If user doesn't have access to the book
        """
        book = await self.book_repo.get_with_users(book_id)
        if not book:
            raise NotFoundError(detail="Book not found")
        
        # Check if user has access to this book
        if user not in book.users:
            raise ForbiddenError(detail="You don't have access to this book")
        
        # Update fields
        update_data = book_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)
        
        book = await self.book_repo.update(book)
        
        # Publish event
        await event_service.publish_book_updated(
            book_id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            user_id=user.id,
            changes=update_data
        )
        
        return book
    
    async def delete_book(self, book_id: int, user: User) -> None:
        """
        Delete a book.
        
        Args:
            book_id: Book's ID
            user: User performing the deletion
        
        Raises:
            NotFoundError: If book not found
            ForbiddenError: If user doesn't have access to the book
        """
        book = await self.book_repo.get_with_users(book_id)
        if not book:
            raise NotFoundError(detail="Book not found")
        
        # Check if user has access to this book
        if user not in book.users:
            raise ForbiddenError(detail="You don't have access to this book")
        
        # Store book info before deletion
        book_title = book.title
        book_author = book.author
        
        await self.book_repo.delete(book)
        
        # Publish event
        await event_service.publish_book_deleted(
            book_id=book_id,
            title=book_title,
            author=book_author,
            user_id=user.id
        )
    
    async def add_user_to_book(self, book_id: int, user_id: int, current_user: User) -> Book:
        """
        Add a user to a book (share book).
        
        Args:
            book_id: Book's ID
            user_id: User ID to add
            current_user: User performing the operation
        
        Returns:
            Updated book instance
        
        Raises:
            NotFoundError: If book or user not found
            ForbiddenError: If current user doesn't have access
        """
        book = await self.book_repo.get_with_users(book_id)
        if not book:
            raise NotFoundError(detail="Book not found")
        
        # Check if current user has access
        if current_user not in book.users:
            raise ForbiddenError(detail="You don't have access to this book")
        
        # Get user to add
        user_to_add = await self.user_repo.get(user_id)
        if not user_to_add:
            raise NotFoundError(detail="User not found")
        
        # Add user if not already in the list
        if user_to_add not in book.users:
            book.users.append(user_to_add)
            await self.book_repo.update(book)
            
            # Publish event
            await event_service.publish_book_shared(
                book_id=book.id,
                title=book.title,
                author=book.author,
                owner_user_id=current_user.id,
                shared_with_user_id=user_to_add.id,
                shared_with_email=user_to_add.email
            )
        
        return book
    
    async def remove_user_from_book(self, book_id: int, user_id: int, current_user: User) -> Book:
        """
        Remove a user from a book.
        
        Args:
            book_id: Book's ID
            user_id: User ID to remove
            current_user: User performing the operation
        
        Returns:
            Updated book instance
        
        Raises:
            NotFoundError: If book or user not found
            ForbiddenError: If current user doesn't have access
        """
        book = await self.book_repo.get_with_users(book_id)
        if not book:
            raise NotFoundError(detail="Book not found")
        
        # Check if current user has access
        if current_user not in book.users:
            raise ForbiddenError(detail="You don't have access to this book")
        
        # Get user to remove
        user_to_remove = await self.user_repo.get(user_id)
        if not user_to_remove:
            raise NotFoundError(detail="User not found")
        
        # Remove user if in the list
        if user_to_remove in book.users:
            book.users.remove(user_to_remove)
            await self.book_repo.update(book)
            
            # Publish event
            await event_service.publish_book_unshared(
                book_id=book.id,
                title=book.title,
                author=book.author,
                owner_user_id=current_user.id,
                removed_user_id=user_to_remove.id
            )
        
        return book
