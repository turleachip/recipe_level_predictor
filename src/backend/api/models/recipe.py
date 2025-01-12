from pydantic import BaseModel, Field, validator, constr
from typing import Optional, Union
from datetime import datetime

class RecipeBase(BaseModel):
    """レシピの基本情報"""
    name: str = Field(..., description="レシピ名")
    job: constr(regex=r'^(CRP|BSM|ARM|GSM|LTW|WVR|ALC|CUL)$') = Field(..., description="クラフタージョブ")
    recipe_level: int = Field(..., ge=1, description="レシピレベル")
    master_book_level: Optional[int] = Field(None, ge=1, description="秘伝書レベル")
    stars: Optional[int] = Field(None, ge=1, le=5, description="星の数")
    patch_version: str = Field(..., regex=r'^\d+\.\d+$', description="パッチバージョン")
    max_durability: int = Field(..., gt=0, description="最大耐久")
    max_quality: int = Field(..., gt=0, description="最大品質")
    required_durability: int = Field(..., gt=0, description="必要耐久")
    required_craftsmanship: int = Field(..., gt=0, description="必要作業精度")
    required_control: int = Field(..., gt=0, description="必要加工精度")
    progress_per_100: float = Field(..., gt=0, description="作業100あたりの進捗")
    quality_per_100: float = Field(..., gt=0, description="加工100あたりの品質")

    @validator('job')
    def validate_job(cls, v):
        valid_jobs = {'CRP', 'BSM', 'ARM', 'GSM', 'LTW', 'WVR', 'ALC', 'CUL'}
        if v not in valid_jobs:
            raise ValueError('Invalid job code')
        return v

class RecipeCreate(RecipeBase):
    """レシピ作成リクエスト"""
    pass

class RecipeUpdate(BaseModel):
    """レシピ更新リクエスト"""
    name: Optional[str] = None
    job: Optional[constr(regex=r'^(CRP|BSM|ARM|GSM|LTW|WVR|ALC|CUL)$')] = None
    recipe_level: Optional[int] = Field(None, ge=1)
    master_book_level: Optional[int] = Field(None, ge=1)
    stars: Optional[int] = Field(None, ge=1, le=5)
    patch_version: Optional[str] = Field(None, regex=r'^\d+\.\d+$')
    max_durability: Optional[int] = Field(None, gt=0)
    max_quality: Optional[int] = Field(None, gt=0)
    required_durability: Optional[int] = Field(None, gt=0)
    required_craftsmanship: Optional[int] = Field(None, gt=0)
    required_control: Optional[int] = Field(None, gt=0)
    progress_per_100: Optional[float] = Field(None, gt=0)
    quality_per_100: Optional[float] = Field(None, gt=0)

class Recipe(RecipeBase):
    """レシピレスポンス"""
    id: int
    collected_at: datetime

    class Config:
        orm_mode = True

class RecipeSearchParams(BaseModel):
    """レシピ検索パラメータ"""
    name: Optional[str] = Field(None, description="レシピ名")
    job: Optional[str] = Field(None, description="クラフタージョブ")
    min_level: Optional[Union[int, str]] = Field(None, description="最小レベル")
    max_level: Optional[Union[int, str]] = Field(None, description="最大レベル")
    master_book_level: Optional[Union[int, str]] = Field(None, description="秘伝書レベル")
    stars: Optional[Union[int, str]] = Field(None, description="星の数")
    patch_version: Optional[str] = Field(None, description="パッチバージョン")
    min_craftsmanship: Optional[Union[int, str]] = Field(None, description="最小作業精度")
    max_craftsmanship: Optional[Union[int, str]] = Field(None, description="最大作業精度")
    min_control: Optional[Union[int, str]] = Field(None, description="最小加工精度")
    max_control: Optional[Union[int, str]] = Field(None, description="最大加工精度")
    skip: int = Field(0, description="スキップ数")
    limit: int = Field(10, description="取得件数")

    @validator("min_level", "max_level", "master_book_level", "stars", 
              "min_craftsmanship", "max_craftsmanship", "min_control", "max_control",
              pre=True)
    def validate_integer_fields(cls, v):
        if v is None:
            return v
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("Invalid integer value")
        raise ValueError("Invalid value type")

    class Config:
        validate_assignment = True 