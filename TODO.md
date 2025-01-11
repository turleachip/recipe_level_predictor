# プロジェクトTODO

## 環境構築状況
### インストール済み ✅
1. バックエンド
   - [x] Python
   - [x] MySQL
   - [x] FastAPI
   - [x] uvicorn
   - [x] MySQL Connector
   - [x] python-dotenv
   - [x] SQLAlchemy

2. フロントエンド
   - [x] Node.js
   - [x] npm

### 未インストール 📦
1. フロントエンド
   - [ ] Next.js
   - [ ] TypeScript
   - [ ] Tailwind CSS
   - [ ] Zustand（状態管理）
   - [ ] React Query（APIクライアント）
   - [ ] React Hook Form（フォーム管理）

### 実装状況 🔥
1. バックエンド
   - [x] FastAPI基本セットアップ
   - [x] テストエンドポイント動作確認
   - [x] MySQLConnector設定
   - [x] データベース接続テスト
   - [ ] APIエンドポイント実装
     - [ ] レシピ登録 (POST /recipes)
     - [ ] レシピ一覧取得 (GET /recipes)
     - [ ] レシピ詳細取得 (GET /recipes/{id})
     - [ ] レシピ更新 (PUT /recipes/{id})
     - [ ] レシピ削除 (DELETE /recipes/{id})
     - [ ] レシピ検索 (GET /recipes/search)
   - [ ] バリデーション
   - [ ] エラーハンドリング

2. フロントエンド
   - [ ] Next.jsプロジェクト作成
   - [ ] 基本コンポーネント設計
     - [ ] レシピ登録フォーム
     - [ ] レシピ一覧表示
     - [ ] レシピ詳細表示
     - [ ] 検索フォーム
     - [ ] 編集フォーム
   - [ ] APIクライアント実装
   - [ ] 状態管理設定
   - [ ] フォーム実装

3. 開発環境/デプロイ
   - [ ] ローカル開発環境
   - [ ] CI/CD
   - [ ] デプロイ戦略

## データベース環境構築 ✅
- [x] MySQLのセットアップ
  - [x] MySQLのインストール
  - [x] データベースの作成
  - [x] テーブルの作成
- [x] 基本的なCRUD操作の実装
  - [x] レシピ基本情報の登録
  - [x] レシピ作業情報の登録
  - [x] 学習データの登録 