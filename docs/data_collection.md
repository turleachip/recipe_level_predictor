# データ収集設計書
> Revision: 2
> Changes: CSVファイル形式からMySQLデータベースへ変更

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

## 2. データベース設計
### テーブル構造
```sql
-- レシピ基本情報
CREATE TABLE recipes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    job ENUM('CRP','BSM','ARM','GSM','LTW','WVR','ALC','CUL') NOT NULL,
    recipe_level INT NOT NULL,
    master_book_level INT DEFAULT 0,
    stars INT DEFAULT 0,
    patch_version VARCHAR(10) NOT NULL,
    collected_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- レシピ作業情報
CREATE TABLE recipe_stats (
    id INT PRIMARY KEY,
    max_durability INT NOT NULL,
    max_quality INT NOT NULL,
    required_durability INT NOT NULL,
    FOREIGN KEY (id) REFERENCES recipes(id)
);

-- 学習データ
CREATE TABLE training_data (
    id INT PRIMARY KEY,
    required_craftsmanship INT NOT NULL,
    required_control INT NOT NULL,
    progress_per_100_efficiency FLOAT NOT NULL,
    quality_per_100_efficiency FLOAT NOT NULL,
    FOREIGN KEY (id) REFERENCES recipes(id)
);

-- モデルバージョン
CREATE TABLE model_versions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ハイパーパラメータ履歴
CREATE TABLE hyperparameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_version_id INT NOT NULL,
    param_name VARCHAR(50) NOT NULL,
    param_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_version_id) REFERENCES model_versions(id)
);

-- 推論結果履歴
CREATE TABLE inference_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    recipe_id INT NOT NULL,
    model_version_id INT NOT NULL,
    predicted_craftsmanship INT NOT NULL,
    predicted_control INT NOT NULL,
    predicted_progress FLOAT NOT NULL,
    predicted_quality FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (model_version_id) REFERENCES model_versions(id)
);
```

## 3. データ管理方針
1. レシピデータの管理
   - 新規レシピの追加時は`recipes`テーブルから開始
   - 関連情報を各テーブルに順次追加

2. モデルバージョン管理
   - メジャーアップデート：1.0.0 → 2.0.0
   - マイナーアップデート：1.0.0 → 1.1.0
   - パッチ：1.0.0 → 1.0.1

3. ハイパーパラメータ管理
   - モデルバージョンと紐付けて保存
   - 調整履歴を追跡可能

4. 推論結果の履歴管理
   - モデルバージョンごとの推論結果を保存
   - 精度の変化を追跡可能 