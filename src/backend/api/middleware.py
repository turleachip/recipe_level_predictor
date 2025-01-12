from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import traceback
from time import time
from .logging_config import logger, get_request_id, bind_request_context
from .models.responses import StandardResponse, ErrorResponse
from pydantic import ValidationError

def create_error_response(status_code: int, message: str, error_type: str, details: dict = None) -> JSONResponse:
    """エラーレスポンスを作成する"""
    error = ErrorResponse(
        code=status_code,
        message=message,
        type=error_type,
        details=details
    )
    return StandardResponse.error_response(error=error)

async def logging_middleware(request: Request, call_next):
    """ロギングミドルウェア"""
    # リクエストIDの生成
    request_id = get_request_id()
    
    # リクエスト情報をログに追加
    bind_request_context(
        logger,
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        ip_address=request.client.host if request.client else None
    )
    
    # リクエスト開始時刻
    start_time = time()
    
    try:
        # リクエストの処理
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "ip_address": request.client.host if request.client else None
            }
        )
        response = await call_next(request)
        
        # レスポンスタイムの計算
        duration_ms = round((time() - start_time) * 1000, 2)
        
        # レスポンス情報をログに追加
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms
            }
        )
        
        return response
        
    except Exception as e:
        # エラー情報をログに追加
        duration_ms = round((time() - start_time) * 1000, 2)
        error_type = "internal_error"
        
        if isinstance(e, HTTPException):
            error_type = "http_error"
        elif isinstance(e, ValidationError):
            errors = []
            for error in e.errors():
                errors.append({
                    "field": error.get("loc", ["unknown"])[0],
                    "message": error.get("msg", "Unknown validation error"),
                    "type": error.get("type", "unknown_error")
                })

            logger.warning(
                f"Validation error occurred: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error_type": "validation_error",
                    "errors": errors
                }
            )
            return create_error_response(
                status_code=400,
                message="入力値が不正です",
                error_type="validation_error",
                details={"errors": errors}
            )
        elif isinstance(e, SQLAlchemyError):
            error_message = str(e)
            status_code = 500
            error_type = "database_error"

            # 一意性制約違反の検出
            if "Duplicate entry" in error_message and "uix_recipe_name_job" in error_message:
                status_code = 409
                error_type = "conflict_error"
                error_message = "同じ名前と職業の組み合わせのレシピが既に存在します"

            logger.error(
                f"Database error occurred: {error_message}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error_type": error_type,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            return create_error_response(
                status_code=status_code,
                message=error_message,
                error_type=error_type,
                details={"error": str(e)}
            )
        else:
            return create_error_response(
                status_code=500,
                message="An unexpected error occurred",
                error_type="internal_error",
                details={"error": str(e)}
            )

def setup_error_handlers(app: FastAPI) -> None:
    """エラーハンドラーの設定"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTPExceptionのハンドリング"""
        error_type = "http_error"
        
        # バリデーションエラーの場合は、error_typeを変更
        if exc.status_code == 400 and "validation" in str(exc.detail).lower():
            error_type = "validation_error"
        
        logger.warning(
            f"HTTP error occurred: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "error_type": error_type
            }
        )
        return create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_type=error_type
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """バリデーションエラーのハンドリング"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": error.get("loc", ["unknown"])[0],
                "message": error.get("msg", "Unknown validation error"),
                "type": error.get("type", "unknown_error")
            })

        error_message = "入力値が不正です"
        logger.warning(
            f"validation_error: {error_message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": "validation_error",
                "errors": errors,
                "status_code": 400
            }
        )

        error_response = ErrorResponse(
            code=400,
            message=error_message,
            type="validation_error",
            details={"errors": errors}
        )
        
        return StandardResponse.error_response(error=error_response)

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """データベースエラーのハンドリング"""
        error_message = str(exc)
        status_code = 500
        error_type = "database_error"

        # 一意性制約違反の検出
        if "Duplicate entry" in error_message and "uix_recipe_name_job" in error_message:
            status_code = 409
            error_type = "conflict_error"
            error_message = "同じ名前と職業の組み合わせのレシピが既に存在します"

        logger.error(
            f"Database error occurred: {error_message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": error_type,
                "error": str(exc),
                "traceback": traceback.format_exc()
            }
        )
        return create_error_response(
            status_code=status_code,
            message=error_message,
            error_type=error_type,
            details={"error": str(exc)}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """予期せぬエラーのハンドリング"""
        logger.error(
            f"Unexpected error occurred: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": "internal_error",
                "error": str(exc),
                "traceback": traceback.format_exc()
            }
        )
        return create_error_response(
            status_code=500,
            message="An unexpected error occurred",
            error_type="internal_error",
            details={"error": str(exc)}
        ) 