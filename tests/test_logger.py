import pytest
from fastapi.testclient import TestClient
import json
import os
from datetime import datetime
from src.backend.api.main import app
from src.backend.api.logging_config import logger, ContextLogger, get_request_id, bind_request_context
from src.backend.api.database import set_test_db
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import asyncio
from httpx import AsyncClient

@pytest.fixture
def mock_db():
    """テスト用データベースセッションのモック"""
    mock_session = MagicMock(spec=Session)
    set_test_db(mock_session)
    yield mock_session
    set_test_db(None)

@pytest.fixture
async def async_client():
    """非同期テストクライアント"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

def find_log_entry(logs, message_pattern):
    """指定したパターンを含むログエントリを探す"""
    for log in reversed(logs):
        try:
            log_data = json.loads(log)
            if message_pattern in log_data.get("message", ""):
                return log_data
        except json.JSONDecodeError:
            continue
    return None

@pytest.mark.asyncio
async def test_log_file_creation():
    """ログファイルが正しく作成されることをテスト"""
    assert os.path.exists("logs/app.log"), "ログファイルが作成されていません"

@pytest.mark.asyncio
async def test_context_logger():
    """ContextLoggerの機能をテスト"""
    # コンテキスト情報の設定
    request_id = get_request_id()
    bind_request_context(
        logger,
        request_id=request_id,
        method="GET",
        path="/test",
        ip_address="127.0.0.1"
    )

    # ログ出力
    test_message = "テストメッセージ"
    logger.info(test_message)

    # ログファイルの内容を確認
    with open("logs/app.log", "r", encoding="utf-8") as f:
        logs = f.readlines()
        for log in reversed(logs):
            try:
                log_data = json.loads(log)
                if log_data.get("message") == test_message:
                    # 基本フィールドの確認
                    assert log_data["level"] == "INFO"
                    assert "timestamp" in log_data
                    assert "module" in log_data
                    assert "function" in log_data

                    # コンテキスト情報の確認
                    assert log_data["request_id"] == request_id
                    assert log_data["method"] == "GET"
                    assert log_data["path"] == "/test"
                    assert log_data["ip_address"] == "127.0.0.1"
                    break
            except json.JSONDecodeError:
                continue

@pytest.mark.asyncio
async def test_api_request_logging(mock_db, async_client):
    """APIリクエストのログ出力をテスト"""
    # テストリクエストの実行
    mock_db.query.return_value.count.return_value = 0
    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    
    response = await async_client.get("/recipes/")
    
    # ログファイルの内容を確認
    with open("logs/app.log", "r", encoding="utf-8") as f:
        logs = f.readlines()
        
        # リクエスト開始ログの確認
        start_log = find_log_entry(logs, "Request started: GET /recipes/")
        assert start_log is not None
        assert start_log["method"] == "GET"
        assert start_log["path"] == "/recipes/"
        assert "request_id" in start_log
        
        # レスポンス完了ログの確認
        complete_log = find_log_entry(logs, "Request completed: GET /recipes/")
        assert complete_log is not None
        assert "status_code" in complete_log
        assert "duration_ms" in complete_log
        assert complete_log["request_id"] == start_log["request_id"]

@pytest.mark.asyncio
async def test_error_logging(mock_db, async_client):
    """エラー時のログ出力をテスト"""
    # 存在しないレシピIDでリクエスト
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    response = await async_client.get("/recipes/99999")
    
    # ログファイルの内容を確認
    with open("logs/app.log", "r", encoding="utf-8") as f:
        logs = f.readlines()
        warning_log = find_log_entry(logs, "Recipe not found")
        
        assert warning_log is not None
        assert warning_log["level"] == "WARNING"
        assert warning_log["path"] == "/recipes/99999"
        assert "request_id" in warning_log

@pytest.mark.asyncio
async def test_validation_error_logging(mock_db, async_client):
    """バリデーションエラー時のログ出力をテスト"""
    # 不正なパラメータでリクエストを送信
    invalid_recipe = {
        "name": "テストレシピ",
        "job": "INVALID_JOB",  # 不正な職業名
        "recipe_level": -1,  # 不正なレベル値
        "patch_version": "6.0",
        "max_durability": 0,  # 不正な耐久値
        "max_quality": 0,
        "required_durability": 0,
        "required_craftsmanship": 0,
        "required_control": 0,
        "progress_per_100": 0,
        "quality_per_100": 0
    }
    
    response = await async_client.post("/recipes/", json=invalid_recipe)
    
    # ログファイルの内容を確認
    with open("logs/app.log", "r", encoding="utf-8") as f:
        logs = f.readlines()
        error_log = None
        for log in reversed(logs):
            try:
                log_data = json.loads(log)
                if "error_type" in log_data and log_data["error_type"] == "validation_error":
                    error_log = log_data
                    break
            except json.JSONDecodeError:
                continue
        
        assert error_log is not None
        assert error_log["level"] == "ERROR"
        assert error_log["path"] == "/recipes/"
        assert "request_id" in error_log
        assert "validation error" in str(error_log.get("error", "")).lower()

@pytest.mark.asyncio
async def test_database_error_logging(mock_db, async_client):
    """データベースエラー時のログ出力をテスト"""
    # データベースエラーをモック
    mock_db.query.side_effect = Exception("Database connection error")
    
    response = await async_client.get("/recipes/")
    
    # ログファイルの内容を確認
    with open("logs/app.log", "r", encoding="utf-8") as f:
        logs = f.readlines()
        error_log = find_log_entry(logs, "Unexpected error")
        
        assert error_log is not None
        assert error_log["level"] == "ERROR"
        assert "traceback" in error_log
        assert "Database connection error" in str(error_log.get("error", "")) 