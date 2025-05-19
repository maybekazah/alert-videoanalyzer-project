from configs.logger import setup_logging
setup_logging()
import logging

from metaclasses.singletone import Singletone
from datetime import datetime

import os
import cv2
import requests
import hashlib
import uuid



# качество сохраняемых картинок в бд

QUALITY_OF_SAVED_IMAGES = int(os.getenv(f'QUALITY_OF_SAVED_IMAGES'))


# урлы для внутреннего взаимодействия сервисов
# --------------------------------------------
ALERTS_URL = os.getenv('ALERTS_URL', "https://backend:8674/api/v1/alerts/")

# токен для внутреннего взаимодействия и сохранения алертов в бд
# --------------------------------------------------------------
TOKEN_FOR_FRAME_PROCESSOR = os.getenv("TOKEN_FOR_FRAME_PROCESSOR")


class DBService(metaclass=Singletone):
    def __init__(self) -> None:
        self.alerts_url = ALERTS_URL
        

    def create_alert(self, context, camera_id: int, message: dict, 
                 first_detection_datetime: datetime = None,
                 last_detection_datetime: datetime = None) -> dict:
        image = context['frame']

        try:
            if first_detection_datetime is None:
                first_detection_datetime = datetime.now()
            if last_detection_datetime is None:
                last_detection_datetime = first_detection_datetime

            output_dir = os.path.join("output", 
                                    first_detection_datetime.strftime("%Y"),
                                    first_detection_datetime.strftime("%m"),
                                    first_detection_datetime.strftime("%d"))
            os.makedirs(output_dir, exist_ok=True)

            unique_hash = hashlib.sha256(f"{first_detection_datetime}{uuid.uuid4().hex}".encode()).hexdigest()[:8]
            image_filename = f"{camera_id}_{first_detection_datetime.strftime('%H-%M-%S-%f')[:-3]}_{unique_hash}.jpg"
            image_path = os.path.join(output_dir, image_filename)
            
            cv2.imwrite(image_path, image, [
                cv2.IMWRITE_JPEG_QUALITY, QUALITY_OF_SAVED_IMAGES,
                cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
            ])

            
            # блок сохранения оригинального изображения без различных детекций
            # -------------------------------------------------------------------------------------------------------------------------------------
            if context['save_original_frame']:
                original_image = context['original_frame']
                original_image_output_dir = os.path.join("output/original",
                                    first_detection_datetime.strftime("%Y"),
                                    first_detection_datetime.strftime("%m"),
                                    first_detection_datetime.strftime("%d"))
                os.makedirs(original_image_output_dir, exist_ok=True)

                original_image_unique_hash = hashlib.sha256(f"{first_detection_datetime}{uuid.uuid4().hex}".encode()).hexdigest()[:8]
                original_image_filename = f"{camera_id}_{first_detection_datetime.strftime('%H-%M-%S-%f')[:-3]}_{original_image_unique_hash}.jpg"
                original_image_path = os.path.join(original_image_output_dir, original_image_filename)
                
                cv2.imwrite(original_image_path, original_image, [
                cv2.IMWRITE_JPEG_QUALITY, int(os.getenv(f'QUALITY_OF_SAVED_ORIGINAL_IMAGES_{camera_id}')),
                cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                cv2.IMWRITE_JPEG_OPTIMIZE, 1
                ])
            # ------------------------------------------------------------------------------------------------------------------------------------
                


            payload = {
                "camera_id": camera_id,
                "message": message,
                "first_detection_datetime": first_detection_datetime.isoformat(),
                "last_detection_datetime": last_detection_datetime.isoformat(),
                "image": image_path  
            }

            headers = {
                "Authorization": f"Token {TOKEN_FOR_FRAME_PROCESSOR}", 
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.alerts_url,
                json=payload,
                headers=headers,
                verify=False
            )

            if response.status_code == 201:
                logging.info(f"Alert created successfully for camera {camera_id}, saved at {image_path}")
                logging.critical(f"responce: {response.content}")
                return response.json()
            else:
                logging.error(f"Failed to create alert: {response.text}")
                return {"error": response.text}

        except Exception as e:
            logging.error(f"Error creating alert: {str(e)}")
            return {"error": str(e)}
            

    def update_alert(self, alert_id: int, data: dict = None, 
                    last_detection_datetime: datetime = None) -> dict:
        """
        Обновляет существующий алерт
        """
        try:
            url = f"{self.alerts_url}{alert_id}/"
            
            update_data = {}
            if data is not None:
                update_data["data"] = data
            if last_detection_datetime is not None:
                update_data["last_detection_datetime"] = last_detection_datetime.isoformat()

            response = requests.patch(url, json=update_data)
            
            if response.status_code == 200:
                logging.info(f"Alert {alert_id} updated successfully")
                return response.json()
            else:
                logging.error(f"Failed to update alert: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logging.error(f"Error updating alert: {str(e)}")
            return {"error": str(e)}


    def get_alert(self, alert_id: int) -> dict:
        """
        Получает данные алерта по ID
        
        """
        defaults = defaults
        context = {}
        try:
            url = f"{self.alerts_url}{alert_id}/"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get alert: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logging.error(f"Error getting alert: {str(e)}")
            return {"error": str(e)}
