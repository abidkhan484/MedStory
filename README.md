# MedStory

MedStory is a personal medical history preservation platform.

## Architecture

- **Backend**: Python FastAPI (Port 8000)
- **Frontend**: Flutter Web (Port 3000)
- **Database**: SQLite (default) or PostgreSQL
- **Storage**: Local Filesystem (default) or AWS S3

## Quick Start (Docker)

To run the entire application stack using Docker Compose:

1. Ensure Docker and Docker Compose are installed.
2. Run the following command from the root directory:

   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API Docs**: http://localhost:8000/docs

### Data Persistence

The Docker setup maps local directories for persistence:
- `./data`: Stores the SQLite database.
- `./media`: Stores uploaded files (when using `STORAGE_TYPE=local`).

## Manual Setup

If you prefer to run services individually without Docker, please refer to the README files in each directory:
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## AI Coding Assistant Support

This project includes comprehensive guidelines for AI coding assistants (GitHub Copilot, Jules, Antigravity, Cursor, etc.):

- **[AI Assistant Setup Guide](AI_ASSISTANT_SETUP.md)** - How to use AI tools with this project
- **[Copilot Instructions](.github/copilot-instructions.md)** - Detailed coding guidelines and patterns
- **[Agent Guidelines](AGENTS.md)** - Repository-wide development guidelines

These files help AI assistants understand the project structure, coding patterns, and security requirements for medical data handling.
