from configs.logger import setup_logging
setup_logging()
import logging

import numpy as np
import cv2
import base64
import json
import os
import redis

from datetime import datetime
from copy import deepcopy
from metaclasses.singletone import Singletone


REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_DECODE_RESPONSES = bool(os.getenv('REDIS_DECODE_RESPONSES'))
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT'))
REDIS_SOCKET_KEEPALIVE = bool(os.getenv('REDIS_SOCKET_KEEPALIVE'))
REDIS_HEALTH_CHECK_INTERVAL = int(os.getenv('REDIS_HEALTH_CHECK_INTERVAL'))
REDIS_POOL = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=REDIS_DECODE_RESPONSES,
    socket_keepalive=REDIS_SOCKET_KEEPALIVE,
    health_check_interval=REDIS_HEALTH_CHECK_INTERVAL,
)

redis_client = redis.Redis(connection_pool=REDIS_POOL)

container_id = os.getenv("CONTAINER_ID")


class RedisService(metaclass=Singletone):
    def __init__(self):
        self.redis_client = redis_client
        logging.info(f"✅ инициализация RedisService")
        self.data_key = f"nn_data_{container_id}"
        self.frame_key = f"nn_frame_base64_{container_id}"
        self.thumbnail_key = f"nn_thumbnail_base64_{container_id}"
        self.full_data_key = f"nn_full_data_{container_id}"

    def send_data(
        self,
        frame,
        container_id: int, 
        thumbnail_size: tuple,
        thumbnail_quality: int,
        frame_size: tuple,
        frame_quality: int,
        data = None,
        only_alert = None
        ) -> None:


        frame_resized = cv2.resize(frame, (960, 540))
        _, thumbnail_buffer = cv2.imencode('.jpg', frame_resized, [int(cv2.IMWRITE_JPEG_QUALITY), thumbnail_quality])


        self.data_key = f"nn_data_{container_id}"
        self.frame_key = f"nn_frame_base64_{container_id}"
        self.thumbnail_key = f"nn_thumbnail_base64_{container_id}"
        self.full_data_key = f"nn_full_data_{container_id}"

        success, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not success or encoded_frame is None:
            logging.error("Ошибка кодирования изображения")
            return {"error": "Ошибка кодирования изображения"}
        base64_frame = base64.b64encode(encoded_frame.tobytes()).decode('utf-8')

        frame_base64 = base64_frame
        thumbnail_base64 = base64.b64encode(thumbnail_buffer).decode('utf-8')
        
        
                
        self.check_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.check_time_key = f"time_check_{container_id}"


        self.redis_alert_data_key = f"only_alert_status_data_{container_id}"
        self.alert_key = f"alert_data_{container_id}"
        alert_data = { self.redis_alert_data_key: 
            {
                self.alert_key: only_alert,
                self.check_time_key: self.check_time

            }
        }
        self.redis_client.set(self.redis_alert_data_key, json.dumps(alert_data))


        self.only_frame_data_key = f"only_frame_data_{container_id}"
        self.frame_key = f"frame_data_{container_id}"
        frame_data = { self.only_frame_data_key: 
            {
                self.frame_key: frame_base64,
                self.alert_key: only_alert,
                self.check_time_key: self.check_time
            }
        }
        self.redis_client.set(self.only_frame_data_key, json.dumps(frame_data))


        self.only_thhumbnail_data_key = f"only_thumbnail_data_{container_id}"
        self.thumbnail_key = f"thumbnail_data_{container_id}"
        thumbnail_data = { self.only_thhumbnail_data_key: 
            {
                self.thumbnail_key: thumbnail_base64,
                self.alert_key: only_alert,
                self.check_time_key: self.check_time
            }
        }
        self.redis_client.set(self.only_thhumbnail_data_key, json.dumps(thumbnail_data))


    def get_data(self) -> dict:
        data = self.redis_client.get(self.full_data_key)
        if data is None:
            return None
        return json.loads(data)
    

    def get_params_from_frontend(self, camera_id: int) -> dict:
        key = f"params_data_{camera_id}"
        data = self.redis_client.get(key)
        if data is None:
            return None
        return json.loads(data)

