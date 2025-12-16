from typing import Optional, List
from datetime import date
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from app.models.user import user_books


class Book(Base, TimestampMixin):
    """
    Book model with SQLAlchemy 2.0 modern features.
    
    Many-to-many relationship with User through user_books association table.
    """
    
    __tablename__ = "books"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    # Book fields
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[Optional[str]] = mapped_column(String(13), unique=True, index=True, default=None)
    published_date: Mapped[Optional[date]] = mapped_column(Date, default=None)
    description: Mapped[Optional[str]] = mapped_column(String(1000), default=None)
    
    # Many-to-many relationship with User
    users: Mapped[List["User"]] = relationship(
        secondary=user_books,
        back_populates="books",
        default_factory=list,
        init=False,
    )
