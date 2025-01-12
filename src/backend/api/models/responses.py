from typing import TypeVar, Generic, Optional, Dict, Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse

T = TypeVar("T")

class ErrorResponse(BaseModel):
    """エラーレスポンスモデル"""
    code: int
    message: str
    type: str = "validation_error"
    details: Optional[Dict[str, Any]] = {}

class StandardResponse(BaseModel, Generic[T]):
    """標準レスポンスモデル"""
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None
    meta: Optional[Dict[str, Any]] = None

    @classmethod
    def success_response(cls, data: Optional[T] = None, meta: Optional[Dict[str, Any]] = None) -> JSONResponse:
        """成功レスポンスを生成"""
        return JSONResponse(
            content={
                "success": True,
                "data": data,
                "meta": meta
            }
        )

    @classmethod
    def error_response(cls, error: ErrorResponse) -> JSONResponse:
        """エラーレスポンスを生成"""
        return JSONResponse(
            status_code=error.code,
            content={
                "success": False,
                "error": {
                    "type": error.type,
                    "message": error.message,
                    "details": error.details
                }
            }
        ) 