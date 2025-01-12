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

def test_get_recipe():
    # テストデータの作成
    recipe_data = {
        "name": "テストレシピ詳細",
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
    
    # レシピを作成
    create_response = client.post("/recipes", json=recipe_data)
    assert create_response.status_code == 200
    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]

    # レシピ詳細の取得テスト
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()

    # データの検証
    assert data["id"] == recipe_id
    assert data["name"] == recipe_data["name"]
    assert data["job"] == recipe_data["job"]
    assert data["recipe_level"] == recipe_data["recipe_level"]
    assert data["master_book_level"] == recipe_data["master_book_level"]
    assert data["stars"] == recipe_data["stars"]
    assert data["patch_version"] == recipe_data["patch_version"]
    assert "collected_at" in data
    assert data["max_durability"] == recipe_data["max_durability"]
    assert data["max_quality"] == recipe_data["max_quality"]
    assert data["required_durability"] == recipe_data["required_durability"]
    assert data["required_craftsmanship"] == recipe_data["required_craftsmanship"]
    assert data["required_control"] == recipe_data["required_control"]
    assert data["progress_per_100"] == recipe_data["progress_per_100"]
    assert data["quality_per_100"] == recipe_data["quality_per_100"]

def test_get_recipe_not_found():
    # 存在しないIDでのテスト
    response = client.get("/recipes/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"

def test_update_recipe():
    # テストデータの作成
    recipe_data = {
        "name": "更新前のレシピ",
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
    
    # レシピを作成
    create_response = client.post("/recipes", json=recipe_data)
    assert create_response.status_code == 200
    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]

    # 部分的な更新データ
    update_data = {
        "name": "更新後のレシピ",
        "recipe_level": 95,
        "max_durability": 85
    }

    # レシピの更新
    response = client.put(f"/recipes/{recipe_id}", json=update_data)
    assert response.status_code == 200
    updated_recipe = response.json()

    # 更新されたフィールドの検証
    assert updated_recipe["name"] == update_data["name"]
    assert updated_recipe["recipe_level"] == update_data["recipe_level"]
    assert updated_recipe["max_durability"] == update_data["max_durability"]
    
    # 更新されていないフィールドの検証
    assert updated_recipe["job"] == recipe_data["job"]
    assert updated_recipe["stars"] == recipe_data["stars"]
    assert updated_recipe["quality_per_100"] == recipe_data["quality_per_100"]

def test_update_recipe_full():
    # テストデータの作成
    recipe_data = {
        "name": "全更新前のレシピ",
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
    
    # レシピを作成
    create_response = client.post("/recipes", json=recipe_data)
    assert create_response.status_code == 200
    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]

    # 全項目の更新データ
    update_data = {
        "name": "全更新後のレシピ",
        "job": "BSM",
        "recipe_level": 95,
        "master_book_level": 2,
        "stars": 3,
        "patch_version": "6.5",
        "max_durability": 85,
        "max_quality": 110,
        "required_durability": 55,
        "required_craftsmanship": 3100,
        "required_control": 3300,
        "progress_per_100": 125.5,
        "quality_per_100": 155.8
    }

    # レシピの更新
    response = client.put(f"/recipes/{recipe_id}", json=update_data)
    assert response.status_code == 200
    updated_recipe = response.json()

    # 全フィールドの検証
    for field in update_data:
        assert updated_recipe[field] == update_data[field]

def test_update_recipe_not_found():
    # 存在しないレシピの更新
    update_data = {"name": "存在しないレシピ"}
    response = client.put("/recipes/99999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"

def test_update_recipe_invalid_data():
    # テストデータの作成
    recipe_data = {
        "name": "無効なデータテスト用レシピ",
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
    
    # レシピを作成
    create_response = client.post("/recipes", json=recipe_data)
    assert create_response.status_code == 200
    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]

    # 無効なデータでの更新
    invalid_data = {
        "max_durability": -1,  # 無効な値（0より大きい値が必要）
        "required_control": 0   # 無効な値（0より大きい値が必要）
    }

    # レシピの更新を試行
    response = client.put(f"/recipes/{recipe_id}", json=invalid_data)
    assert response.status_code == 422  # バリデーションエラーは422
    error_detail = response.json()
    assert "detail" in error_detail  # エラー詳細が含まれていることを確認 

def test_delete_recipe():
    # テストデータの作成
    recipe_data = {
        "name": "削除用テストレシピ",
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
    
    # レシピを作成
    create_response = client.post("/recipes", json=recipe_data)
    assert create_response.status_code == 200
    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]

    # レシピの削除
    response = client.delete(f"/recipes/{recipe_id}")
    if response.status_code != 204:
        print("Error response:", response.json())
    assert response.status_code == 204

    # 削除されたことを確認
    get_response = client.get(f"/recipes/{recipe_id}")
    assert get_response.status_code == 404

def test_delete_recipe_not_found():
    # 存在しないレシピの削除
    response = client.delete("/recipes/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found" 

def test_search_recipes():
    # テストデータの作成
    recipes = [
        {
            "name": "ハイスチール・インゴット",
            "job": "BSM",
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
        },
        {
            "name": "ハイスチール・プレート",
            "job": "BSM",
            "recipe_level": 90,
            "master_book_level": 1,
            "stars": 2,
            "patch_version": "6.4",
            "max_durability": 80,
            "max_quality": 100,
            "required_durability": 50,
            "required_craftsmanship": 3100,
            "required_control": 3300,
            "progress_per_100": 120.5,
            "quality_per_100": 150.8
        },
        {
            "name": "クラフターズデライト・シロップ",
            "job": "ALC",
            "recipe_level": 88,
            "master_book_level": 0,
            "stars": 0,
            "patch_version": "6.4",
            "max_durability": 70,
            "max_quality": 90,
            "required_durability": 40,
            "required_craftsmanship": 2800,
            "required_control": 2900,
            "progress_per_100": 110.5,
            "quality_per_100": 140.8
        }
    ]

    # レシピを作成
    for recipe in recipes:
        response = client.post("/recipes", json=recipe)
        assert response.status_code == 200

    # 名前による検索
    response = client.get("/search/recipes?name=ハイスチール")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all("ハイスチール" in item["name"] for item in data["items"])

    # 職業による検索
    response = client.get("/search/recipes?job=BSM")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["job"] == "BSM" for item in data["items"])

    # レベル範囲による検索
    response = client.get("/search/recipes?min_level=89&max_level=90")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(89 <= item["recipe_level"] <= 90 for item in data["items"])

    # クラフター要求値による検索
    response = client.get("/search/recipes?min_craftsmanship=3000&max_control=3300")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["required_craftsmanship"] >= 3000 and item["required_control"] <= 3300 for item in data["items"])

def test_search_recipes_no_results():
    # 存在しないレシピ名での検索
    response = client.get("/search/recipes?name=存在しないレシピ")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0

def test_search_recipes_invalid_params():
    # 無効なレベル範囲での検索
    response = client.get("/search/recipes?min_level=-1")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

    # 無効なクラフター要求値での検索
    response = client.get("/search/recipes?min_craftsmanship=-100")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data 