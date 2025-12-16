from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BookBase(BaseModel):
    """Base book schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    published_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)


class BookCreate(BookBase):
    """Schema for creating a book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    published_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)


class BookResponse(BookBase):
    """Schema for book responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BookWithUsers(BookResponse):
    """Schema for book with associated users."""
    user_ids: List[int] = []
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedBooksResponse(BaseModel):
    """Schema for paginated book list."""
    items: List[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
