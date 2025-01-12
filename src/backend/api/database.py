from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from contextlib import contextmanager

# データベースURL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/ff14_recipe_predictor")

# エンジンの作成
engine = create_engine(DATABASE_URL)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()

class RecipeDB(Base):
    """レシピ基本情報テーブル"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    job = Column(String(3), index=True)
    recipe_level = Column(Integer, index=True)
    master_book_level = Column(Integer, nullable=True)
    stars = Column(Integer, nullable=True)
    patch_version = Column(String(10))
    collected_at = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    stats = relationship("RecipeStatsDB", back_populates="recipe", uselist=False)
    training_data = relationship("TrainingDataDB", back_populates="recipe", uselist=False)

class RecipeStatsDB(Base):
    """レシピ作業情報テーブル"""
    __tablename__ = "recipe_stats"

    id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    max_durability = Column(Integer)
    max_quality = Column(Integer)
    required_durability = Column(Integer)

    # リレーションシップ
    recipe = relationship("RecipeDB", back_populates="stats")

class TrainingDataDB(Base):
    """トレーニングデータテーブル"""
    __tablename__ = "training_data"

    id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    required_craftsmanship = Column(Integer)
    required_control = Column(Integer)
    progress_per_100 = Column(Float)
    quality_per_100 = Column(Float)

    # リレーションシップ
    recipe = relationship("RecipeDB", back_populates="training_data")

# データベース依存関係
_db = None

@contextmanager
def get_db():
    """データベースセッションを取得する"""
    global _db
    if _db is not None:
        yield _db
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def set_test_db(db):
    """テスト用データベースを設定する"""
    global _db
    _db = db 