# MedStory Backend

This is the backend for the MedStory application, built with **FastAPI**.

## Prerequisites

- Python 3.12+
- Virtual environment (recommended)

## Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The application uses environment variables for configuration. You can create a `.env` file in the `backend/` directory or set them in your shell.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./medstory.db` |
| `STORAGE_TYPE` | Storage strategy (`local` or `s3`) | `local` |
| `MEDIA_DIR` | Directory for local file storage | `media` |

## Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## Testing

Run tests with pytest:

```bash
pytest
```
