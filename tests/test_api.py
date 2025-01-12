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
    assert data["name"] == recipe_data["name"]
    assert data["job"] == recipe_data["job"]
    assert "id" in data
    assert "collected_at" in data

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
    recipe_id = create_response.json()["id"]

    # 作成したレシピを取得
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == recipe_data["name"]
    assert data["job"] == recipe_data["job"]

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
    recipe_id = create_response.json()["id"]

    # レシピを更新
    update_data = {
        "name": "更新後のレシピ",
        "recipe_level": 91
    }
    response = client.put(f"/recipes/{recipe_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["recipe_level"] == update_data["recipe_level"]
    assert data["job"] == recipe_data["job"]  # 更新していない項目は元の値のまま

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
    recipe_id = create_response.json()["id"]

    # レシピを削除
    response = client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

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
            "master_book_level": 0,
            "stars": 0,
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
            "master_book_level": 0,
            "stars": 0,
            "patch_version": "6.4",
            "max_durability": 80,
            "max_quality": 100,
            "required_durability": 50,
            "required_craftsmanship": 3800,
            "required_control": 3500,
            "progress_per_100": 120,
            "quality_per_100": 100
        }
    ]

    for recipe_data in recipes:
        response = client.post("/recipes/", json=recipe_data)
        assert response.status_code == 200

    # レシピの検索
    search_params = {
        "min_level": "85",
        "max_level": "90",
        "job": "CRP",
        "min_craftsmanship": "3000",
        "max_craftsmanship": "4000"
    }
    response = client.get("/recipes/search", params=search_params)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "テストレシピ1" 