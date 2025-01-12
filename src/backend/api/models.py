from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RecipeBase(BaseModel):
    """レシピの基本情報"""
    name: str = Field(..., description="レシピ名")
    job: str = Field(..., description="クラフタージョブ")
    recipe_level: int = Field(..., description="レシピレベル")
    master_book_level: Optional[int] = Field(None, description="秘伝書レベル")
    stars: Optional[int] = Field(None, description="星の数")
    patch_version: str = Field(..., description="パッチバージョン")
    max_durability: int = Field(..., description="最大耐久")
    max_quality: int = Field(..., description="最大品質")
    required_durability: int = Field(..., description="必要耐久")
    required_craftsmanship: int = Field(..., description="必要作業精度")
    required_control: int = Field(..., description="必要加工精度")
    progress_per_100: float = Field(..., description="作業100あたりの進捗")
    quality_per_100: float = Field(..., description="加工100あたりの品質")

class RecipeCreate(RecipeBase):
    """レシピ作成リクエスト"""
    pass

class RecipeUpdate(BaseModel):
    """レシピ更新リクエスト"""
    name: Optional[str] = None
    job: Optional[str] = None
    recipe_level: Optional[int] = None
    master_book_level: Optional[int] = None
    stars: Optional[int] = None
    patch_version: Optional[str] = None
    max_durability: Optional[int] = None
    max_quality: Optional[int] = None
    required_durability: Optional[int] = None
    required_craftsmanship: Optional[int] = None
    required_control: Optional[int] = None
    progress_per_100: Optional[float] = None
    quality_per_100: Optional[float] = None

class Recipe(RecipeBase):
    """レシピレスポンス"""
    id: int
    collected_at: datetime

    class Config:
        orm_mode = True

class RecipeSearchParams(BaseModel):
    """レシピ検索パラメータ"""
    name: Optional[str] = None
    job: Optional[str] = None
    min_level: Optional[int] = None
    max_level: Optional[int] = None
    master_book_level: Optional[int] = None
    stars: Optional[int] = None
    patch_version: Optional[str] = None
    min_craftsmanship: Optional[int] = None
    max_craftsmanship: Optional[int] = None
    min_control: Optional[int] = None
    max_control: Optional[int] = None 