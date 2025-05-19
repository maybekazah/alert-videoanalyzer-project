from datetime import datetime, timedelta
from services.postgres_db import DBService
db_service = DBService()

ALERT_TIMERS = {}


def send_data_to_bd(context):
    camera_id = context['camera_id']
    if camera_id not in ALERT_TIMERS:
        ALERT_TIMERS[camera_id] = {
            'alert_save_timeout': 30,
            'end_alert_save_timeout': None,
            'start_alert_save_timeout': None
        }

    alert_data = {
        "data_detection_result": context['detection_model_result'],
        "alert_status": context['alert_status']
    }

    if alert_data['alert_status']:
        current_time = datetime.now()
        last_save_time = ALERT_TIMERS[camera_id]['start_alert_save_timeout']
        
        if last_save_time is None:
            time_diff = None
        else:
            time_diff = (current_time - last_save_time).total_seconds()

        if last_save_time is None or time_diff >= ALERT_TIMERS[camera_id]['alert_save_timeout']:
            ALERT_TIMERS[camera_id]['start_alert_save_timeout'] = current_time
            ALERT_TIMERS[camera_id]['end_alert_save_timeout'] = current_time + timedelta(seconds=ALERT_TIMERS[camera_id]['alert_save_timeout'])

            db_service.create_alert(context, camera_id, alert_data)
            

