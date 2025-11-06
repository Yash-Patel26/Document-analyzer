# AI Document Analysis Backend

Backend API for the AI Document Analysis System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Set up PostgreSQL database and update `DATABASE_URL` in `.env`

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
python main.py
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

