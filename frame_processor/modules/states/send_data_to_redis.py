from configs.logger import setup_logging
import logging
setup_logging()


from services.redis import RedisService
redis_service = RedisService()


def send_data_to_redis(context):
    detection_result = context.get('detection_model_result')
    alert_status = context.get('alert_status', False)
    only_alert= None
    alert_data = None
    if detection_result:
        alert_data = {
            "data_detection_result": detection_result,
            "alert_status": alert_status
        }
        only_alert = {"alert_status": alert_status}

    redis_service.send_data(
        context.get('frame'),
        context.get('camera_id'),
        context.get('thumbnail_size'),
        context.get('thumbnail_quality'),
        context.get('frame_size'),
        context.get('frame_quality'),
        alert_data,
        only_alert
    )
