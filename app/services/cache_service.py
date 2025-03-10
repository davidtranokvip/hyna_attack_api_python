import redis
import json
from functools import wraps

class CacheService:
    def __init__(self, app=None):
        self.redis = None
        self.default_ttl = 3600  # 1 giờ mặc định cho dữ liệu ít thay đổi
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        # Lấy cấu hình từ config của Flask app
        redis_host = app.config.get('REDIS_HOST', 'localhost')
        redis_port = app.config.get('REDIS_PORT', 6379)
        redis_db = app.config.get('REDIS_DB', 0)
        self.default_ttl = app.config.get('REDIS_DEFAULT_TTL', 3600)
        
        # Tạo connection pool
        pool = redis.ConnectionPool(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            socket_timeout=2,
            socket_connect_timeout=2,
            socket_keepalive=True,
            retry_on_timeout=True,
            max_connections=10
        )
        
        self.redis = redis.Redis(connection_pool=pool)
        
        # Kiểm tra kết nối
        try:
            self.redis.ping()
            app.logger.info("Redis connection successful")
        except redis.RedisError as e:
            app.logger.error(f"Redis connection failed: {str(e)}")
            self.redis = None
    
    def get(self, key):
        """Lấy dữ liệu từ cache"""
        if not self.redis:
            return None
            
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except:
            return None
    
    def set(self, key, value, ttl=None):
        """Lưu dữ liệu vào cache"""
        if not self.redis:
            return False
            
        if ttl is None:
            ttl = self.default_ttl
            
        try:
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except:
            return False
    
    def delete(self, key):
        """Xóa key khỏi cache"""
        if not self.redis:
            return False
            
        return self.redis.delete(key)
    
    def delete_pattern(self, pattern):
        """Xóa tất cả keys theo pattern"""
        if not self.redis:
            return 0
            
        keys = self.redis.keys(pattern)
        if not keys:
            return 0
            
        return self.redis.delete(*keys)
    
    def cached(self, key_prefix, ttl=None):
        """Decorator để cache kết quả của hàm"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Tạo key từ prefix và tham số
                key_parts = [key_prefix]
                # Thêm class name nếu là method
                if args and hasattr(args[0], '__class__'):
                    key_parts.append(args[0].__class__.__name__)
                # Thêm các tham số vào key
                for arg in args[1:]:
                    key_parts.append(str(arg))
                for k, v in kwargs.items():
                    key_parts.append(f"{k}:{v}")
                
                cache_key = ":".join(key_parts)
                
                # Thử lấy từ cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Gọi hàm gốc
                result = func(*args, **kwargs)
                
                # Lưu vào cache
                self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
cache = CacheService()