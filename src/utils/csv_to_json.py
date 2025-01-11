import csv
import json
import argparse
from typing import List, Dict, Any
import logging

def convert_csv_to_json(csv_file: str) -> List[Dict[str, Any]]:
    """CSVファイルをJSONフォーマットに変換
    
    Args:
        csv_file: 入力CSVファイルのパス
        
    Returns:
        List[Dict[str, Any]]: レシピデータのリスト
    """
    recipes = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # 数値型への変換
                recipe = {
                    'name': row['name'],
                    'job': row['job'],
                    'recipe_level': int(row['recipe_level']),
                    'master_book_level': int(row['master_book_level']),
                    'stars': int(row['stars']),
                    'patch_version': row['patch_version'],
                    'max_durability': int(row['max_durability']),
                    'max_quality': int(row['max_quality']),
                    'required_durability': int(row['required_durability']),
                    'required_craftsmanship': int(row['required_craftsmanship']),
                    'required_control': int(row['required_control']),
                    'progress_per_100': float(row['progress_per_100']),
                    'quality_per_100': float(row['quality_per_100'])
                }
                recipes.append(recipe)
                
        return recipes
        
    except Exception as e:
        logging.error(f"Error converting CSV to JSON: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Convert CSV to JSON for FF14 recipe data')
    parser.add_argument('input', help='Input CSV file path')
    parser.add_argument('output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    # CSVからデータを読み込み
    recipes = convert_csv_to_json(args.input)
    
    if recipes:
        # JSONファイルに書き出し
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"✅ 変換完了: {len(recipes)}件のレシピを{args.output}に保存しました")
    else:
        print("❌ 変換に失敗しました")

if __name__ == "__main__":
    main() 