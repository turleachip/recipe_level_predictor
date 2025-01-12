from fastapi.testclient import TestClient
import pytest
from datetime import datetime
from src.backend.api.main import app
from src.backend.api.database import Base, engine
from sqlalchemy.sql import text

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    # テスト用データベースのセットアップ
    Base.metadata.create_all(bind=engine)
    yield
    # テスト後のクリーンアップ
    with engine.begin() as conn:
        # 外部キー制約を一時的に無効化
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        # テーブルの削除（外部キーを持つテーブルから順に削除）
        conn.execute(text("DROP TABLE IF EXISTS training_data"))
        conn.execute(text("DROP TABLE IF EXISTS recipe_stats"))
        conn.execute(text("DROP TABLE IF EXISTS inference_history"))
        conn.execute(text("DROP TABLE IF EXISTS recipes"))
        # 外部キー制約を再度有効化
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Recipe Level Predictor API"}

def test_create_recipe():
    recipe_data = {
        "name": "テストレシピ",
        "job": "CRP",
        "recipe_level": 90,
        "master_book_level": 1,
        "stars": 2,
        "patch_version": "6.4",
        "max_durability": 80,
        "max_quality": 100,
        "required_durability": 50,
        "required_craftsmanship": 3000,
        "required_control": 3200,
        "progress_per_100": 120.5,
        "quality_per_100": 150.8
    }

    response = client.post("/recipes", json=recipe_data)
    if response.status_code != 200:
        print("Error response:", response.json())
    assert response.status_code == 200
    data = response.json()
    
    # 基本情報の検証
    assert data["name"] == recipe_data["name"]
    assert data["job"] == recipe_data["job"]
    assert data["recipe_level"] == recipe_data["recipe_level"]
    assert "id" in data
    assert "collected_at" in data

def test_get_recipes():
    # テストデータの作成
    recipe_data = {
        "name": "テストレシピ1",
        "job": "CRP",
        "recipe_level": 90,
        "patch_version": "6.4",
        "max_durability": 80,
        "max_quality": 100,
        "required_durability": 50,
        "required_craftsmanship": 3000,
        "required_control": 3200,
        "progress_per_100": 120.5,
        "quality_per_100": 150.8
    }
    client.post("/recipes", json=recipe_data)

    # レシピ一覧の取得テスト
    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    
    # レスポンス構造の検証
    assert "total" in data
    assert "items" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    
    # データの検証
    assert data["total"] > 0
    assert len(data["items"]) > 0
    assert data["items"][0]["name"] == recipe_data["name"]

def test_get_recipes_with_filter():
    # フィルター用のテストデータを作成
    recipe_data1 = {
        "name": "CRP レシピ",
        "job": "CRP",
        "recipe_level": 90,
        "patch_version": "6.4",
        "max_durability": 80,
        "max_quality": 100,
        "required_durability": 50,
        "required_craftsmanship": 3000,
        "required_control": 3200,
        "progress_per_100": 120.5,
        "quality_per_100": 150.8
    }
    recipe_data2 = {
        "name": "BSM レシピ",
        "job": "BSM",
        "recipe_level": 80,
        "patch_version": "6.4",
        "max_durability": 80,
        "max_quality": 100,
        "required_durability": 50,
        "required_craftsmanship": 3000,
        "required_control": 3200,
        "progress_per_100": 120.5,
        "quality_per_100": 150.8
    }
    client.post("/recipes", json=recipe_data1)
    client.post("/recipes", json=recipe_data2)

    # フィルター付きで取得
    response = client.get("/recipes?job=CRP&min_level=85")
    assert response.status_code == 200
    data = response.json()
    
    # フィルター結果の検証
    assert data["total"] == 1
    assert data["items"][0]["job"] == "CRP"
    assert data["items"][0]["recipe_level"] >= 85 