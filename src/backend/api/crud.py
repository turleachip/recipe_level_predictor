from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Tuple
from . import models
from .database import RecipeDB, RecipeStatsDB, TrainingDataDB
from fastapi import HTTPException

async def create_recipe(db: Session, recipe: models.RecipeCreate) -> Union[Dict[str, Any], Tuple[str, int]]:
    """レシピを新規登録する"""
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

        return {
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
    except IntegrityError as e:
        db.rollback()
        if "Duplicate entry" in str(e):
            return "Recipe with this name and job already exists", 409
        return str(e), 400

async def get_recipes(db: Session, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
    """レシピ一覧を取得する"""
    total = db.query(RecipeDB).count()
    recipes = db.query(RecipeDB).offset(skip).limit(limit).all()
    
    items = []
    for recipe in recipes:
        stats = recipe.stats
        training = recipe.training_data
        if stats and training:
            item = {
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
            items.append(item)
    
    return {
        "total": total,
        "items": items
    }

async def get_recipe(db: Session, recipe_id: int) -> Optional[Dict[str, Any]]:
    """指定されたIDのレシピを取得する"""
    recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if recipe is None:
        return None

    stats = recipe.stats
    training = recipe.training_data
    if not stats or not training:
        return None

    return {
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

async def update_recipe(db: Session, recipe_id: int, recipe_update: models.RecipeUpdate) -> Optional[Dict[str, Any]]:
    """レシピを更新する"""
    recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if recipe is None:
        return None

    # レシピ基本情報の更新
    for key, value in recipe_update.dict(exclude_unset=True).items():
        if hasattr(recipe, key):
            setattr(recipe, key, value)

    # レシピ作業情報の更新
    if recipe.stats:
        for key, value in recipe_update.dict(exclude_unset=True).items():
            if hasattr(recipe.stats, key):
                setattr(recipe.stats, key, value)

    # トレーニングデータの更新
    if recipe.training_data:
        for key, value in recipe_update.dict(exclude_unset=True).items():
            if hasattr(recipe.training_data, key):
                setattr(recipe.training_data, key, value)

    db.commit()
    db.refresh(recipe)
    db.refresh(recipe.stats)
    db.refresh(recipe.training_data)

    return await get_recipe(db, recipe_id)

async def delete_recipe(db: Session, recipe_id: int) -> bool:
    """レシピを削除する"""
    recipe = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
    if recipe is None:
        return False

    # 関連するレコードを削除
    db.query(TrainingDataDB).filter(TrainingDataDB.id == recipe_id).delete()
    db.query(RecipeStatsDB).filter(RecipeStatsDB.id == recipe_id).delete()
    db.query(RecipeDB).filter(RecipeDB.id == recipe_id).delete()
    
    db.commit()
    return True

async def search_recipes(db: Session, params: models.RecipeSearchParams) -> Dict[str, Any]:
    """レシピを検索する"""
    query = db.query(RecipeDB)

    # 検索条件の適用
    if params.name:
        query = query.filter(RecipeDB.name.like(f"%{params.name}%"))
    if params.job:
        query = query.filter(RecipeDB.job == params.job)
    if params.min_level is not None:
        query = query.filter(RecipeDB.recipe_level >= params.min_level)
    if params.max_level is not None:
        query = query.filter(RecipeDB.recipe_level <= params.max_level)
    if params.master_book_level is not None:
        query = query.filter(RecipeDB.master_book_level == params.master_book_level)
    if params.stars is not None:
        query = query.filter(RecipeDB.stars == params.stars)
    if params.patch_version:
        query = query.filter(RecipeDB.patch_version == params.patch_version)

    # トレーニングデータの条件
    if any([params.min_craftsmanship, params.max_craftsmanship, 
            params.min_control, params.max_control]):
        query = query.join(TrainingDataDB)
        if params.min_craftsmanship is not None:
            query = query.filter(TrainingDataDB.required_craftsmanship >= params.min_craftsmanship)
        if params.max_craftsmanship is not None:
            query = query.filter(TrainingDataDB.required_craftsmanship <= params.max_craftsmanship)
        if params.min_control is not None:
            query = query.filter(TrainingDataDB.required_control >= params.min_control)
        if params.max_control is not None:
            query = query.filter(TrainingDataDB.required_control <= params.max_control)

    total = query.count()
    recipes = query.offset(params.skip).limit(params.limit).all()

    items = []
    for recipe in recipes:
        stats = recipe.stats
        training = recipe.training_data
        if stats and training:
            item = {
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
            items.append(item)

    return {
        "total": total,
        "items": items
    } 