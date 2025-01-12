from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, Union
from datetime import datetime
from .database import get_db
from .crud import (
    create_recipe,
    get_recipes,
    get_recipe,
    update_recipe,
    delete_recipe,
    search_recipes
)
from .models import (
    RecipeCreate,
    RecipeUpdate,
    RecipeSearchParams,
    Recipe
)
from .models.responses import StandardResponse, ErrorResponse
from .logging_config import logger
from .middleware import setup_error_handlers, logging_middleware
from pydantic import ValidationError
from fastapi.encoders import jsonable_encoder

app = FastAPI(
    title="FF14 レシピレベル推論API",
    description="FF14のレシピ情報を管理し、レシピレベルを推論するAPI",
    version="1.0.0"
)

# ミドルウェアの設定
app.middleware("http")(logging_middleware)
setup_error_handlers(app)

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("Application shutdown")

@app.post("/recipes/")
async def create_recipe_endpoint(request: Request, db: Session = Depends(get_db)):
    """レシピを新規登録する"""
    try:
        # リクエストボディのパース
        body = await request.json()
        recipe = RecipeCreate(**body)
        
        logger.info(f"Creating new recipe: {recipe.name}")
        with db as session:
            result = await create_recipe(db=session, recipe=recipe)
            if isinstance(result, tuple):
                error_message, status_code = result
                error = ErrorResponse(
                    code=status_code,
                    message=error_message,
                    type="database_error" if status_code == 409 else "validation_error",
                    details={"error_code": status_code}
                )
                return StandardResponse.error_response(error=error)
            return StandardResponse.success_response(data=jsonable_encoder(result))
    except ValidationError as e:
        logger.error(
            "Validation error: Invalid recipe data",
            extra={
                "error": str(e),
                "error_type": "validation_error",
                "details": e.errors()
            }
        )
        error = ErrorResponse(
            code=400,
            message="Invalid recipe data",
            type="validation_error",
            details=e.errors()
        )
        return StandardResponse.error_response(error=error)
    except Exception as e:
        logger.error(
            f"Error creating recipe: {str(e)}",
            extra={
                "error": str(e),
                "error_type": "internal_error"
            }
        )
        error = ErrorResponse(
            code=500,
            message="Internal server error",
            type="internal_error"
        )
        return StandardResponse.error_response(error=error)

@app.get("/recipes/")
async def read_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """レシピ一覧を取得する"""
    logger.info(f"Fetching recipes with skip={skip}, limit={limit}")
    with db as session:
        result = await get_recipes(db=session, skip=skip, limit=limit)
        return StandardResponse.success_response(
            data=jsonable_encoder(result["items"]),
            meta={"total": result["total"]}
        )

@app.get("/recipes/search")
async def search_recipes_endpoint(
    name: Optional[str] = None,
    job: Optional[str] = None,
    min_level: Optional[str] = None,
    max_level: Optional[str] = None,
    master_book_level: Optional[str] = None,
    stars: Optional[str] = None,
    patch_version: Optional[str] = None,
    min_craftsmanship: Optional[str] = None,
    max_craftsmanship: Optional[str] = None,
    min_control: Optional[str] = None,
    max_control: Optional[str] = None,
    skip: str = "0",
    limit: str = "10",
    db: Session = Depends(get_db)
):
    """レシピを検索する"""
    try:
        params = RecipeSearchParams(
            name=name,
            job=job,
            min_level=min_level,
            max_level=max_level,
            master_book_level=master_book_level,
            stars=stars,
            patch_version=patch_version,
            min_craftsmanship=min_craftsmanship,
            max_craftsmanship=max_craftsmanship,
            min_control=min_control,
            max_control=max_control,
            skip=skip,
            limit=limit
        )
        logger.info(f"Searching recipes with params: {params}")
        with db as session:
            result = await search_recipes(db=session, params=params)
        return StandardResponse.success_response(
            data=jsonable_encoder(result["items"]),
            meta={"total": result["total"]}
        )
    except ValidationError as e:
        logger.error(
            "Validation error: Invalid search parameters",
            extra={
                "error": str(e),
                "error_type": "validation_error",
                "details": e.errors()
            }
        )
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid search parameters",
                "errors": e.errors()
            }
        )

@app.get("/recipes/{recipe_id}")
async def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """指定されたIDのレシピを取得する"""
    logger.info(f"Fetching recipe with id={recipe_id}")
    with db as session:
        recipe = await get_recipe(db=session, recipe_id=recipe_id)
    if recipe is None:
        logger.warning(f"Recipe not found: id={recipe_id}")
        error = ErrorResponse(
            code=404,
            message="Recipe not found",
            type="not_found"
        )
        return StandardResponse.error_response(error=error)
    return StandardResponse.success_response(data=jsonable_encoder(recipe))

@app.put("/recipes/{recipe_id}")
async def update_recipe_endpoint(recipe_id: int, recipe_update: RecipeUpdate, db: Session = Depends(get_db)):
    """レシピを更新する"""
    logger.info(f"Updating recipe: id={recipe_id}")
    with db as session:
        recipe = await update_recipe(db=session, recipe_id=recipe_id, recipe_update=recipe_update)
    if recipe is None:
        logger.warning(f"Recipe not found: id={recipe_id}")
        error = ErrorResponse(
            code=404,
            message="Recipe not found",
            type="not_found"
        )
        return StandardResponse.error_response(error=error)
    return StandardResponse.success_response(data=jsonable_encoder(recipe))

@app.delete("/recipes/{recipe_id}")
async def delete_recipe_endpoint(recipe_id: int, db: Session = Depends(get_db)):
    """レシピを削除する"""
    logger.info(f"Deleting recipe: id={recipe_id}")
    with db as session:
        success = await delete_recipe(db=session, recipe_id=recipe_id)
    if not success:
        logger.warning(f"Recipe not found: id={recipe_id}")
        error = ErrorResponse(
            code=404,
            message="Recipe not found",
            type="not_found"
        )
        return StandardResponse.error_response(error=error)
    return StandardResponse.success_response(data={"success": True})
