from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import math

from .models import RecipeCreate, RecipeResponse, RecipeFilter, PaginatedRecipeResponse
from .database import get_db, RecipeDB, RecipeStatsDB, TrainingDataDB

app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse({"message": "Welcome to Recipe Level Predictor API"})

@app.get("/test")
async def test():
    return JSONResponse({"message": "FastAPI is working!"})

@app.post("/recipes", response_model=RecipeResponse)
async def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    try:
        # レシピ基本情報の作成
        db_recipe = RecipeDB(
            name=recipe.name,
            job=recipe.job,
            recipe_level=recipe.recipe_level,
            master_book_level=recipe.master_book_level,
            stars=recipe.stars,
            patch_version=recipe.patch_version,
            collected_at=datetime.utcnow()
        )
        db.add(db_recipe)
        db.flush()  # IDを生成するためにflush

        # レシピ作業情報の作成
        db_stats = RecipeStatsDB(
            id=db_recipe.id,
            max_durability=recipe.max_durability,
            max_quality=recipe.max_quality,
            required_durability=recipe.required_durability
        )
        db.add(db_stats)

        # トレーニングデータの作成
        db_training = TrainingDataDB(
            id=db_recipe.id,
            required_craftsmanship=recipe.required_craftsmanship,
            required_control=recipe.required_control,
            progress_per_100=recipe.progress_per_100,
            quality_per_100=recipe.quality_per_100
        )
        db.add(db_training)

        db.commit()
        db.refresh(db_recipe)
        db.refresh(db_stats)
        db.refresh(db_training)

        # レスポンスの作成
        response = {
            "id": db_recipe.id,
            "name": db_recipe.name,
            "job": db_recipe.job,
            "recipe_level": db_recipe.recipe_level,
            "master_book_level": db_recipe.master_book_level,
            "stars": db_recipe.stars,
            "patch_version": db_recipe.patch_version,
            "collected_at": db_recipe.collected_at,
            "max_durability": db_stats.max_durability,
            "max_quality": db_stats.max_quality,
            "required_durability": db_stats.required_durability,
            "required_craftsmanship": db_training.required_craftsmanship,
            "required_control": db_training.required_control,
            "progress_per_100": db_training.progress_per_100,
            "quality_per_100": db_training.quality_per_100
        }
        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recipes", response_model=PaginatedRecipeResponse)
async def get_recipes(
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0, le=100),
    filter: RecipeFilter = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # フィルター条件の構築
        conditions = []
        if filter.job:
            conditions.append(RecipeDB.job == filter.job)
        if filter.min_level:
            conditions.append(RecipeDB.recipe_level >= filter.min_level)
        if filter.max_level:
            conditions.append(RecipeDB.recipe_level <= filter.max_level)
        if filter.master_book_level is not None:
            conditions.append(RecipeDB.master_book_level == filter.master_book_level)
        if filter.stars is not None:
            conditions.append(RecipeDB.stars == filter.stars)

        # 総件数の取得
        query = db.query(RecipeDB)
        if conditions:
            query = query.filter(and_(*conditions))
        total = query.count()

        # ページネーション
        recipes = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # レスポンスの作成
        items = []
        for recipe in recipes:
            stats = recipe.stats
            training = recipe.training_data
            if stats and training:
                item = {
                    **recipe.__dict__,
                    **stats.__dict__,
                    **training.__dict__
                }
                items.append(item)

        return {
            "total": total,
            "items": items,
            "page": page,
            "per_page": per_page,
            "total_pages": math.ceil(total / per_page)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
