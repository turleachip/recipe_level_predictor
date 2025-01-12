from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from src.backend.api.main import app
from src.backend.api.database import Base, get_db

# テスト用のデータベースURL
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# テスト用のエンジンとセッション
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用のデータベース依存関係
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # テストの前にデータベースを作成
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # テストの後にデータベースを削除
    Base.metadata.drop_all(bind=engine)

def test_create_recipe(client):
    """レシピ作成のテスト"""
    recipe_data = {
        "name": "テストレシピ",
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
    assert data["data"]["name"] == recipe_data["name"]
    assert data["data"]["job"] == recipe_data["job"]
    assert "id" in data["data"]
    assert "collected_at" in data["data"]

def test_get_recipe(client):
    """レシピ取得のテスト"""
    # まずレシピを作成
    recipe_data = {
        "name": "テストレシピ",
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
    create_response = client.post("/recipes/", json=recipe_data)
    recipe_id = create_response.json()["data"]["id"]

    # 作成したレシピを取得
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == recipe_data["name"]
    assert data["data"]["job"] == recipe_data["job"]

def test_update_recipe(client):
    """レシピ更新のテスト"""
    # まずレシピを作成
    recipe_data = {
        "name": "テストレシピ",
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
    create_response = client.post("/recipes/", json=recipe_data)
    recipe_id = create_response.json()["data"]["id"]

    # レシピを更新
    update_data = {
        "name": "更新後のレシピ",
        "recipe_level": 91
    }
    response = client.put(f"/recipes/{recipe_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == update_data["name"]
    assert data["data"]["recipe_level"] == update_data["recipe_level"]
    assert data["data"]["job"] == recipe_data["job"]  # 更新していない項目は元の値のまま

def test_delete_recipe(client):
    """レシピ削除のテスト"""
    # まずレシピを作成
    recipe_data = {
        "name": "テストレシピ",
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
    create_response = client.post("/recipes/", json=recipe_data)
    recipe_id = create_response.json()["data"]["id"]

    # レシピを削除
    response = client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["success"] is True

    # 削除したレシピが取得できないことを確認
    get_response = client.get(f"/recipes/{recipe_id}")
    assert get_response.status_code == 404

def test_search_recipes(client):
    """レシピ検索のテスト"""
    # テストデータの作成
    recipes = [
        {
            "name": "テストレシピ1",
            "job": "CRP",
            "recipe_level": 85,
            "master_book_level": 1,
            "stars": 1,
            "patch_version": "6.4",
            "max_durability": 80,
            "max_quality": 100,
            "required_durability": 50,
            "required_craftsmanship": 3500,
            "required_control": 3200,
            "progress_per_100": 120,
            "quality_per_100": 100
        },
        {
            "name": "テストレシピ2",
            "job": "CRP",
            "recipe_level": 90,
            "master_book_level": 1,
            "stars": 1,
            "patch_version": "6.4",
            "max_durability": 80,
            "max_quality": 100,
            "required_durability": 50,
            "required_craftsmanship": 3500,
            "required_control": 3200,
            "progress_per_100": 120,
            "quality_per_100": 100
        }
    ]
    
    # レシピを登録
    for recipe in recipes:
        response = client.post("/recipes/", json=recipe)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "id" in response.json()["data"]

    # レシピレベルで検索
    response = client.get("/recipes/search", params={"min_level": "85", "max_level": "90"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]) == 2

    # レシピレベルで絞り込み検索
    response = client.get("/recipes/search", params={"min_level": "90"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]) == 1 