# データ収集設計書

## 1. 収集項目
### 基本情報
- ID（プロジェクト内連番：1, 2, 3...）
- レシピ名
- クラフター職種
- レシピレベル
- 秘伝書レベル（該当する場合）
- ☆の数（該当する場合）

### クラフト情報
- 最大工数
- 最大品質
- 必要工数

### キャラクター情報
- クラフターレベル
- 作業精度
- 加工精度

### メタ情報
- パッチバージョン
- データ収集日時

### 学習ターゲット
1. 必要ステータス推論
   - 必要作業精度
   - 必要加工精度
2. 効率推論
   - 作業効率100あたりの工数進捗量
   - 加工効率100あたりの品質進捗量

## 2. データ形式案
### レシピ基本情報（recipes.csv）
```csv
id,name,job,recipe_level,master_book_level,stars,patch_version,collected_at
1,ハイスチール・インゴット,BSM,90,0,0,6.4,2024-01-09
```

### レシピ作業情報（recipe_stats.csv）
```csv
id,max_durability,max_quality,required_durability
1,70,12000,70
```

### キャラクター情報（character_stats.csv）
```csv
crafter_level,craftsmanship,control
90,3500,3300
```

### 学習データ（training_data.csv）
```csv
id,required_craftsmanship,required_control,progress_per_100_efficiency,quality_per_100_efficiency
1,3200,3000,250,250
``` 