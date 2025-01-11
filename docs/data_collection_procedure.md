# データ収集手順書

## 1. 概要
FF14のレシピデータを収集し、データベースに登録する手順を説明します。

## 2. 収集対象
### 2.1 レシピの選定基準
- 秘伝書レシピ：実装済みの全レシピ
- 通常レシピ：レベル帯ごとに代表的なレシピ

### 2.2 必要な情報
1. レシピ基本情報
   - レシピ名
   - クラフター職種
   - レシピレベル
   - 秘伝書レベル
   - ★の数
   - パッチバージョン

2. レシピ作業情報
   - 最大工数
   - 最大品質
   - 必要工数

3. 学習データ
   - 必要作業精度
   - 必要加工精度
   - 作業効率100あたりの工数進捗量
   - 加工効率100あたりの品質進捗量

## 3. 収集手順
### 3.1 データの準備
1. ゲーム内で対象レシピを開く
2. 必要な情報をGoogle Spreadsheetに記録
   - テンプレート: [FF14レシピデータ収集テンプレート]
   - 1シートにつき1職種のデータを記録
   - シート名は職種名（例：BSM, CRP）とする

### 3.2 データの登録
1. Google SpreadsheetからCSVでエクスポート
   - ファイル → ダウンロード → カンマ区切りの値（.csv）
2. CSVからJSONフォーマットに変換
   ```python
   # 変換スクリプトを使用
   python src/utils/csv_to_json.py input.csv output.json
   ```

3. データベースへの登録
   - 一括登録機能を使用
   - 登録後にデータの整合性を確認

## 4. データの検証
### 4.1 検証項目
1. 必須項目の入力確認
2. データ型の確認
3. 値の範囲チェック
   - レベルは1-90の範囲内
   - 工数・品質は正の整数
   - 効率値は正の実数

### 4.2 検証手順
1. 登録データの検索
   ```python
   # 職種ごとのデータ確認
   results = connector.search_recipes(job='BSM')
   
   # レベル帯ごとのデータ確認
   results = connector.search_recipes(recipe_level=90)
   ```

2. データの可視化
   - レベルと必要精度の関係
   - 工数と品質の分布
   - 職種ごとのレシピ数

## 5. エラー対応
### 5.1 データ登録エラー
1. 外部キー制約エラー
   - レシピ基本情報が正しく登録されているか確認
   - 必要に応じてロールバック

2. データ型エラー
   - 数値項目に文字列が入っていないか確認
   - NULL値が許可されていない項目の確認

### 5.2 データ修正手順
1. エラーが発生したレコードの特定
2. バックアップの作成
3. データの修正と再登録
4. 修正後の検証

## 6. 注意事項
- データ収集は一度に大量に行わず、少量ずつ実施
- 定期的にバックアップを作成
- エラーログは必ず保存
- 不明点があれば都度記録 