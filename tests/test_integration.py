import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.api.main import app
from src.backend.api.database import Base, get_db
import os
import logging
import json
from datetime import datetime

# データベース接続URLを環境変数から構築
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
TEST_DB_NAME = "ff14_recipe_test"

if not MYSQL_PASSWORD:
    raise ValueError("MYSQL_PASSWORD environment variable is not set")

DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{TEST_DB_NAME}"

# テスト用のエンジンとセッション
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def client():
    # テストの前にデータベースを作成
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # テストの後にデータベースを削除
    Base.metadata.drop_all(bind=engine)

def test_complete_recipe_lifecycle(client):
    """レシピのライフサイクル全体をテストする"""
    # 1. レシピの作成
    recipe_data = {
        "name": "統合テストレシピ",
        "job": "CRP",
        "recipe_level": 90,
        "master_book_level": 1,
        "stars": 3,
        "patch_version": "6.4",
        "max_durability": 80,
        "max_quality": 100,
        "required_durability": 50,
        "required_craftsmanship": 3500,
        "required_control": 3200,
        "progress_per_100": 120,
        "quality_per_100": 100
    }
    
    response = client.post("/recipes/", json=recipe_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    recipe_id = data["data"]["id"]

    # 2. レシピの取得と検証
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == recipe_data["name"]

    # 3. レシピの更新
    update_data = {
        "name": "更新後の統合テストレシピ",
        "recipe_level": 91
    }
    response = client.put(f"/recipes/{recipe_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == update_data["name"]

    # 4. レシピの検索
    response = client.get("/recipes/search", params={
        "min_level": "90",
        "max_level": "91",
        "job": "CRP"
    })
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0

    # 5. レシピの削除
    response = client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # 6. 削除の確認
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 404

def test_error_handling_and_logging(client, tmp_path):
    """エラーハンドリングとロギングをテストする"""
    # ログファイルの設定
    log_file = tmp_path / "test.log"
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    # ログハンドラの設定
    file_handler = logging.FileHandler(str(log_file))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # ルートロガーにハンドラを追加
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    try:
        # 1. バリデーションエラー
        invalid_recipe = {
            "name": "無効なレシピ",
            "job": "INVALID",  # 無効なジョブコード
            "recipe_level": -1,  # 無効なレベル
            "patch_version": "invalid"  # 無効なバージョン形式
        }
        response = client.post("/recipes/", json=invalid_recipe)
        assert response.status_code == 400
        data = response.json()
        assert not data["success"]
        assert "validation_error" in str(data)

        # 2. 存在しないリソースへのアクセス
        response = client.get("/recipes/99999")
        assert response.status_code == 404
        data = response.json()
        assert not data["success"]
        assert data["error"]["type"] == "not_found"

        # 3. ログの検証
        with open(log_file, "r") as f:
            logs = f.readlines()
            validation_error_logged = any("validation_error" in line for line in logs)
            not_found_error_logged = any("Recipe not found" in line for line in logs)
            assert validation_error_logged
            assert not_found_error_logged
    finally:
        # クリーンアップ：ハンドラを削除
        root_logger.removeHandler(file_handler)
        file_handler.close()

def test_database_constraints(client):
    """データベースの制約をテストする"""
    # 1. 重複するレシピの作成（同じ名前と職業）
    recipe_data = {
        "name": "制約テストレシピ",
        "job": "CRP",
        "recipe_level": 90,
        "master_book_level": 1,
        "stars": 3,
        "patch_version": "6.4",
        "max_durability": 80,
        "max_quality": 100,
        "required_durability": 50,
        "required_craftsmanship": 3500,
        "required_control": 3200,
        "progress_per_100": 120,
        "quality_per_100": 100
    }
    
    # 1回目の作成（成功するはず）
    response = client.post("/recipes/", json=recipe_data)
    assert response.status_code == 200

    # 2回目の作成（一意性制約に違反するはず）
    response = client.post("/recipes/", json=recipe_data)
    assert response.status_code in [400, 409]  # 400 Bad Request または 409 Conflict

def test_performance(client):
    """基本的なパフォーマンステスト"""
    # 1. 複数のレシピを一括作成
    recipes = []
    for i in range(10):
        recipes.append({
            "name": f"パフォーマンステストレシピ{i}",
            "job": "CRP",
            "recipe_level": 90 + i,
            "master_book_level": 1,
            "stars": 3,
            "patch_version": "6.4",
            "max_durability": 80,
            "max_quality": 100,
            "required_durability": 50,
            "required_craftsmanship": 3500,
            "required_control": 3200,
            "progress_per_100": 120,
            "quality_per_100": 100
        })

    start_time = datetime.now()
    for recipe in recipes:
        response = client.post("/recipes/", json=recipe)
        assert response.status_code == 200

    # 2. 一括検索のパフォーマンス
    response = client.get("/recipes/", params={"limit": 100})
    assert response.status_code == 200
    end_time = datetime.now()

    # 全体の処理時間が3秒未満であることを確認
    duration = (end_time - start_time).total_seconds()
    assert duration < 3, f"Performance test took {duration} seconds" 