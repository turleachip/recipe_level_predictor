import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.mysql_connector import MySQLConnector
from typing import Dict

class TestResult:
    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.details: Dict[str, str] = {}
    
    def add_result(self, test_name: str, success: bool, detail: str = ""):
        self.results[test_name] = success
        if detail:
            self.details[test_name] = detail
    
    def print_summary(self):
        print("\n=== テスト結果サマリー ===")
        total = len(self.results)
        success = sum(1 for result in self.results.values() if result)
        
        print(f"実行したテスト数: {total}")
        print(f"成功: {success}")
        print(f"失敗: {total - success}")
        
        print("\n詳細:")
        for name, result in self.results.items():
            status = "✅" if result else "❌"
            print(f"{status} {name}")
            if name in self.details:
                print(f"   └ {self.details[name]}")

def test_connection():
    """データベース接続テスト"""
    # コネクタのインスタンス作成（環境変数から自動で設定を読み込み）
    connector = MySQLConnector()
    
    # 接続テスト
    try:
        success = connector.connect()
        if success:
            print("✅ データベース接続成功")
            
            # 接続情報の確認
            if connector.connection.is_connected():
                db_info = connector.connection.get_server_info()
                print(f"📊 MySQL Server version: {db_info}")
                
                cursor = connector.connection.cursor()
                cursor.execute("SELECT DATABASE();")
                db_name = cursor.fetchone()[0]
                print(f"🗄️ データベース名: {db_name}")
                cursor.close()
        else:
            print("❌ データベース接続失敗")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        
    finally:
        # 接続を閉じる
        connector.disconnect()
        print("🔌 接続を閉じました")

def test_recipe_operations():
    """レシピ操作のテスト"""
    connector = MySQLConnector()
    
    try:
        # テスト用レシピの登録
        test_recipe = {
            'name': 'テスト用ハイスチール・インゴット',
            'job': 'BSM',
            'recipe_level': 90,
            'master_book_level': 0,
            'stars': 0,
            'patch_version': '6.4'
        }
        
        print("\n📝 レシピ登録テスト")
        print(f"登録するレシピ: {test_recipe['name']}")
        recipe_id = connector.insert_recipe(**test_recipe)
        
        if recipe_id:
            print(f"✅ レシピ登録成功（ID: {recipe_id}）")
            
            # 登録したレシピの確認
            query = "SELECT * FROM recipes WHERE id = %s"
            result = connector.execute_query(query, (recipe_id,))
            
            if result and len(result) > 0:
                recipe = result[0]
                print("\n📊 登録されたレシピ情報:")
                print(f"ID: {recipe[0]}")
                print(f"名前: {recipe[1]}")
                print(f"職種: {recipe[2]}")
                print(f"レベル: {recipe[3]}")
                print(f"秘伝書: {recipe[4]}")
                print(f"★数: {recipe[5]}")
                print(f"パッチ: {recipe[6]}")
                print(f"収集日時: {recipe[7]}")
                
                # テストデータのクリーンアップ
                cleanup_query = "DELETE FROM recipes WHERE id = %s"
                connector.execute_query(cleanup_query, (recipe_id,))
                print("\n🧹 テストデータを削除しました")
            else:
                print("❌ 登録したレシピの取得に失敗")
        else:
            print("❌ レシピ登録に失敗")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        
    finally:
        connector.disconnect()
        print("🔌 接続を閉じました")

def test_full_recipe_registration():
    """レシピの完全な登録テスト"""
    connector = MySQLConnector()
    result = TestResult()
    
    try:
        # 1. テスト用レシピの基本情報を登録
        test_recipe = {
            'name': 'テスト用ハイスチール・インゴット',
            'job': 'BSM',
            'recipe_level': 90,
            'master_book_level': 0,
            'stars': 0,
            'patch_version': '6.4'
        }
        
        recipe_id = connector.insert_recipe(**test_recipe)
        result.add_result("レシピ基本情報の登録", bool(recipe_id), 
                         f"登録ID: {recipe_id}" if recipe_id else "登録失敗")
        
        if recipe_id:
            # 2. レシピ作業情報の登録
            stats_success = connector.insert_recipe_stats(
                recipe_id=recipe_id,
                max_durability=70,
                max_quality=12000,
                required_durability=70
            )
            result.add_result("レシピ作業情報の登録", stats_success)
            
            # 3. 学習データの登録
            training_success = connector.insert_training_data(
                recipe_id=recipe_id,
                required_craftsmanship=3200,
                required_control=3000,
                progress_per_100=250,
                quality_per_100=250
            )
            result.add_result("学習データの登録", training_success)
            
            # クリーンアップ
            cleanup_success = True
            try:
                connector.execute_query("DELETE FROM training_data WHERE id = %s", (recipe_id,))
                connector.execute_query("DELETE FROM recipe_stats WHERE id = %s", (recipe_id,))
                connector.execute_query("DELETE FROM recipes WHERE id = %s", (recipe_id,))
            except Exception as e:
                cleanup_success = False
            
            result.add_result("テストデータのクリーンアップ", cleanup_success)
            
    except Exception as e:
        result.add_result("テスト全体", False, f"エラー: {str(e)}")
        
    finally:
        connector.disconnect()
        return result

def test_search_and_bulk_insert():
    """検索機能と一括登録機能のテスト"""
    connector = MySQLConnector()
    result = TestResult()
    
    try:
        # テスト用レシピデータ
        test_recipes = [
            {
                'name': 'テスト用ハイスチール・インゴット',
                'job': 'BSM',
                'recipe_level': 90,
                'master_book_level': 0,
                'stars': 0,
                'patch_version': '6.4',
                'max_durability': 70,
                'max_quality': 12000,
                'required_durability': 70,
                'required_craftsmanship': 3200,
                'required_control': 3000,
                'progress_per_100': 250,
                'quality_per_100': 250
            },
            {
                'name': 'テスト用チタンインゴット',
                'job': 'BSM',
                'recipe_level': 88,
                'master_book_level': 0,
                'stars': 0,
                'patch_version': '6.4',
                'max_durability': 70,
                'max_quality': 11000,
                'required_durability': 70,
                'required_craftsmanship': 3100,
                'required_control': 2900,
                'progress_per_100': 240,
                'quality_per_100': 240
            }
        ]
        
        # 1. 一括登録テスト
        registered_ids = connector.bulk_insert_recipes(test_recipes)
        result.add_result("レシピの一括登録", 
                         len(registered_ids) == len(test_recipes),
                         f"登録成功: {len(registered_ids)}/{len(test_recipes)}")
        
        # 2. 検索テスト
        search_results = connector.search_recipes(job='BSM', recipe_level=90)
        result.add_result("レシピの検索",
                         len(search_results) > 0,
                         f"検索結果: {len(search_results)}件")
        
        # 3. クリーンアップ
        cleanup_success = True
        try:
            for recipe_id in registered_ids:
                connector.execute_query("DELETE FROM training_data WHERE id = %s", (recipe_id,))
                connector.execute_query("DELETE FROM recipe_stats WHERE id = %s", (recipe_id,))
                connector.execute_query("DELETE FROM recipes WHERE id = %s", (recipe_id,))
        except Exception as e:
            cleanup_success = False
            
        result.add_result("テストデータのクリーンアップ", cleanup_success)
        
    except Exception as e:
        result.add_result("テスト全体", False, f"エラー: {str(e)}")
        
    finally:
        connector.disconnect()
        return result

if __name__ == "__main__":
    print("=== 検索・一括登録テスト ===")
    test_result = test_search_and_bulk_insert()
    test_result.print_summary() 