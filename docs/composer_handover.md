# Cursor COMPOSER 引継ぎ資料

## 1. プロジェクト概要
FF14のクラフトレシピの難易度を予測するWebアプリケーション。

### 1.1 特別な支援要件
1. コミットのタイミング提案
   - 機能実装の完了時
   - テストの追加時
   - 環境構築の区切り時
   - 設定ファイルの更新時

2. 技術スタックの更新提案
   - 現在の実装との互換性確認
   - コミュニティのトレンド分析
   - 代替技術の比較検討
   - アップデートによるメリット・デメリット

3. コードレビューの観点
   - Pythonコードスタイル（black, flake8準拠）
   - TypeScriptのベストプラクティス
   - セキュリティの考慮

## 2. プロジェクト構造
```
recipe_level_predictor/
├── src/
│   ├── backend/
│   │   └── api/
│   │       └── main.py (FastAPI実装)
│   ├── database/
│   │   └── mysql_connector.py
│   └── frontend/
│       └── src/
│           └── app/ (Next.js実装)
├── tests/
│   └── test_mysql_connector.py
└── docs/
    ├── data_collection.md
    └── data_collection_procedure.md
```

## 3. 技術スタック
### 3.1 バックエンド
- Python 3.8+
- FastAPI
- MySQL 8.0
- SQLAlchemy
- python-dotenv
- mysql-connector-python

### 3.2 フロントエンド
- Next.js 14
- TypeScript
- Tailwind CSS
- Zustand（状態管理）
- React Query
- React Hook Form + Zod

## 4. データベース設計
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
    collected_at DATETIME NOT NULL
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
    progress_per_100 FLOAT NOT NULL,
    quality_per_100 FLOAT NOT NULL,
    FOREIGN KEY (id) REFERENCES recipes(id)
);
```

## 5. 実装状況
### 5.1 完了済み
- ✅ プロジェクト基本構造の設定
- ✅ バックエンド環境構築
- ✅ フロントエンド環境構築
- ✅ データベース接続設定
- ✅ 基本的なテスト実装

### 5.2 実装予定
1. バックエンド
   - APIエンドポイント（CRUD操作）
   - バリデーション
   - エラーハンドリング

2. フロントエンド
   - コンポーネント設計
   - APIクライアント実装
   - 状態管理設定
   - フォーム実装

## 6. 非機能要件
### 6.1 性能要件
- レスポンス時間：1秒以内
- メモリ使用量：2GB以内
- CPU使用率：30%以下（通常時）

### 6.2 開発環境
- OS：Windows 11 Home (23H2)
- エディタ：Cursor
- バージョン管理：Git

## 7. 開発フロー
1. 機能追加やバグ修正は新しいブランチを作成
2. コードスタイルはblackとflake8に従う
3. 変更前にテストを実行
4. プルリクエストを作成

## 8. 注意事項
1. 環境変数は`.env`で管理
2. APIキーなどの機密情報は`.gitignore`で除外
3. コミットメッセージは[Conventional Commits](https://www.conventionalcommits.org/)に従う
4. 定期的なバックアップを推奨 