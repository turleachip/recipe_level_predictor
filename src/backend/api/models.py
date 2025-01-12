from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional, List

class CrafterJob(str, Enum):
    CRP = "CRP"
    BSM = "BSM"
    ARM = "ARM"
    GSM = "GSM"
    LTW = "LTW"
    WVR = "WVR"
    ALC = "ALC"
    CUL = "CUL"

class RecipeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    job: CrafterJob
    recipe_level: int = Field(..., gt=0)
    master_book_level: int = Field(default=0, ge=0)
    stars: int = Field(default=0, ge=0, le=5)
    patch_version: str = Field(..., regex=r"^\d+\.\d+$")

class RecipeCreate(RecipeBase):
    max_durability: int = Field(..., gt=0)
    max_quality: int = Field(..., gt=0)
    required_durability: int = Field(..., gt=0)
    required_craftsmanship: int = Field(..., gt=0)
    required_control: int = Field(..., gt=0)
    progress_per_100: float = Field(..., gt=0)
    quality_per_100: float = Field(..., gt=0)

class Recipe(RecipeBase):
    id: int
    collected_at: datetime

    class Config:
        from_attributes = True

class RecipeResponse(Recipe, RecipeCreate):
    class Config:
        from_attributes = True
        populate_by_name = True

class RecipeFilter(BaseModel):
    job: Optional[CrafterJob] = None
    min_level: Optional[int] = None
    max_level: Optional[int] = None
    master_book_level: Optional[int] = None
    stars: Optional[int] = None

class PaginatedRecipeResponse(BaseModel):
    total: int
    items: List[RecipeResponse]
    page: int
    per_page: int
    total_pages: int 