"""
ResuMiner 统一自定义异常体系

所有业务代码应抛出对应的自定义异常，杜绝裸抛 Exception
"""


class ResuMinerException(Exception):
    """ResuMiner 基础异常类"""
    
    def __init__(self, message: str = None, code: str = None, details: dict = None):
        self.message = message or "ResuMiner 异常"
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"[{self.code}] {self.message} - Details: {self.details}"
        return f"[{self.code}] {self.message}"


# ============================================
# 爬虫相关异常
# ============================================

class CrawlerException(ResuMinerException):
    """爬虫基础异常"""
    
    def __init__(self, message: str = None, code: str = "CRAWLER_ERROR", details: dict = None):
        super().__init__(message or "爬虫异常", code, details)


class RequestException(CrawlerException):
    """请求异常"""
    
    def __init__(self, message: str = None, url: str = None, status_code: int = None, details: dict = None):
        self.url = url
        self.status_code = status_code
        error_details = details or {}
        if url:
            error_details['url'] = url
        if status_code:
            error_details['status_code'] = status_code
        super().__init__(message or "请求异常", "REQUEST_ERROR", error_details)


class ResponseParseException(CrawlerException):
    """响应解析异常"""
    
    def __init__(self, message: str = None, response_data: str = None, details: dict = None):
        error_details = details or {}
        if response_data:
            error_details['response_preview'] = response_data[:200] if len(response_data) > 200 else response_data
        super().__init__(message or "响应解析异常", "PARSE_ERROR", error_details)


class RateLimitException(CrawlerException):
    """频率限制异常"""
    
    def __init__(self, message: str = None, retry_after: int = None, details: dict = None):
        self.retry_after = retry_after
        error_details = details or {}
        if retry_after:
            error_details['retry_after'] = retry_after
        super().__init__(message or "触发频率限制", "RATE_LIMIT", error_details)


class CaptchaException(CrawlerException):
    """验证码异常"""
    
    def __init__(self, message: str = None, captcha_url: str = None, details: dict = None):
        self.captcha_url = captcha_url
        error_details = details or {}
        if captcha_url:
            error_details['captcha_url'] = captcha_url
        super().__init__(message or "需要验证码验证", "CAPTCHA_REQUIRED", error_details)


class LoginRequiredException(CrawlerException):
    """需要登录异常"""
    
    def __init__(self, message: str = None, platform: str = None, details: dict = None):
        self.platform = platform
        error_details = details or {}
        if platform:
            error_details['platform'] = platform
        super().__init__(message or "需要登录", "LOGIN_REQUIRED", error_details)


class EmptyResultException(CrawlerException):
    """空结果异常"""
    
    def __init__(self, message: str = None, keyword: str = None, page: int = None, details: dict = None):
        self.keyword = keyword
        self.page = page
        error_details = details or {}
        if keyword:
            error_details['keyword'] = keyword
        if page is not None:
            error_details['page'] = page
        super().__init__(message or "返回空结果", "EMPTY_RESULT", error_details)


# ============================================
# 配置相关异常
# ============================================

class ConfigException(ResuMinerException):
    """配置异常"""
    
    def __init__(self, message: str = None, config_key: str = None, details: dict = None):
        self.config_key = config_key
        error_details = details or {}
        if config_key:
            error_details['config_key'] = config_key
        super().__init__(message or "配置异常", "CONFIG_ERROR", error_details)


class ConfigNotFoundException(ConfigException):
    """配置未找到异常"""
    
    def __init__(self, message: str = None, config_key: str = None, details: dict = None):
        super().__init__(message or "配置项未找到", config_key, details)
        self.code = "CONFIG_NOT_FOUND"


# ============================================
# 数据处理相关异常
# ============================================

class ETLException(ResuMinerException):
    """数据处理异常"""
    
    def __init__(self, message: str = None, code: str = "ETL_ERROR", details: dict = None):
        super().__init__(message or "数据处理异常", code, details)


class DataValidationException(ETLException):
    """数据验证异常"""
    
    def __init__(self, message: str = None, field: str = None, value: any = None, details: dict = None):
        self.field = field
        self.value = value
        error_details = details or {}
        if field:
            error_details['field'] = field
        if value is not None:
            error_details['value'] = str(value)
        super().__init__(message or "数据验证失败", "VALIDATION_ERROR", error_details)


class DataTransformException(ETLException):
    """数据转换异常"""
    
    def __init__(self, message: str = None, transform_type: str = None, details: dict = None):
        self.transform_type = transform_type
        error_details = details or {}
        if transform_type:
            error_details['transform_type'] = transform_type
        super().__init__(message or "数据转换失败", "TRANSFORM_ERROR", error_details)


# ============================================
# RPC 相关异常
# ============================================

class RPCException(ResuMinerException):
    """RPC 异常"""
    
    def __init__(self, message: str = None, rpc_method: str = None, details: dict = None):
        self.rpc_method = rpc_method
        error_details = details or {}
        if rpc_method:
            error_details['rpc_method'] = rpc_method
        super().__init__(message or "RPC 调用异常", "RPC_ERROR", error_details)


class RPCConnectionException(RPCException):
    """RPC 连接异常"""
    
    def __init__(self, message: str = None, host: str = None, port: int = None, details: dict = None):
        self.host = host
        self.port = port
        error_details = details or {}
        if host:
            error_details['host'] = host
        if port:
            error_details['port'] = port
        super().__init__(message or "RPC 连接失败", "RPC_CONNECTION_ERROR", error_details)


class RPCTimeoutException(RPCException):
    """RPC 超时异常"""
    
    def __init__(self, message: str = None, timeout: float = None, details: dict = None):
        self.timeout = timeout
        error_details = details or {}
        if timeout:
            error_details['timeout'] = timeout
        super().__init__(message or "RPC 调用超时", "RPC_TIMEOUT", error_details)
