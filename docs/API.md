# API Documentation
user
## Authentication

### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "full_name": "Full Name"
}
```

### POST /auth/login
Login and get access tokens.

**Request Body:**
```json
{
  "username": "username",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer"
}
```

## Document Upload

### POST /upload/
Upload a document for analysis.

**Headers:**
- `Authorization: Bearer <access_token>`

**Request:**
- Multipart form data with `file` field

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2024-01-01T00:00:00"
}
```

## Jobs

### GET /jobs/{job_id}
Get job status.

### GET /jobs/{job_id}/result
Get analysis results.

### POST /jobs/{job_id}/analyze
Trigger analysis for a job.

## Chat

### POST /jobs/{job_id}/chat
Ask a question about a document.

**Request Body:**
```json
{
  "message": "What is this document about?"
}
```

### GET /jobs/{job_id}/chat/history
Get chat history for a job.

## Export

### GET /jobs/{job_id}/export?format=pdf|json|csv
Export analysis report.

## Admin

### POST /admin/retrain
Trigger model retraining (admin only).

### GET /admin/models
List model versions (admin only).

