from typing import Optional, List
from sqlalchemy import String, Boolean, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


# Association table for many-to-many relationship between User and Book
user_books = Table(
    "user_books",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base, TimestampMixin):
    """
    User model with SQLAlchemy 2.0 modern features.
    
    Uses Mapped[T] for type safety and mapped_column() for reduced boilerplate.
    The MappedAsDataclass from Base automatically generates __init__, __repr__, etc.
    """
    
    __tablename__ = "users"
    
    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    # User fields with type annotations
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Many-to-many relationship with Book
    books: Mapped[List["Book"]] = relationship(
        secondary=user_books,
        back_populates="users",
        default_factory=list,
        init=False,
    )
