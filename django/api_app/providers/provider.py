from api_app.services.redis import RedisService
from api_app.services.websocket import WebSocketService
from api_app.metaclasses.singletone import Singletone
from api_app.services.thumbnail_websocket import ThumbnailWebSocketService
from api_app.services.frame_websocket import FrameWebSocketService
from api_app.services.alert_websocket import AlertWebSocketService


class Provider(metaclass=Singletone):

    @staticmethod
    def get_postgres_db_repository():
        pass

    @staticmethod
    def get_redis_service() -> RedisService:
        return RedisService()

    @staticmethod
    def get_websocket_service() -> WebSocketService:
        return WebSocketService(RedisService())


    @staticmethod
    def get_alert_websocket_service() -> AlertWebSocketService:
        return AlertWebSocketService(RedisService())
    
    
    @staticmethod
    def get_frame_websocket_service() -> FrameWebSocketService:
        return FrameWebSocketService(RedisService())
    
    
    @staticmethod
    def get_thumbnail_websocket_service() -> ThumbnailWebSocketService:
        return ThumbnailWebSocketService(RedisService())