# Alembic Database Migration Setup Guide

> A comprehensive guide to setting up and using Alembic for database migrations in your Python projects with the latest best practices.

## Table of Contents

- [What is Alembic?](#what-is-alembic)
- [Why Use Alembic?](#why-use-alembic)
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Configuration](#configuration)
- [Creating Your First Migration](#creating-your-first-migration)
- [Common Migration Operations](#common-migration-operations)
- [Best Practices](#best-practices)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## What is Alembic?

Alembic is a lightweight database migration tool for SQLAlchemy. It allows you to:
- Track database schema changes over time
- Version control your database structure
- Apply incremental changes to production databases
- Roll back changes if needed
- Collaborate with team members on database changes

## Why Use Alembic?

✅ **Version Control** - Track all database schema changes in Git  
✅ **Reproducibility** - Apply same changes across dev, staging, and production  
✅ **Collaboration** - Multiple developers can work on database changes  
✅ **Safety** - Review migrations before applying to production  
✅ **Rollback** - Easily revert problematic changes  
✅ **Auto-generation** - Automatically detect model changes  

---

## Installation

### Latest Version (As of December 2024)

```bash
# Install Alembic with the latest version
pip install alembic

# For async support with SQLAlchemy
pip install alembic sqlalchemy asyncpg

# Check installed version
alembic --version
```

### Recommended Requirements

Create or update your `requirements.txt`:

```txt
# Latest stable versions
alembic>=1.13.0
sqlalchemy>=2.0.25
asyncpg>=0.29.0  # For PostgreSQL async support
psycopg2-binary>=2.9.9  # For PostgreSQL sync support
```

> [!TIP]
> Use `alembic>=1.13.0` for the latest features including improved async support and better type hints.

---

## Initial Setup

### Step 1: Initialize Alembic

Navigate to your project root directory and run:

```bash
# Initialize Alembic (creates alembic directory and alembic.ini)
alembic init alembic
```

This creates:
```
your_project/
├── alembic/
│   ├── versions/          # Migration files go here
│   ├── env.py            # Migration environment configuration
│   ├── script.py.mako    # Template for new migrations
│   └── README
├── alembic.ini           # Alembic configuration file
```

### Step 2: Project Structure

For a clean project structure, organize your files like this:

```
your_project/
├── app/
│   ├── models/           # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py       # Base model
│   │   ├── user.py
│   │   └── book.py
│   ├── core/
│   │   ├── database.py   # Database session setup
│   │   └── config.py     # Configuration
│   └── main.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── .env                  # Environment variables
└── requirements.txt
```

---

## Configuration

### Step 1: Configure `alembic.ini`

Update the `alembic.ini` file:

```ini
# alembic.ini

[alembic]
# Path to migration scripts
script_location = alembic

# Template used to generate migration files
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Timezone for timestamps
timezone = UTC

# DO NOT put database URL here for security reasons
# We'll configure it in env.py to use environment variables
# sqlalchemy.url = driver://user:pass@localhost/dbname

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

> [!IMPORTANT]
> Never hardcode database credentials in `alembic.ini`. Use environment variables instead.

### Step 2: Create Environment Variables

Create a `.env` file in your project root:

```env
# .env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/your_database

# Alternative for sync PostgreSQL
# DATABASE_URL=postgresql://postgres:password@localhost:5432/your_database

# For MySQL
# DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/your_database

# For SQLite (development only)
# DATABASE_URL=sqlite+aiosqlite:///./test.db
```

### Step 3: Configure `env.py` for Async Support

Update `alembic/env.py` for modern SQLAlchemy 2.0 with async support:

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your models' Base
from app.models.base import Base

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL from environment variable
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Set the SQLAlchemy URL
config.set_main_option("sqlalchemy.url", database_url)

# Set target metadata from your models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async support.
    
    In this scenario we need to create an Engine and associate 
    a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

> [!NOTE]
> This configuration supports async SQLAlchemy operations and automatically imports all your models.

### Step 4: Set Up Base Model

Create `app/models/base.py` with SQLAlchemy 2.0 syntax:

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for all models with automatic dataclass generation.
    
    SQLAlchemy 2.0 features:
    - MappedAsDataclass: Auto-generates __init__, __repr__, __eq__
    - Mapped[T]: Type-safe column definitions
    - mapped_column(): Infers SQL types from Python type hints
    """
    pass


class TimestampMixin(MappedAsDataclass):
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
    )
```

### Step 5: Create Models

Create your SQLAlchemy models using SQLAlchemy 2.0 syntax:

```python
# app/models/user.py
from typing import Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model with SQLAlchemy 2.0 syntax."""
    
    __tablename__ = "users"
    
    # Primary key (init=False means not in __init__)
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    # Required fields
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    # Optional fields
    full_name: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships (init=False for back_populates)
    books: Mapped[List["Book"]] = relationship(
        secondary="user_books",
        back_populates="users",
        init=False,
        default_factory=list,
    )
```

```python
# app/models/book.py
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Text, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


# Association table for many-to-many relationship
user_books = Table(
    "user_books",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)


class Book(Base, TimestampMixin):
    """Book model with SQLAlchemy 2.0 syntax."""
    
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255), index=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(13), unique=True, default=None)
    published_date: Mapped[Optional[date]] = mapped_column(default=None)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        secondary=user_books,
        back_populates="books",
        init=False,
        default_factory=list,
    )
```

### Step 6: Import All Models

Create `app/models/__init__.py` to import all models:

```python
# app/models/__init__.py
"""Import all models here so Alembic can detect them."""

from app.models.base import Base
from app.models.user import User
from app.models.book import Book, user_books

__all__ = ["Base", "User", "Book", "user_books"]
```

> [!IMPORTANT]
> All models must be imported in `__init__.py` for Alembic to detect them during auto-generation.

---

## Creating Your First Migration

### Step 1: Auto-generate Initial Migration

```bash
# Create initial migration with auto-detection
alembic revision --autogenerate -m "Initial migration - users and books tables"
```

This creates a new file in `alembic/versions/` like:
```
20241209_0730_abc123def456_initial_migration_users_and_books_tables.py
```

### Step 2: Review the Generated Migration

Open the generated file and review:

```python
# alembic/versions/20241209_0730_abc123_initial_migration.py
"""Initial migration - users and books tables

Revision ID: abc123def456
Revises: 
Create Date: 2024-12-09 07:30:00.123456

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration."""
    # ### commands auto generated by Alembic ###
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    op.create_table('books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('isbn', sa.String(length=13), nullable=True),
        sa.Column('published_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_author'), 'books', ['author'], unique=False)
    op.create_index(op.f('ix_books_isbn'), 'books', ['isbn'], unique=True)
    op.create_index(op.f('ix_books_title'), 'books', ['title'], unique=False)
    
    op.create_table('user_books',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'book_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Revert migration."""
    # ### commands auto generated by Alembic ###
    op.drop_table('user_books')
    op.drop_index(op.f('ix_books_title'), table_name='books')
    op.drop_index(op.f('ix_books_isbn'), table_name='books')
    op.drop_index(op.f('ix_books_author'), table_name='books')
    op.drop_table('books')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
```

> [!TIP]
> Always review auto-generated migrations before applying them. Alembic may not capture everything correctly.

### Step 3: Apply the Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> abc123def456, Initial migration
```

### Step 4: Verify Migration

```bash
# Check current migration version
alembic current

# View migration history
alembic history

# View detailed history
alembic history --verbose
```

---

## Common Migration Operations

### Adding a New Column

1. **Update your model**:

```python
# app/models/user.py
class User(Base, TimestampMixin):
    # ... existing fields ...
    
    # Add new field
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), default=None)
```

2. **Generate migration**:

```bash
alembic revision --autogenerate -m "Add phone_number to users"
```

3. **Review and apply**:

```bash
# Review the generated file
# Then apply
alembic upgrade head
```

### Modifying a Column

```python
# In a new migration file
def upgrade() -> None:
    # Change column type
    op.alter_column('users', 'phone_number',
        type_=sa.String(length=15),
        existing_type=sa.String(length=20)
    )
    
    # Make column nullable
    op.alter_column('users', 'full_name',
        nullable=True,
        existing_type=sa.String(length=255)
    )
    
    # Add default value
    op.alter_column('users', 'is_active',
        server_default='true',
        existing_type=sa.Boolean()
    )
```

### Adding an Index

```python
def upgrade() -> None:
    # Add index
    op.create_index('ix_books_published_date', 'books', ['published_date'])
    
    # Add unique index
    op.create_index('ix_users_email_unique', 'users', ['email'], unique=True)
    
    # Add composite index
    op.create_index('ix_books_author_title', 'books', ['author', 'title'])
```

### Adding a Foreign Key

```python
def upgrade() -> None:
    # Add column
    op.add_column('books', sa.Column('publisher_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_books_publisher',
        'books', 'publishers',
        ['publisher_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add index for foreign key
    op.create_index('ix_books_publisher_id', 'books', ['publisher_id'])
```

### Dropping a Column

```python
def upgrade() -> None:
    # Drop column
    op.drop_column('users', 'old_field')

def downgrade() -> None:
    # Add it back
    op.add_column('users', sa.Column('old_field', sa.String(255), nullable=True))
```

### Renaming a Table

```python
def upgrade() -> None:
    op.rename_table('old_table_name', 'new_table_name')

def downgrade() -> None:
    op.rename_table('new_table_name', 'old_table_name')
```

### Data Migrations

```python
from alembic import op
from sqlalchemy import text

def upgrade() -> None:
    # Example: Update existing data
    connection = op.get_bind()
    connection.execute(
        text("UPDATE users SET is_active = true WHERE is_active IS NULL")
    )
    
    # Example: Bulk insert default data
    connection.execute(
        text("""
            INSERT INTO categories (name, description)
            VALUES 
                ('Fiction', 'Fiction books'),
                ('Non-Fiction', 'Non-fiction books'),
                ('Science', 'Science books')
        """)
    )
```

---

## Best Practices

### 1. Migration Naming

Use descriptive migration messages:

```bash
# Good ✅
alembic revision --autogenerate -m "Add email verification fields to users"
alembic revision --autogenerate -m "Create orders and order_items tables"
alembic revision --autogenerate -m "Add indexes to improve book search performance"

# Bad ❌
alembic revision --autogenerate -m "update"
alembic revision --autogenerate -m "fix"
alembic revision --autogenerate -m "changes"
```

### 2. Always Review Auto-generated Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# STOP! Review the generated file before running upgrade
# Check alembic/versions/latest_file.py

# Then apply
alembic upgrade head
```

### 3. Test Migrations in Development First

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 4. Use Transactions

Alembic uses transactions by default, but be explicit:

```python
def upgrade() -> None:
    # These operations are wrapped in a transaction
    op.create_table(...)
    op.add_column(...)
    # If any operation fails, all are rolled back
```

### 5. Handle Data Safely

When modifying columns with data:

```python
def upgrade() -> None:
    # 1. Add new nullable column
    op.add_column('users', sa.Column('new_email', sa.String(255), nullable=True))
    
    # 2. Migrate data
    op.execute("UPDATE users SET new_email = old_email")
    
    # 3. Make new column non-nullable
    op.alter_column('users', 'new_email', nullable=False)
    
    # 4. Drop old column
    op.drop_column('users', 'old_email')
```

### 6. Keep Migrations Small

```bash
# Good ✅ - One logical change per migration
alembic revision --autogenerate -m "Add user roles table"
alembic revision --autogenerate -m "Add role_id to users"
alembic revision --autogenerate -m "Add indexes to roles table"

# Bad ❌ - Too many changes in one migration
alembic revision --autogenerate -m "Add roles, permissions, user_roles, and 15 other things"
```

### 7. Document Complex Migrations

```python
"""Add user roles and permissions system

This migration creates:
1. roles table - defines available roles
2. permissions table - defines available permissions
3. role_permissions - many-to-many relationship
4. user_roles - many-to-many relationship

Note: This migration includes default data for admin and user roles.
"""

def upgrade() -> None:
    # Create tables...
    
    # Insert default data...
    pass
```

### 8. Version Control

```bash
# Always commit migrations with related code changes
git add alembic/versions/20241209_new_migration.py
git add app/models/user.py
git commit -m "Add email verification to user model"
```

### 9. Environment-Specific Migrations

Use environment variables for different environments:

```python
# alembic/env.py
import os

# Use different databases for different environments
env = os.getenv("ENVIRONMENT", "development")
if env == "test":
    database_url = os.getenv("TEST_DATABASE_URL")
else:
    database_url = os.getenv("DATABASE_URL")
```

### 10. Backup Before Production Migrations

```bash
# ALWAYS backup production database before migrations
pg_dump -U postgres -d production_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Then run migrations
alembic upgrade head

# If something goes wrong:
alembic downgrade -1  # or restore from backup
```

---

## Advanced Features

### 1. Branching and Merging

When multiple developers create migrations:

```bash
# Developer A creates migration
alembic revision --autogenerate -m "Add feature A"

# Developer B creates migration (branches from same point)
alembic revision --autogenerate -m "Add feature B"

# This creates two heads - merge them:
alembic merge heads -m "Merge feature A and B"

# Apply merged migration
alembic upgrade head
```

### 2. Stamping Database

Mark database as being at a specific revision without running migrations:

```bash
# Mark as current version
alembic stamp head

# Mark as specific version
alembic stamp abc123def456

# Useful for existing databases
```

### 3. Generating SQL Without Applying

```bash
# Generate SQL for next migration
alembic upgrade head --sql

# Generate SQL for range
alembic upgrade abc123:def456 --sql

# Redirect to file
alembic upgrade head --sql > migration.sql
```

### 4. Multiple Databases

Configure separate migration paths for different databases:

```ini
# alembic.ini
[app1]
script_location = alembic/app1
sqlalchemy.url = postgresql://localhost/app1_db

[app2]
script_location = alembic/app2
sqlalchemy.url = postgresql://localhost/app2_db
```

```bash
# Run migrations for specific database
alembic -n app1 upgrade head
alembic -n app2 upgrade head
```

### 5. Custom Migration Templates

Edit `alembic/script.py.mako` to customize migration template:

```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
Author: Your Name
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

### 6. Post-Deployment Migrations

For zero-downtime deployments:

```python
# Step 1: Add nullable column (safe while old code is running)
def upgrade() -> None:
    op.add_column('users', sa.Column('new_field', sa.String(255), nullable=True))

# Step 2: Deploy new application code that uses new_field

# Step 3: Backfill data
def upgrade() -> None:
    op.execute("UPDATE users SET new_field = 'default' WHERE new_field IS NULL")

# Step 4: Make column non-nullable
def upgrade() -> None:
    op.alter_column('users', 'new_field', nullable=False)
```

---

## Troubleshooting

### Issue: Alembic can't detect model changes

**Solution:**
```python
# Make sure all models are imported in app/models/__init__.py
from app.models.user import User
from app.models.book import Book

# Make sure env.py imports Base correctly
from app.models.base import Base
target_metadata = Base.metadata
```

### Issue: Migration conflicts (multiple heads)

**Solution:**
```bash
# Check for multiple heads
alembic heads

# Merge heads
alembic merge heads -m "Merge conflicting migrations"

# Apply merged migration
alembic upgrade head
```

### Issue: Database connection error

**Solution:**
```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows

# Test database connection
psql -U postgres -d your_database

# Verify alembic can connect
alembic current
```

### Issue: Need to rollback migration

**Solution:**
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123def456

# Rollback all migrations
alembic downgrade base

# Then fix the issue and upgrade again
alembic upgrade head
```

### Issue: Circular dependency in models

**Solution:**
```python
# Use string references for forward declarations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.book import Book

class User(Base):
    books: Mapped[List["Book"]] = relationship(...)  # Use string
```

### Issue: Alembic not detecting relationship changes

**Solution:**
```bash
# Relationship changes often need manual migration
alembic revision -m "Update user-book relationship"

# Then manually write the migration operations
```

### Issue: Production migration failed halfway

**Solution:**
```bash
# 1. Check current database state
alembic current

# 2. Check migration history
alembic history

# 3. If transaction failed (PostgreSQL), safe to retry
alembic upgrade head

# 4. If partially applied (MySQL), may need manual fix
# Restore from backup or manually complete the migration

# 5. Mark as completed if needed
alembic stamp head
```

---

## Quick Reference

### Common Commands

```bash
# Initialize Alembic
alembic init alembic

# Create new migration (auto-generate)
alembic revision --autogenerate -m "Description"

# Create empty migration
alembic revision -m "Description"

# Apply all pending migrations
alembic upgrade head

# Apply next migration
alembic upgrade +1

# Rollback last migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Show current version
alembic current

# Show migration history
alembic history

# Show detailed history
alembic history --verbose

# Check for multiple heads
alembic heads

# Merge multiple heads
alembic merge heads -m "Merge description"

# Generate SQL without applying
alembic upgrade head --sql

# Mark database at specific version
alembic stamp head
```

### Migration File Structure

```python
def upgrade() -> None:
    """Apply migration changes."""
    # Create table
    op.create_table('table_name', ...)
    
    # Add column
    op.add_column('table_name', sa.Column(...))
    
    # Modify column
    op.alter_column('table_name', 'column_name', ...)
    
    # Drop column
    op.drop_column('table_name', 'column_name')
    
    # Create index
    op.create_index('index_name', 'table_name', ['column'])
    
    # Create foreign key
    op.create_foreign_key('fk_name', 'source', 'target', ['col'], ['id'])
    
    # Execute raw SQL
    op.execute("SQL statement")


def downgrade() -> None:
    """Revert migration changes."""
    # Reverse all operations in upgrade()
    pass
```

---

## Additional Resources

📚 **Official Documentation**
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)

🎓 **Tutorials**
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto-generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

🔧 **Tools**
- [Alembic GitHub](https://github.com/sqlalchemy/alembic)
- [SQLAlchemy GitHub](https://github.com/sqlalchemy/sqlalchemy)

---

## Summary Checklist

When setting up Alembic for a new project:

- [ ] Install latest Alembic (`pip install alembic>=1.13.0`)
- [ ] Initialize Alembic (`alembic init alembic`)
- [ ] Configure `alembic.ini` (file template, logging)
- [ ] Set up environment variables (`.env` file)
- [ ] Configure `env.py` for async support
- [ ] Create Base model with SQLAlchemy 2.0 syntax
- [ ] Create your models using `Mapped[T]` and `mapped_column()`
- [ ] Import all models in `app/models/__init__.py`
- [ ] Generate initial migration (`alembic revision --autogenerate`)
- [ ] Review generated migration file
- [ ] Apply migration (`alembic upgrade head`)
- [ ] Verify migration (`alembic current`)
- [ ] Add migrations to version control (`git add alembic/`)
- [ ] Document migration workflow for your team

> [!TIP]
> Bookmark this guide for future reference! Alembic is a powerful tool that becomes easier with practice.

---

**Happy Migrating! 🚀**

*Last Updated: December 2024 | Alembic 1.13+ | SQLAlchemy 2.0+*
