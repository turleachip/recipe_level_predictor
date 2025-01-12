import os
import logging
import uuid
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from datetime import datetime
from typing import Optional, Dict, Any

# ログディレクトリの作成
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# ログファイルのパス設定
log_file = os.path.join(log_dir, "app.log")

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """カスタムJSONフォーマッタ"""
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # 基本フィールド
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        
        # コンテキスト情報
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'ip_address'):
            log_record['ip_address'] = record.ip_address
        if hasattr(record, 'path'):
            log_record['path'] = record.path
        if hasattr(record, 'method'):
            log_record['method'] = record.method
        if hasattr(record, 'status_code'):
            log_record['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms

class ContextLogger(logging.Logger):
    """コンテキスト情報を持つロガー"""
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self._context: Dict[str, Any] = {}

    def bind(self, **kwargs) -> None:
        """コンテキスト情報を追加"""
        self._context.update(kwargs)

    def _log(self, level: int, msg: object, args: tuple, exc_info: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, stack_info: bool = False, stacklevel: int = 1) -> None:
        """ログ出力時にコンテキスト情報を追加"""
        if extra is None:
            extra = {}
        extra.update(self._context)
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

def setup_logger() -> ContextLogger:
    """ロガーの設定"""
    logging.setLoggerClass(ContextLogger)
    logger = logging.getLogger('ff14_recipe_predictor')
    logger.setLevel(logging.INFO)

    # ファイルハンドラの設定（ローテーション付き）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(module)s %(function)s %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # ハンドラの追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# グローバルロガーの設定
logger = setup_logger()

def get_request_id() -> str:
    """リクエストIDを生成"""
    return str(uuid.uuid4())

def bind_request_context(logger: ContextLogger, request_id: str, method: str, path: str, ip_address: Optional[str] = None) -> None:
    """リクエストコンテキストをロガーにバインド"""
    logger.bind(
        request_id=request_id,
        method=method,
        path=path,
        ip_address=ip_address
    ) 