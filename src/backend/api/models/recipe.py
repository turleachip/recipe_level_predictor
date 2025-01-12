from pydantic import BaseModel, Field, validator
from pydantic.types import constr
from typing import Optional, Union, Annotated
from datetime import datetime
import re

class RecipeBase(BaseModel):
    """レシピの基本情報"""
    name: str = Field(..., description="レシピ名")
    job: Annotated[str, constr(regex=r'^(CRP|BSM|ARM|GSM|LTW|WVR|ALC|CUL)$')] = Field(..., description="クラフタージョブ")
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
    job: Optional[Annotated[str, constr(regex=r'^(CRP|BSM|ARM|GSM|LTW|WVR|ALC|CUL)$')]] = None
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
    min_level: Optional[int] = Field(None, description="最小レベル")
    max_level: Optional[int] = Field(None, description="最大レベル")
    master_book_level: Optional[int] = Field(None, description="秘伝書レベル")
    stars: Optional[int] = Field(None, description="星の数")
    patch_version: Optional[str] = Field(None, description="パッチバージョン")
    min_craftsmanship: Optional[int] = Field(None, description="最小作業精度")
    max_craftsmanship: Optional[int] = Field(None, description="最大作業精度")
    min_control: Optional[int] = Field(None, description="最小加工精度")
    max_control: Optional[int] = Field(None, description="最大加工精度")
    skip: int = Field(0, ge=0, description="スキップ数")
    limit: int = Field(10, ge=1, le=100, description="取得件数")

    @validator('min_level', 'max_level', 'master_book_level', 'stars',
              'min_craftsmanship', 'max_craftsmanship', 'min_control', 'max_control',
              'skip', 'limit', pre=True)
    def convert_string_to_int(cls, v):
        if isinstance(v, str) and v.strip():
            try:
                return int(v)
            except ValueError:
                raise ValueError('数値に変換できない文字列です')
        return v

    @validator("min_level", "max_level", "master_book_level", "stars", 
              "min_craftsmanship", "max_craftsmanship", "min_control", "max_control",
              "skip", "limit", pre=True)
    def validate_integer_fields(cls, v, field):
        if v is None and field.name not in ["skip", "limit"]:
            return v
        try:
            if isinstance(v, str):
                if v.strip() == "":
                    return None
                value = int(v)
            else:
                value = v
            
            if not isinstance(value, int):
                raise ValueError
                
            # バリデーションチェック
            if field.name in ["min_level", "max_level", "master_book_level", 
                            "min_craftsmanship", "max_craftsmanship", 
                            "min_control", "max_control"] and value < 1:
                raise ValueError(f"{field.name} must be greater than or equal to 1")
            
            if field.name == "stars" and (value < 1 or value > 5):
                raise ValueError("stars must be between 1 and 5")
                
            if field.name == "skip" and value < 0:
                raise ValueError("skip must be greater than or equal to 0")
                
            if field.name == "limit" and (value < 1 or value > 100):
                raise ValueError("limit must be between 1 and 100")
                
            return value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid integer value for {field.name}")

    @validator("job")
    def validate_job(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        valid_jobs = {'CRP', 'BSM', 'ARM', 'GSM', 'LTW', 'WVR', 'ALC', 'CUL'}
        if v not in valid_jobs:
            raise ValueError('Invalid job code')
        return v

    @validator("patch_version")
    def validate_patch_version(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        if not isinstance(v, str):
            raise ValueError("Patch version must be a string")
        if not re.match(r'^\d+\.\d+$', v):
            raise ValueError("Invalid patch version format")
        return v

    @validator("max_level")
    def validate_max_level(cls, v, values):
        if v is not None and values.get("min_level") is not None:
            if v < values["min_level"]:
                raise ValueError("max_level must be greater than or equal to min_level")
        return v

    @validator("max_craftsmanship")
    def validate_max_craftsmanship(cls, v, values):
        if v is not None and values.get("min_craftsmanship") is not None:
            if v < values["min_craftsmanship"]:
                raise ValueError("max_craftsmanship must be greater than or equal to min_craftsmanship")
        return v

    @validator("max_control")
    def validate_max_control(cls, v, values):
        if v is not None and values.get("min_control") is not None:
            if v < values["min_control"]:
                raise ValueError("max_control must be greater than or equal to min_control")
        return v

    class Config:
        validate_assignment = True 