from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import math

from .models import RecipeCreate, RecipeResponse, RecipeFilter, PaginatedRecipeResponse, RecipeUpdate
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

@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    try:
        # レシピの取得
        recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # レスポンスの作成
        stats = recipe.stats
        training = recipe.training_data
        if not stats or not training:
            raise HTTPException(status_code=404, detail="Recipe data is incomplete")

        response = {
            "id": recipe.id,
            "name": recipe.name,
            "job": recipe.job,
            "recipe_level": recipe.recipe_level,
            "master_book_level": recipe.master_book_level,
            "stars": recipe.stars,
            "patch_version": recipe.patch_version,
            "collected_at": recipe.collected_at,
            "max_durability": stats.max_durability,
            "max_quality": stats.max_quality,
            "required_durability": stats.required_durability,
            "required_craftsmanship": training.required_craftsmanship,
            "required_control": training.required_control,
            "progress_per_100": training.progress_per_100,
            "quality_per_100": training.quality_per_100
        }
        return response

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(recipe_id: int, recipe_update: RecipeUpdate, db: Session = Depends(get_db)):
    try:
        # レシピの取得
        recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # 関連データの取得
        stats = recipe.stats
        training = recipe.training_data
        if not stats or not training:
            raise HTTPException(status_code=404, detail="Recipe data is incomplete")

        # レシピ基本情報の更新
        for field, value in recipe_update.dict(exclude_unset=True).items():
            if field in RecipeDB.__table__.columns:
                setattr(recipe, field, value)

        # レシピ作業情報の更新
        stats_fields = ["max_durability", "max_quality", "required_durability"]
        for field in stats_fields:
            if getattr(recipe_update, field) is not None:
                setattr(stats, field, getattr(recipe_update, field))

        # トレーニングデータの更新
        training_fields = ["required_craftsmanship", "required_control", "progress_per_100", "quality_per_100"]
        for field in training_fields:
            if getattr(recipe_update, field) is not None:
                setattr(training, field, getattr(recipe_update, field))

        db.commit()
        db.refresh(recipe)
        db.refresh(stats)
        db.refresh(training)

        # レスポンスの作成
        response = {
            "id": recipe.id,
            "name": recipe.name,
            "job": recipe.job,
            "recipe_level": recipe.recipe_level,
            "master_book_level": recipe.master_book_level,
            "stars": recipe.stars,
            "patch_version": recipe.patch_version,
            "collected_at": recipe.collected_at,
            "max_durability": stats.max_durability,
            "max_quality": stats.max_quality,
            "required_durability": stats.required_durability,
            "required_craftsmanship": training.required_craftsmanship,
            "required_control": training.required_control,
            "progress_per_100": training.progress_per_100,
            "quality_per_100": training.quality_per_100
        }
        return response

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
