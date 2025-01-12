import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from starlette.testclient import TestClient as StarletteTestClient

def create_test_app():
    """テスト用のFastAPIアプリケーションを作成"""
    app = FastAPI()
    
    from src.backend.api.middleware import setup_error_handlers
    setup_error_handlers(app)
    
    @app.get("/test_http_error")
    async def test_http_error():
        """HTTPエラーをテスト用に発生させる"""
        raise HTTPException(status_code=404, detail="Not found")
    
    @app.get("/test_database_error")
    async def test_database_error():
        """データベースエラーをテスト用に発生させる"""
        raise SQLAlchemyError("Database connection error")
    
    @app.get("/test_validation_error")
    async def test_validation_error():
        """バリデーションエラーをテスト用に発生させる"""
        raise ValueError("Invalid input")
    
    @app.get("/test_unexpected_error")
    async def test_unexpected_error():
        """予期せぬエラーをテスト用に発生させる"""
        raise RuntimeError("Unexpected error")
    
    return app

def test_http_exception_handling():
    """HTTPエラーのハンドリングをテスト"""
    app = create_test_app()
    client = StarletteTestClient(app)
    response = client.get("/test_http_error")
    assert response.status_code == 404
    data = response.json()
    assert not data["success"]
    assert data["error"]["code"] == 404
    assert data["error"]["message"] == "Not found"
    assert data["error"]["type"] == "http_error"

def test_database_error_handling():
    """データベースエラーのハンドリングをテスト"""
    app = create_test_app()
    client = StarletteTestClient(app)
    response = client.get("/test_database_error")
    assert response.status_code == 500
    data = response.json()
    assert not data["success"]
    assert data["error"]["code"] == 500
    assert data["error"]["message"] == "Database error occurred"
    assert data["error"]["type"] == "database_error"
    assert "Database connection error" in data["error"]["details"]["error"]

def test_validation_error_handling():
    """バリデーションエラーのハンドリングをテスト"""
    app = create_test_app()
    client = StarletteTestClient(app)
    response = client.get("/test_validation_error")
    assert response.status_code == 400
    data = response.json()
    assert not data["success"]
    assert data["error"]["code"] == 400
    assert data["error"]["message"] == "Invalid input"
    assert data["error"]["type"] == "value_error"

def test_unexpected_error_handling():
    """予期せぬエラーのハンドリングをテスト"""
    app = create_test_app()
    client = StarletteTestClient(app)
    response = client.get("/test_unexpected_error")
    assert response.status_code == 500
    data = response.json()
    assert not data["success"]
    assert data["error"]["code"] == 500
    assert data["error"]["message"] == "An unexpected error occurred"
    assert data["error"]["type"] == "internal_server_error"
    assert "Unexpected error" in data["error"]["details"]["error"] 