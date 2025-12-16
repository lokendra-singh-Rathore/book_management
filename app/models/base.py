from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    """
    Base class for all SQLAlchemy models using SQLAlchemy 2.0 features.
    
    MappedAsDataclass automatically generates:
    - __init__() method
    - __repr__() method
    - __eq__() method
    
    This significantly reduces boilerplate code.
    """
    pass


class TimestampMixin(MappedAsDataclass):
    """Mixin for adding timestamp fields to models."""
    
    # Use init=False to exclude from __init__ as these are auto-generated
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
    )
