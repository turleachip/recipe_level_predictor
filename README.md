# レシピレベル推論君

FF14のクラフターレシピの難易度を機械学習で推論するツール

## 概要

このプロジェクトは、FF14（Final Fantasy XIV）のクラフターレシピの難易度を機械学習を用いて推論することを目的としています。
新しいレシピが実装された際に、その難易度を事前に予測し、適切なマクロ作成を支援します。

### 主な機能
- レシピの難易度推論
  - 工数難易度の推定
  - 品質難易度の推定
- 難易度分析
  - 秘伝書レベル間の比較
  - ☆レベルによる難易度変化の分析
- 精度検証・可視化
  - 予測精度の追跡
  - 分析結果の可視化

## 環境要件

- Python 3.8以上
- Windows 11 Home
- 必要なPythonパッケージ（requirements.txtを参照）

## インストール方法

1. リポジトリのクローン
```bash
git clone https://github.com/turleachip/recipe_level_predictor.git
cd recipe_level_predictor
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

## 使用方法

※ 開発中のため、詳細は後日追加予定

## 開発者向け情報

### プロジェクト構成
```
recipe_level_predictor/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── notebooks/          # 実験用Jupyter notebooks
├── src/               # ソースコード
│   ├── __init__.py
│   ├── data/         # データ処理関連
│   ├── models/       # モデル関連
│   └── utils/        # ユーティリティ
├── tests/            # テストコード
├── data/             # データ格納
│   ├── raw/         
│   └── processed/    
└── docs/             # ドキュメント
```

### 開発フロー
1. 機能追加やバグ修正は新しいブランチを作成
2. コードスタイルはblackとflake8に従う
3. 変更前にテストを実行
4. プルリクエストを作成

## ライセンス

MIT License

Copyright (c) 2024 turleachip

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 