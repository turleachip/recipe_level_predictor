from typing import Dict, List, Any, Optional, Union
import mysql.connector
from mysql.connector import Error
import logging
from dotenv import load_dotenv
import os

class MySQLConnector:
    def __init__(self):
        """データベース接続用クラスの初期化"""
        # .envファイルから環境変数を読み込み
        load_dotenv()
        
        # 環境変数から接続情報を取得
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.database = os.getenv('MYSQL_DATABASE', 'ff14_recipe_level_predictor')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.connection = None
        
        if not self.password:
            raise ValueError("Database password not set in environment variables")
    
    def connect(self) -> bool:
        """データベースに接続
        
        Returns:
            bool: 接続成功ならTrue
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            return False
            
    def disconnect(self):
        """データベース接続を閉じる"""
        if self.connection and self.connection.is_connected():
            self.connection.close() 
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[tuple]]:
        """SQLクエリを実行し、結果を返す
        
        Args:
            query: 実行するSQLクエリ
            params: クエリパラメータ（プリペアドステートメント用）
            
        Returns:
            Optional[List[tuple]]: SELECT文の場合は結果を返す、それ以外はNone
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return None
                
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return None
    
    def insert_recipe(self, name: str, job: str, recipe_level: int,
                     master_book_level: int = 0, stars: int = 0,
                     patch_version: str = '6.4') -> Optional[int]:
        """レシピを登録する
        
        Args:
            name: レシピ名
            job: クラフター職種
            recipe_level: レシピレベル
            master_book_level: 秘伝書レベル（デフォルト：0）
            stars: ☆の数（デフォルト：0）
            patch_version: パッチバージョン（デフォルト：6.4）
            
        Returns:
            Optional[int]: 登録されたレシピのID。失敗時はNone
        """
        query = """
        INSERT INTO recipes (name, job, recipe_level, master_book_level, stars, 
                           patch_version, collected_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        params = (name, job, recipe_level, master_book_level, stars, patch_version)
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            
            recipe_id = cursor.lastrowid
            cursor.close()
            return recipe_id
            
        except Error as e:
            logging.error(f"Error inserting recipe: {e}")
            return None 
    
    def insert_recipe_stats(self, recipe_id: int, max_durability: int,
                           max_quality: int, required_durability: int) -> bool:
        """レシピの作業情報を登録する
        
        Args:
            recipe_id: レシピID（recipesテーブルの外部キー）
            max_durability: 最大工数
            max_quality: 最大品質
            required_durability: 必要工数
            
        Returns:
            bool: 登録成功ならTrue
        """
        query = """
        INSERT INTO recipe_stats (id, max_durability, max_quality, required_durability)
        VALUES (%s, %s, %s, %s)
        """
        params = (recipe_id, max_durability, max_quality, required_durability)
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            logging.error(f"Error inserting recipe stats: {e}")
            return False
    
    def insert_training_data(self, recipe_id: int, required_craftsmanship: int,
                            required_control: int, progress_per_100: float,
                            quality_per_100: float) -> bool:
        """レシピの学習データを登録する
        
        Args:
            recipe_id: レシピID（recipesテーブルの外部キー）
            required_craftsmanship: 必要作業精度
            required_control: 必要加工精度
            progress_per_100: 作業効率100あたりの工数進捗量
            quality_per_100: 加工効率100あたりの品質進捗量
            
        Returns:
            bool: 登録成功ならTrue
        """
        query = """
        INSERT INTO training_data (id, required_craftsmanship, required_control,
                                 progress_per_100_efficiency, quality_per_100_efficiency)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (recipe_id, required_craftsmanship, required_control,
                 progress_per_100, quality_per_100)
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            logging.error(f"Error inserting training data: {e}")
            return False 
    
    def search_recipes(self, 
                      job: str = None,
                      recipe_level: int = None,
                      master_book_level: int = None,
                      stars: int = None) -> List[Dict[str, Any]]:
        """レシピを検索する
        
        Args:
            job: クラフター職種（任意）
            recipe_level: レシピレベル（任意）
            master_book_level: 秘伝書レベル（任意）
            stars: ☆の数（任意）
            
        Returns:
            List[Dict[str, Any]]: 検索結果のリスト
        """
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []
        
        if job:
            query += " AND job = %s"
            params.append(job)
        if recipe_level:
            query += " AND recipe_level = %s"
            params.append(recipe_level)
        if master_book_level is not None:
            query += " AND master_book_level = %s"
            params.append(master_book_level)
        if stars is not None:
            query += " AND stars = %s"
            params.append(stars)
            
        try:
            result = self.execute_query(query, tuple(params))
            if result:
                # 結果を辞書のリストに変換
                columns = ['id', 'name', 'job', 'recipe_level', 
                          'master_book_level', 'stars', 'patch_version', 
                          'collected_at', 'created_at']
                return [dict(zip(columns, row)) for row in result]
            return []
            
        except Error as e:
            logging.error(f"Error searching recipes: {e}")
            return []
    
    def bulk_insert_recipes(self, recipes: List[Dict[str, Any]]) -> List[int]:
        """レシピを一括登録する
        
        Args:
            recipes: 登録するレシピのリスト。各レシピは以下のキーを含む辞書：
                    - name: レシピ名
                    - job: クラフター職種
                    - recipe_level: レシピレベル
                    - master_book_level: 秘伝書レベル（オプション）
                    - stars: ☆の数（オプション）
                    - patch_version: パッチバージョン
                    - max_durability: 最大工数
                    - max_quality: 最大品質
                    - required_durability: 必要工数
                    - required_craftsmanship: 必要作業精度
                    - required_control: 必要加工精度
                    - progress_per_100: 作業効率100あたりの工数進捗量
                    - quality_per_100: 加工効率100あたりの品質進捗量
        
        Returns:
            List[int]: 登録されたレシピのIDリスト
        """
        registered_ids = []
        
        try:
            for recipe in recipes:
                # 1. レシピ基本情報の登録
                recipe_id = self.insert_recipe(
                    name=recipe['name'],
                    job=recipe['job'],
                    recipe_level=recipe['recipe_level'],
                    master_book_level=recipe.get('master_book_level', 0),
                    stars=recipe.get('stars', 0),
                    patch_version=recipe.get('patch_version', '6.4')
                )
                
                if recipe_id:
                    # 2. レシピ作業情報の登録
                    stats_success = self.insert_recipe_stats(
                        recipe_id=recipe_id,
                        max_durability=recipe['max_durability'],
                        max_quality=recipe['max_quality'],
                        required_durability=recipe['required_durability']
                    )
                    
                    # 3. 学習データの登録
                    training_success = self.insert_training_data(
                        recipe_id=recipe_id,
                        required_craftsmanship=recipe['required_craftsmanship'],
                        required_control=recipe['required_control'],
                        progress_per_100=recipe['progress_per_100'],
                        quality_per_100=recipe['quality_per_100']
                    )
                    
                    if stats_success and training_success:
                        registered_ids.append(recipe_id)
                    else:
                        # 登録に失敗した場合は、そのレシピのデータを削除
                        self.execute_query("DELETE FROM training_data WHERE id = %s", (recipe_id,))
                        self.execute_query("DELETE FROM recipe_stats WHERE id = %s", (recipe_id,))
                        self.execute_query("DELETE FROM recipes WHERE id = %s", (recipe_id,))
            
            return registered_ids
            
        except Error as e:
            logging.error(f"Error in bulk insert: {e}")
            return registered_ids 