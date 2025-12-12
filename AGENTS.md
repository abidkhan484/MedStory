# Repository Guidelines for AI Coding Assistants

This document provides guidelines for AI coding assistants (GitHub Copilot, Jules, Antigravity, Cursor, etc.) working with the MedStory codebase.

---

## Project Structure & Module Organization

### Backend Structure (`backend/`)
- **`app/`** - Main application package
  - **`models.py`** - SQLModel database models and Pydantic schemas (DTOs)
  - **`routes/`** - FastAPI route handlers organized by domain (e.g., `timeline.py`)
  - **`database.py`** - Database engine configuration and session management
  - **`storage.py`** - Storage abstraction layer with pluggable backends (Local/S3)
  - **`config.py`** - Pydantic Settings for environment-based configuration
  - **`main.py`** - FastAPI application initialization, middleware, and lifespan events
- **`tests/`** - Backend test suite (pytest)
- **`Dockerfile`** - Multi-stage Docker build for production
- **`requirements.txt`** - Python dependencies
- **`env.example`** - Template for environment variables

### Frontend Structure (`frontend/`)
- **`lib/`** - Main Dart/Flutter source code
  - **`models/`** - Data transfer objects (DTOs) matching backend schemas
  - **`services/`** - API clients and business logic (Provider pattern)
  - **`screens/`** - UI screens/pages (feature-based organization)
  - **`main.dart`** - Flutter application entry point
- **`test/`** - Frontend test suite (flutter_test)
- **`pubspec.yaml`** - Flutter dependencies and project metadata
- **`Dockerfile`** - Multi-stage build with Nginx for serving
- **`nginx.conf`** - Nginx configuration for Flutter web
- **`env.example`** - Template for environment variables

### Root Configuration
- **`docker-compose.yml`** - Orchestrates backend and frontend services
- **`.env`** - Root environment variables (ports, etc.)
- **`env.example`** - Template for root environment variables
- **`data/`** - Persistent SQLite database storage (Docker volume)
- **`media/`** - Uploaded files storage (Docker volume)
- **`README.md`** - Project overview and quick start guide
- **`.github/copilot-instructions.md`** - Detailed coding guidelines for AI assistants

---

## Build, Test, and Development Commands

### Backend Development

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests (when pytest is added)
pytest

# Type checking (when mypy is added)
mypy app/

# Linting (when ruff/flake8 is added)
ruff check app/
```

### Frontend Development

```bash
# Setup
cd frontend
flutter pub get

# Run on Chrome (web)
flutter run -d chrome

# Run on specific port
flutter run -d web-server --web-port 3000

# Run tests
flutter test

# Build for production
flutter build web

# Analyze code
flutter analyze
```

### Docker Development

```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Rebuild specific service
docker-compose up --build backend
```

---

## Coding Style & Naming Conventions

### Python (Backend)

- **Indentation**: 4 spaces (PEP 8)
- **Naming**:
  - `snake_case` for functions, variables, and module names
  - `PascalCase` for classes and Pydantic models
  - `UPPER_SNAKE_CASE` for constants
- **Type Hints**: Required for all function signatures
- **Docstrings**: Use for public functions and classes (Google style)
- **Imports**: Group by standard library, third-party, local (separated by blank lines)
- **Line Length**: 88 characters (Black formatter standard)

**Example:**
```python
from typing import Optional
from datetime import datetime

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from .models import TimelineItem
from .database import get_session

MAX_UPLOAD_SIZE = 10_000_000  # 10MB


async def get_timeline_item_by_id(
    item_id: int,
    session: Session = Depends(get_session)
) -> TimelineItem:
    """
    Retrieve a timeline item by its ID.
    
    Args:
        item_id: Unique identifier of the timeline item
        session: Database session (dependency injected)
        
    Returns:
        The requested timeline item
        
    Raises:
        HTTPException: If item not found (404)
    """
    item = session.get(TimelineItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Timeline item not found")
    return item
```

### Dart (Frontend)

- **Indentation**: 2 spaces (Dart convention)
- **Naming**:
  - `camelCase` for variables, functions, and parameters
  - `PascalCase` for classes, enums, and typedefs
  - `lowercase_with_underscores` for library and file names
- **Type Safety**: Avoid `dynamic`, use explicit types
- **Null Safety**: Properly use `?` and `!` operators
- **Documentation**: Use `///` for public APIs
- **Line Length**: 80 characters (dartfmt default)

**Example:**
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/timeline_item.dart';
import '../services/timeline_provider.dart';

/// Screen displaying the user's medical timeline.
class TimelineScreen extends StatefulWidget {
  const TimelineScreen({super.key});

  @override
  State<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends State<TimelineScreen> {
  @override
  void initState() {
    super.initState();
    // Fetch timeline on screen load
    Future.microtask(
      () => context.read<TimelineProvider>().fetchTimeline(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<TimelineProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        return ListView.builder(
          itemCount: provider.items.length,
          itemBuilder: (context, index) {
            final item = provider.items[index];
            return TimelineItemCard(item: item);
          },
        );
      },
    );
  }
}
```

### Environment Files

- **Never commit `.env` files** - only commit `.env.example` templates
- **Document all variables** with comments in `.env.example`
- **Use sensible defaults** for development
- **Validate required variables** at application startup

**Example (`backend/env.example`):**
```bash
# Database connection string
# SQLite: sqlite:///./data/medstory.db
# PostgreSQL: postgresql://user:password@localhost/medstory
DATABASE_URL=sqlite:///./data/medstory.db

# Storage backend: local or s3
STORAGE_TYPE=local

# Directory for uploaded media files (local storage only)
MEDIA_DIR=/app/media

# CORS allowed origins (comma-separated or * for all)
CORS_ORIGINS=http://localhost:3000
```

---

## Testing Guidelines

### Backend Testing (Python)

- **Framework**: `pytest` with `pytest-asyncio` for async tests
- **Location**: `backend/tests/`
- **Naming**: `test_*.py` (e.g., `test_timeline.py`, `test_storage.py`)
- **Test Database**: Use in-memory SQLite (`:memory:`) for isolation
- **Fixtures**: Create reusable fixtures in `conftest.py`
- **Coverage**: Aim for >80% code coverage

**Example:**
```python
# backend/tests/test_timeline.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import TimelineItem, ItemType


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden dependencies."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_status_item(client: TestClient):
    """Test creating a status timeline item."""
    response = client.post(
        "/api/timeline/",
        data={"type": "status", "text": "Feeling better today"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "status"
    assert data["text"] == "Feeling better today"
    assert "id" in data
    assert "created_at" in data


def test_list_timeline_items(client: TestClient, session: Session):
    """Test listing timeline items with pagination."""
    # Create test data
    for i in range(5):
        item = TimelineItem(type=ItemType.STATUS, text=f"Status {i}")
        session.add(item)
    session.commit()
    
    # Test pagination
    response = client.get("/api/timeline/?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
```

### Frontend Testing (Dart)

- **Framework**: `flutter_test` for widgets, `test` for unit tests
- **Location**: `frontend/test/`
- **Naming**: `*_test.dart` (e.g., `timeline_screen_test.dart`)
- **Mocking**: Use `mockito` or manual mocks for API clients
- **Widget Tests**: Test UI components in isolation
- **Integration Tests**: Test full user flows (optional)

**Example:**
```dart
// frontend/test/services/api_client_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'dart:convert';

import 'package:medstory/services/api_client.dart';

void main() {
  group('ApiClient', () {
    test('get() returns parsed JSON on success', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          json.encode([
            {'id': 1, 'type': 'status', 'text': 'Test', 'created_at': '2024-01-01T00:00:00Z'}
          ]),
          200,
        );
      });

      final apiClient = ApiClient(
        baseUrl: 'http://localhost:8000',
        client: mockClient,
      );

      final result = await apiClient.get('/api/timeline');
      expect(result, isA<List>());
      expect(result[0]['type'], equals('status'));
    });

    test('get() throws exception on error', () async {
      final mockClient = MockClient((request) async {
        return http.Response('Not Found', 404);
      });

      final apiClient = ApiClient(
        baseUrl: 'http://localhost:8000',
        client: mockClient,
      );

      expect(
        () => apiClient.get('/api/timeline'),
        throwsException,
      );
    });
  });
}
```

---

## Commit & Pull Request Guidelines

### Commit Messages

- **Format**: `<type>: <subject>` (imperative mood)
- **Types**: 
  - `feat`: New feature
  - `fix`: Bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, no logic change)
  - `refactor`: Code refactoring
  - `test`: Adding or updating tests
  - `chore`: Maintenance tasks (dependencies, config)
- **Subject**: Short (50 chars), capitalized, no period
- **Body**: Optional, explain *why* not *what*

**Examples:**
```
feat: Add pagination to timeline API endpoint
fix: Handle missing file extension in upload
docs: Update environment variable documentation
refactor: Extract storage logic into abstract service
test: Add unit tests for timeline creation
chore: Update FastAPI to version 0.109.0
```

### Pull Request Guidelines

1. **Reference issues**: Use `Fixes #123` or `Closes #456` in description
2. **Describe changes**: Explain what and why, not just how
3. **List breaking changes**: Highlight any API or schema changes
4. **Include screenshots**: For UI changes, attach before/after images
5. **Verify locally**: 
   - Backend: Run tests, check API docs at `/docs`
   - Frontend: Test on web, check console for errors
   - Docker: Verify `docker-compose up` works
6. **Update documentation**: Modify README or AGENTS.md if needed
7. **Check environment files**: Update `.env.example` if new variables added

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Tested locally with Docker
- [ ] API documentation updated

## Screenshots (if applicable)
[Attach images]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
```

---

## Database Migration Guidelines

### Schema Changes

When modifying database models:

1. **Document the change** in commit message and PR
2. **Consider backward compatibility** - can existing data be migrated?
3. **Provide migration script** if needed (future: use Alembic)
4. **Update model schemas** in both backend and frontend
5. **Test with existing data** to ensure no data loss

**Example Migration Pattern:**
```python
# Future: When using Alembic for migrations
# alembic revision --autogenerate -m "Add user_id to timeline items"

# Manual migration for now (SQLModel auto-creates tables)
# 1. Backup database: cp data/medstory.db data/medstory.db.backup
# 2. Update models.py
# 3. Delete database (dev only): rm data/medstory.db
# 4. Restart app (tables recreated)
```

### Adding New Models

```python
# 1. Define model in models.py
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# 2. Create Pydantic schemas
class UserCreate(SQLModel):
    email: str

class UserResponse(User):
    pass

# 3. Tables auto-created on app startup via create_db_and_tables()
```

---

## Security Best Practices

### Sensitive Data Handling

- **Never log PHI/PII**: Medical data, emails, names, etc.
- **Sanitize error messages**: Don't expose internal details to users
- **Validate all inputs**: Use Pydantic models for automatic validation
- **Use parameterized queries**: SQLModel handles this automatically
- **Implement rate limiting**: Prevent abuse (future enhancement)

### File Upload Security

```python
# ✅ Good: Validate and sanitize uploads
import uuid
import os
from pathlib import Path

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def upload_file(file: UploadFile) -> str:
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Validate extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Generate safe filename
    filename = f"{uuid.uuid4()}{ext}"
    
    # Save file
    # ... storage logic
    
    return filename
```

### Environment Variables

```python
# ✅ Good: Use Pydantic Settings with validation
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str  # Future: for JWT tokens
    
    @field_validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        return v
```

---

## Performance Optimization

### Backend Performance

- **Database Indexing**: Add indexes to frequently queried columns
  ```python
  class TimelineItem(SQLModel, table=True):
      user_id: int = Field(foreign_key="user.id", index=True)  # Future
      created_at: datetime = Field(index=True)  # For ordering
  ```

- **Query Optimization**: Use `select()` with specific columns when possible
  ```python
  # ✅ Good: Only select needed columns
  items = session.exec(
      select(TimelineItem.id, TimelineItem.text)
      .where(TimelineItem.type == ItemType.STATUS)
  ).all()
  ```

- **Pagination**: Always implement pagination for list endpoints
  ```python
  @router.get("/")
  def list_items(skip: int = 0, limit: int = 100):
      # Limit max page size
      limit = min(limit, 100)
      # ... query with offset/limit
  ```

- **Async Operations**: Use `async`/`await` for I/O operations
  ```python
  # ✅ Good: Async file operations
  async def upload_file(file: UploadFile):
      contents = await file.read()
      # ... process
  ```

### Frontend Performance

- **Lazy Loading**: Load images on demand
  ```dart
  Image.network(
    item.imageUrl,
    loadingBuilder: (context, child, loadingProgress) {
      if (loadingProgress == null) return child;
      return CircularProgressIndicator();
    },
  )
  ```

- **Const Constructors**: Use for immutable widgets
  ```dart
  const Text('Medical Timeline')  // ✅ Good
  ```

- **Provider Optimization**: Use `Consumer` only where needed
  ```dart
  // ✅ Good: Only rebuild specific widgets
  Consumer<TimelineProvider>(
    builder: (context, provider, child) => Text(provider.count),
  )
  ```

---

## Docker Best Practices

### Multi-Stage Builds

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Volume Management

```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data          # Database persistence
  - ./media:/app/media        # File uploads
  - ./backend/.env:/app/.env  # Environment config
```

### Health Checks

```yaml
# Future enhancement
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## AI Assistant Workflow Tips

### When Adding New Features

1. **Understand the domain**: Medical timeline, health data, privacy concerns
2. **Check existing patterns**: Look at `timeline.py` for route structure
3. **Follow the stack**: Backend (FastAPI) → Frontend (Flutter)
4. **Update both sides**: Model changes require backend + frontend updates
5. **Test thoroughly**: Medical data requires extra validation

### When Debugging

1. **Check environment variables**: Many issues stem from misconfiguration
2. **Verify CORS settings**: Common frontend-backend communication issue
3. **Check Docker logs**: `docker-compose logs -f backend`
4. **Test API directly**: Use FastAPI docs at `http://localhost:8000/docs`
5. **Validate file paths**: Ensure media directory exists and is writable

### When Refactoring

1. **Maintain backward compatibility**: Don't break existing APIs
2. **Update tests**: Ensure tests reflect new structure
3. **Document changes**: Update README and this file
4. **Consider migrations**: Database schema changes need careful handling
5. **Test with Docker**: Ensure `docker-compose up` still works

---

## Quick Reference

### Project Commands Cheat Sheet

```bash
# Development
docker-compose up --build              # Start all services
docker-compose logs -f backend         # View backend logs
docker-compose exec backend bash       # Access backend container
docker-compose down -v                 # Clean shutdown with volume removal

# Backend
cd backend && uvicorn app.main:app --reload
curl http://localhost:8000/docs        # API documentation

# Frontend  
cd frontend && flutter run -d chrome
flutter analyze                        # Static analysis
flutter test                           # Run tests

# Database
sqlite3 data/medstory.db               # Access SQLite database
.tables                                # List tables
.schema timelineitem                   # View schema
```

### Important File Paths

| Purpose | Backend | Frontend |
|---------|---------|----------|
| **Configuration** | `backend/app/config.py` | `frontend/lib/main.dart` |
| **Models** | `backend/app/models.py` | `frontend/lib/models/` |
| **API Routes** | `backend/app/routes/` | `frontend/lib/services/api_client.dart` |
| **Database** | `backend/app/database.py` | N/A |
| **Environment** | `backend/.env` | `frontend/.env` |
| **Dependencies** | `backend/requirements.txt` | `frontend/pubspec.yaml` |
| **Tests** | `backend/tests/` | `frontend/test/` |

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **CORS errors** | Check `CORS_ORIGINS` in `backend/.env` |
| **Database locked** | Ensure only one process accesses SQLite |
| **File upload fails** | Verify `MEDIA_DIR` exists and is writable |
| **Frontend can't connect** | Check `API_BASE_URL` in `frontend/.env` |
| **Docker build fails** | Run `docker-compose down -v` and rebuild |
| **Port already in use** | Change ports in root `.env` file |

---

## Summary for AI Assistants

**MedStory** is a medical timeline platform built with:
- **Backend**: FastAPI + SQLModel + Pydantic
- **Frontend**: Flutter Web + Provider
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Storage**: Local filesystem (dev) / S3 (future)

**Key Principles:**
1. **Security First**: Medical data requires HIPAA-compliant patterns
2. **Type Safety**: Use type hints (Python) and strong typing (Dart)
3. **Environment-Driven**: All config via environment variables
4. **Service Layer**: Separate business logic from routes/UI
5. **Test Coverage**: Write tests for critical functionality
6. **Documentation**: Keep README and AGENTS.md updated

**Before Making Changes:**
- ✅ Read existing code patterns
- ✅ Check `.github/copilot-instructions.md` for detailed guidelines
- ✅ Validate with tests
- ✅ Update documentation
- ✅ Test with Docker Compose

**Remember**: You're working with sensitive medical data. Always prioritize security, privacy, and data integrity.
