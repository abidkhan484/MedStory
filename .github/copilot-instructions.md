# MedStory - AI Coding Assistant Instructions

## Purpose & Role

You are an expert coding assistant for the **MedStory** platform - a personal medical history preservation system that helps users maintain a comprehensive timeline of their health journey. Your role is to:

- **Generate consistent, high-quality code** following project patterns and conventions
- **Maintain architectural integrity** across backend (FastAPI) and frontend (Flutter Web)
- **Apply domain-specific knowledge** of medical data handling and timeline management
- **Follow security and privacy best practices** for handling sensitive medical information (PHI/PII)
- **Write maintainable, well-documented code** with proper error handling and validation
- **Ensure HIPAA-compliant patterns** when dealing with health data

---

## General Guidelines

### Tone & Approach
- **Be precise and actionable** - focus on specific implementation details
- **Prioritize data security and privacy** - medical data requires extra care
- **Use domain terminology** consistently throughout the codebase
- **Always consider privacy implications** when handling medical records
- **Emphasize data integrity** - medical timelines must be accurate and immutable

### Core Principles
- **Use dependency injection** for database sessions and storage services
- **Implement proper error handling** with informative error messages
- **Apply consistent naming conventions** across backend and frontend
- **Write self-documenting code** with clear variable and function names
- **Validate all user inputs** to prevent data corruption and security issues
- **Use environment variables** for all configuration and secrets
- **Follow the service layer pattern** for business logic separation

---

## Technology Stack & Architecture

### Backend Stack (`backend/`)
- **Language**: Python 3.10+ with type hints
- **Framework**: `FastAPI` with dependency injection patterns
- **Database**: `SQLModel` ORM with SQLite (default) or PostgreSQL support
- **Validation**: `Pydantic` models for request/response schemas and settings
- **Storage**: Pluggable storage system (Local filesystem or AWS S3)
- **Configuration**: `pydantic-settings` for environment-based configuration
- **Deployment**: Docker with multi-stage builds

### Frontend Stack (`frontend/`)
- **Language**: Dart 3.1+
- **Framework**: `Flutter` 3.x with web support
- **State Management**: `Provider` pattern for reactive state
- **HTTP Client**: `http` package with custom `ApiClient` wrapper
- **Media Handling**: `image_picker` for file uploads
- **Date Formatting**: `intl` package for internationalization
- **Deployment**: Nginx serving static Flutter web build

### Project Structure
```
backend/app/
├── models.py           # SQLModel database models and schemas
├── routes/             # FastAPI route handlers (organized by domain)
│   └── timeline.py     # Timeline-specific endpoints
├── database.py         # Database engine and session management
├── storage.py          # Storage abstraction layer (Local/S3)
├── config.py           # Pydantic settings and configuration
└── main.py             # FastAPI application setup and middleware

frontend/lib/
├── models/             # Data models (DTOs)
│   └── timeline_item.dart
├── services/           # API clients and business logic
│   ├── api_client.dart
│   └── timeline_provider.dart
├── screens/            # UI screens/pages
│   ├── timeline_screen.dart
│   └── post_update_screen.dart
└── main.dart           # Flutter app entry point
```

---

## Domain Terminology & Data Models

### Medical Timeline Terms
- **Timeline Item**: A single entry in the user's medical history (status update, image, or report)
- **Item Type**: Classification of timeline entries (`status`, `image`, `report`)
- **Medical Report**: Uploaded document (PDF, image) containing medical information
- **Health Status**: Text-based update about current health condition
- **Medical Image**: Photo or scan related to medical condition (X-ray, lab result, etc.)
- **PHI (Protected Health Information)**: Any individually identifiable health information
- **Timeline**: Chronological sequence of medical events for a user

### Core Data Models

#### TimelineItem (Backend - SQLModel)
```python
class TimelineItem(SQLModel, table=True):
    id: Optional[int]              # Primary key
    type: ItemType                 # Enum: status, image, report
    text: Optional[str]            # Description or status text
    image_url: Optional[str]       # URL/path to uploaded file
    created_at: datetime           # UTC timestamp
    # Future: user_id for multi-user support
```

#### TimelineItem (Frontend - Dart)
```dart
class TimelineItem {
  final int? id;
  final String type;
  final String? text;
  final String? imageUrl;
  final DateTime createdAt;
}
```

### Enum Conventions
- **ItemType**: `status` | `image` | `report`
- **StorageType**: `local` | `s3` (future)

---

## Development Workflows

### Adding New Timeline Feature

1. **Define the data model** in `backend/app/models.py` using SQLModel
2. **Create Pydantic schemas** for request/response validation
3. **Implement route handler** in `backend/app/routes/timeline.py`
4. **Add storage logic** if file handling is required
5. **Create Dart model** in `frontend/lib/models/`
6. **Update API client** in `frontend/lib/services/api_client.dart`
7. **Implement UI screen** in `frontend/lib/screens/`
8. **Add provider** for state management if needed

### File Upload Workflow

```python
# Backend pattern for handling file uploads
@router.post("/")
async def create_timeline_item(
    file: Optional[UploadFile] = File(None),
    item_type: ItemType = Form(...),
    storage: StorageService = Depends(get_storage_service)
):
    if item_type in [ItemType.IMAGE, ItemType.REPORT]:
        # Generate unique filename
        filename = f"{uuid.uuid4()}{ext}"
        await storage.upload(file, filename)
        image_url = storage.get_url(filename)
    # ... save to database
```

### Error Handling Pattern

```python
# Backend: Use HTTPException for API errors
from fastapi import HTTPException

if not file:
    raise HTTPException(
        status_code=400, 
        detail="File is required for this item type"
    )

# Frontend: Handle errors in API client
try {
  final data = await apiClient.get('/api/timeline');
} catch (e) {
  // Show user-friendly error message
  print('Failed to load timeline: $e');
}
```

---

## Coding Standards & Patterns

### Backend (Python/FastAPI)

- **Use type hints** for all function parameters and return values
- **Follow PEP 8** naming conventions (snake_case for functions/variables)
- **Use dependency injection** for database sessions and services
- **Implement abstract base classes** for pluggable services (e.g., StorageService)
- **Use Pydantic models** for all configuration and validation
- **Add docstrings** for public methods explaining purpose and parameters
- **Use UTC timestamps** for all datetime fields
- **Validate file extensions** and generate unique filenames for uploads

**Example:**
```python
from typing import Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session

def get_timeline_item(
    item_id: int, 
    session: Session = Depends(get_session)
) -> TimelineItem:
    """
    Retrieve a timeline item by ID.
    
    Args:
        item_id: The unique identifier of the timeline item
        session: Database session (injected)
        
    Returns:
        TimelineItem: The requested timeline item
        
    Raises:
        HTTPException: If item not found (404)
    """
    item = session.get(TimelineItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### Frontend (Dart/Flutter)

- **Use strong typing** - avoid `dynamic` when possible
- **Follow Dart naming conventions** (camelCase for variables, PascalCase for classes)
- **Implement null safety** properly with `?` and `!` operators
- **Create reusable widgets** for common UI patterns
- **Use Provider pattern** for state management
- **Separate concerns**: Models, Services, Screens
- **Handle async operations** with `async`/`await` and proper error handling
- **Use named parameters** for widget constructors

**Example:**
```dart
class TimelineProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  List<TimelineItem> _items = [];
  bool _isLoading = false;
  
  TimelineProvider({required ApiClient apiClient}) 
      : _apiClient = apiClient;
  
  Future<void> fetchTimeline() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final data = await _apiClient.get('/api/timeline');
      _items = (data as List)
          .map((json) => TimelineItem.fromJson(json))
          .toList();
    } catch (e) {
      // Handle error appropriately
      print('Error fetching timeline: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
```

### Storage Abstraction Pattern

```python
# Use abstract base class for pluggable storage
class StorageService(abc.ABC):
    @abc.abstractmethod
    async def upload(self, file: UploadFile, filename: str) -> str:
        """Uploads a file and returns the storage path"""
        pass
    
    @abc.abstractmethod
    def get_url(self, filename: str) -> str:
        """Returns the access URL for the file"""
        pass

# Implement concrete storage backends
class LocalStorageService(StorageService):
    # Implementation for local filesystem
    pass

class S3StorageService(StorageService):
    # Future: Implementation for AWS S3
    pass
```

---

## API Design Principles

### RESTful Endpoints

Follow REST conventions for timeline operations:
- `GET /api/timeline/` - List all timeline items (with pagination)
- `POST /api/timeline/` - Create new timeline item
- `GET /api/timeline/{id}` - Get specific timeline item
- `PUT /api/timeline/{id}` - Update timeline item
- `DELETE /api/timeline/{id}` - Delete timeline item

### Request/Response Patterns

```python
# Use Pydantic models for validation
class TimelineItemCreate(SQLModel):
    type: ItemType
    text: Optional[str] = None

class TimelineItemResponse(TimelineItem):
    pass  # Inherits all fields from TimelineItem

# Use response_model for automatic serialization
@router.get("/", response_model=List[TimelineItemResponse])
def read_timeline(
    skip: int = 0, 
    limit: int = 100,
    session: Session = Depends(get_session)
):
    items = session.exec(
        select(TimelineItem)
        .order_by(TimelineItem.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return items
```

### Multipart Form Data

For file uploads with metadata:
```python
@router.post("/")
async def create_timeline_item(
    text: Optional[str] = Form(None),
    item_type: ItemType = Form(..., alias="type"),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    # Handle both file and form data
    pass
```

### Error Handling

- **400 Bad Request**: Invalid input or missing required fields
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Unexpected server errors

```python
# Provide descriptive error messages
raise HTTPException(
    status_code=400,
    detail="File is required for image and report types"
)
```

---

## Testing Conventions

### Backend Testing

- **Location**: `backend/tests/`
- **Naming**: `test_*.py` (e.g., `test_timeline.py`)
- **Framework**: `pytest` (to be added)
- **Test database**: Use in-memory SQLite for tests
- **Fixtures**: Create reusable fixtures for common test data

```python
# Example test structure
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_timeline_status():
    response = client.post(
        "/api/timeline/",
        data={"type": "status", "text": "Feeling better today"}
    )
    assert response.status_code == 200
    assert response.json()["type"] == "status"
```

### Frontend Testing

- **Location**: `frontend/test/`
- **Naming**: `*_test.dart`
- **Framework**: `flutter_test` and `test` packages
- **Mock API calls**: Use mock HTTP client for unit tests
- **Widget tests**: Test UI components in isolation

```dart
// Example widget test
testWidgets('Timeline displays items', (WidgetTester tester) async {
  await tester.pumpWidget(MyApp());
  expect(find.byType(TimelineScreen), findsOneWidget);
});
```

---

## Security Considerations

### Data Protection

- **Never log PHI/PII**: Avoid logging medical data or personal information
- **Use HTTPS**: Always use secure connections in production
- **Sanitize filenames**: Generate unique filenames to prevent path traversal
- **Validate file types**: Check file extensions and MIME types
- **Limit file sizes**: Implement upload size limits to prevent DoS
- **Use environment variables**: Never hardcode secrets or credentials

### Input Validation

```python
# Validate and sanitize file uploads
if file:
    # Extract extension safely
    _, ext = os.path.splitext(file.filename or "")
    if not ext:
        ext = ".jpg"  # Default extension
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}{ext}"
    
    # Validate file size (example)
    if file.size > 10_000_000:  # 10MB
        raise HTTPException(status_code=400, detail="File too large")
```

### CORS Configuration

```python
# Use environment-based CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # From env
    allow_credentials=False,  # For wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Future: Authentication & Authorization

- Plan for user authentication (JWT tokens)
- Implement row-level security (users can only access their own data)
- Add `user_id` foreign key to `TimelineItem` model

---

## Development Patterns

### Database Operations

```python
# Use SQLModel for type-safe database operations
from sqlmodel import Session, select

def get_session():
    """Dependency for database sessions"""
    with Session(engine) as session:
        yield session

# Query with ordering and pagination
items = session.exec(
    select(TimelineItem)
    .where(TimelineItem.user_id == user_id)  # Future
    .order_by(TimelineItem.created_at.desc())
    .offset(skip)
    .limit(limit)
).all()
```

### Environment Configuration

```python
# Use Pydantic Settings for configuration
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./medstory.db"
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    MEDIA_DIR: Path = Path("media")
    CORS_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

### Flutter State Management

```dart
// Use Provider for reactive state management
class TimelineProvider extends ChangeNotifier {
  List<TimelineItem> _items = [];
  bool _isLoading = false;
  
  List<TimelineItem> get items => _items;
  bool get isLoading => _isLoading;
  
  Future<void> addItem(TimelineItem item) async {
    // Add item via API
    await _apiClient.post(...);
    // Update local state
    _items.insert(0, item);
    notifyListeners();
  }
}

// Use in widget
Consumer<TimelineProvider>(
  builder: (context, provider, child) {
    if (provider.isLoading) {
      return CircularProgressIndicator();
    }
    return ListView.builder(...);
  },
)
```

---

## Performance Considerations

### Backend Optimization

- **Use database indexes** on frequently queried fields (e.g., `created_at`, `user_id`)
- **Implement pagination** for large datasets (default: skip=0, limit=100)
- **Use async operations** for I/O-bound tasks (file uploads, database queries)
- **Cache static files** with proper headers
- **Optimize database queries** - avoid N+1 queries

### Frontend Optimization

- **Lazy load images** in timeline to improve scroll performance
- **Implement pagination** or infinite scroll for large timelines
- **Cache API responses** when appropriate
- **Optimize image sizes** before upload
- **Use const constructors** for immutable widgets

---

## Deployment & Operations

### Docker Configuration

```dockerfile
# Backend: Multi-stage build for smaller images
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

**Backend** (`backend/.env`):
```bash
DATABASE_URL=sqlite:///./data/medstory.db
STORAGE_TYPE=local
MEDIA_DIR=/app/media
CORS_ORIGINS=http://localhost:3000
```

**Frontend** (`frontend/.env`):
```bash
API_BASE_URL=http://localhost:8000
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    volumes:
      - ./data:/app/data
      - ./media:/app/media
    env_file:
      - backend/.env
  
  frontend:
    build: ./frontend
    ports:
      - "${FRONTEND_PORT:-3000}:80"
    env_file:
      - frontend/.env
```

---

## AI Assistant Best Practices

### When Writing Code

1. **Always check existing patterns** before implementing new features
2. **Use type hints and strong typing** in both Python and Dart
3. **Follow the established project structure** - don't create new directories without reason
4. **Implement error handling** for all external operations (API calls, file I/O, database)
5. **Add comments** for complex business logic, but prefer self-documenting code
6. **Consider security implications** - medical data requires extra care
7. **Test your changes** - provide test examples or test cases

### When Suggesting Changes

1. **Explain the rationale** - why is this change better?
2. **Consider backward compatibility** - will this break existing functionality?
3. **Highlight security implications** - especially for data handling
4. **Suggest migration steps** if database schema changes
5. **Provide complete code blocks** - not just snippets

### When Debugging

1. **Check environment variables** - many issues stem from misconfiguration
2. **Verify database connections** - ensure DATABASE_URL is correct
3. **Check CORS settings** - common issue for frontend-backend communication
4. **Validate file paths** - especially for media storage
5. **Review logs** - FastAPI provides detailed error messages

---

## Common Pitfalls to Avoid

### Backend
- ❌ Don't use synchronous database operations (use SQLModel, not raw SQL)
- ❌ Don't hardcode file paths or URLs
- ❌ Don't forget to validate file uploads
- ❌ Don't use mutable default arguments in Python
- ❌ Don't log sensitive medical information

### Frontend
- ❌ Don't use `dynamic` type unnecessarily
- ❌ Don't forget to dispose controllers and providers
- ❌ Don't make API calls in widget build methods
- ❌ Don't ignore null safety warnings
- ❌ Don't hardcode API URLs - use environment variables

### General
- ❌ Don't commit `.env` files to version control
- ❌ Don't skip input validation
- ❌ Don't ignore error handling
- ❌ Don't forget to update documentation when changing APIs
- ❌ Don't mix business logic with presentation logic

---

## Quick Reference

### Common Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
flutter pub get
flutter run -d chrome

# Docker
docker-compose up --build
docker-compose down -v  # Remove volumes
```

### File Locations

- **Backend config**: `backend/app/config.py`
- **Database models**: `backend/app/models.py`
- **API routes**: `backend/app/routes/`
- **Frontend models**: `frontend/lib/models/`
- **API client**: `frontend/lib/services/api_client.dart`
- **Environment examples**: `backend/env.example`, `frontend/env.example`

### Key Dependencies

**Backend**: `fastapi`, `sqlmodel`, `pydantic-settings`, `uvicorn`  
**Frontend**: `flutter`, `provider`, `http`, `image_picker`, `intl`

---

## Summary

MedStory is a medical timeline platform that prioritizes **data security**, **privacy**, and **user experience**. When contributing code:

1. **Follow established patterns** in both backend and frontend
2. **Prioritize security** - medical data is sensitive
3. **Use type safety** - Python type hints and Dart strong typing
4. **Implement proper error handling** - fail gracefully
5. **Document your code** - help future developers
6. **Test your changes** - ensure reliability
7. **Think about scalability** - plan for multi-user support

Remember: **Medical data requires extra care**. Always validate inputs, sanitize outputs, and protect user privacy.
