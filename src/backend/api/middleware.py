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
            error_type = "validation_error"
        elif isinstance(e, SQLAlchemyError):
            error_type = "database_error"
            
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "error_type": error_type,
                "duration_ms": duration_ms,
                "traceback": traceback.format_exc()
            }
        )
        
        # エラーの種類に応じたレスポンスを返す
        if isinstance(e, HTTPException):
            return create_error_response(
                status_code=e.status_code,
                message=str(e.detail),
                error_type="http_error"
            )
        elif isinstance(e, ValidationError):
            return create_error_response(
                status_code=400,
                message="Invalid parameter value",
                error_type="validation_error",
                details={"errors": e.errors()}
            )
        elif isinstance(e, SQLAlchemyError):
            return create_error_response(
                status_code=500,
                message="Database error occurred",
                error_type="database_error",
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
        logger.warning(
            f"HTTP error occurred: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "error_type": "http_error"
            }
        )
        return create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_type="http_error"
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """バリデーションエラーのハンドリング"""
        logger.warning(
            f"Validation error occurred: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": "validation_error",
                "error": str(exc)
            }
        )
        return create_error_response(
            status_code=400,
            message="Invalid parameter value",
            error_type="validation_error",
            details={"errors": exc.errors()}
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """データベースエラーのハンドリング"""
        logger.error(
            f"Database error occurred: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": "database_error",
                "error": str(exc),
                "traceback": traceback.format_exc()
            }
        )
        return create_error_response(
            status_code=500,
            message="Database error occurred",
            error_type="database_error",
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