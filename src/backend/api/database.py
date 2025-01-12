from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数から接続情報を取得
host = os.getenv("MYSQL_HOST", "localhost")
database = os.getenv("MYSQL_DATABASE", "ff14_recipe_level_predictor")
user = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", "")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RecipeDB(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    job = Column(String(3), nullable=False)
    recipe_level = Column(Integer, nullable=False)
    master_book_level = Column(Integer, default=0)
    stars = Column(Integer, default=0)
    patch_version = Column(String(10), nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)

    stats = relationship("RecipeStatsDB", back_populates="recipe", uselist=False)
    training_data = relationship("TrainingDataDB", back_populates="recipe", uselist=False)

class RecipeStatsDB(Base):
    __tablename__ = "recipe_stats"

    id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    max_durability = Column(Integer, nullable=False)
    max_quality = Column(Integer, nullable=False)
    required_durability = Column(Integer, nullable=False)

    recipe = relationship("RecipeDB", back_populates="stats")

class TrainingDataDB(Base):
    __tablename__ = "training_data"

    id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    required_craftsmanship = Column(Integer, nullable=False)
    required_control = Column(Integer, nullable=False)
    progress_per_100 = Column(Float, nullable=False)
    quality_per_100 = Column(Float, nullable=False)

    recipe = relationship("RecipeDB", back_populates="training_data") 