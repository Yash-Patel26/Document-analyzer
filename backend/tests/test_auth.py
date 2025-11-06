"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register():
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()


def test_login():
    """Test user login."""
    # First register
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "testpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

