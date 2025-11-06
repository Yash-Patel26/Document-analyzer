# AI Document Analysis System

A complete self-hosted AI document analysis system with Flutter mobile app and Python backend.

## Features

- Document capture via camera or file picker
- OCR text extraction
- Entity extraction and summarization
- Interactive Q&A chat with documents
- Offline support with queue management
- Secure authentication and encryption
- Admin model management

## Project Structure

```
analyzer/
├── backend/          # Python FastAPI backend
├── mobile/          # Flutter mobile app
└── docs/            # Documentation
```

## Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Set up database:
```bash
alembic upgrade head
```

4. Run server:
```bash
python main.py
```

Or use Docker:
```bash
docker-compose up
```

## Mobile App Setup

1. Install Flutter dependencies:
```bash
cd mobile
flutter pub get
```

2. Run the app:
```bash
flutter run
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See [docs/API.md](docs/API.md) for detailed API documentation.

## Development

### Backend
- FastAPI for REST API
- PyTorch for AI models
- PostgreSQL for metadata
- FAISS for vector search

### Mobile
- Flutter with Riverpod for state management
- go_router for navigation
- sqflite for local storage
- flutter_secure_storage for secure token storage

## License

MIT

