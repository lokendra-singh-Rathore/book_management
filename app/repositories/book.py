from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.models.user import User
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Repository for Book model with custom methods."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Book, db)
    
    async def get_books_for_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Book]:
        """
        Get all books associated with a specific user with advanced filtering.
        
        Args:
            user_id: User's ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search query for title or author
            author: Filter by specific author
            sort_by: Field to sort by (title, author, published_date, created_at)
            sort_order: Sort order (asc or desc)
        
        Returns:
            List of books associated with the user
        """
        query = select(Book).join(Book.users).where(User.id == user_id)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Book.title.ilike(search_pattern),
                    Book.author.ilike(search_pattern),
                    Book.description.ilike(search_pattern),
                )
            )
        
        # Apply author filter
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        
        # Apply sorting
        sort_column = getattr(Book, sort_by, Book.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_books_for_user(
        self,
        user_id: int,
        search: Optional[str] = None,
        author: Optional[str] = None,
    ) -> int:
        """
        Count books associated with a specific user with optional filters.
        
        Args:
            user_id: User's ID
            search: Search query for title or author
            author: Filter by specific author
        
        Returns:
            Total count of books for the user matching filters
        """
        from sqlalchemy import func
        
        query = (
            select(func.count())
            .select_from(Book)
            .join(Book.users)
            .where(User.id == user_id)
        )
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Book.title.ilike(search_pattern),
                    Book.author.ilike(search_pattern),
                    Book.description.ilike(search_pattern),
                )
            )
        
        # Apply author filter
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def search_books(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        """
        Search books by title or author.
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of matching books
        """
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(Book)
            .where(
                or_(
                    Book.title.ilike(search_pattern),
                    Book.author.ilike(search_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_users(self, book_id: int) -> Optional[Book]:
        """
        Get a book with its associated users eagerly loaded.
        
        Args:
            book_id: Book's ID
        
        Returns:
            Book instance with users loaded, or None
        """
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.users))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()
