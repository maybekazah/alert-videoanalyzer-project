from configs.logger import setup_logging
setup_logging()
import logging

from ultralytics import YOLO
import torch
import os


# путь к весам нейросети
# ----------------------
DETECTION_MODEL_PATH = os.getenv('DETECTION_MODEL_PATH')
# дефолтная видеокарта для обработки
CONTAINER_ID = os.getenv('CONTAINER_ID')

# ----------------------------------
DETECTION_MODEL_CUDA_DEVICE = os.getenv(f'DETECTION_MODEL_CUDA_DEVICE_{CONTAINER_ID}')


class BaseYOLOModel:
    def __init__(self, model_name):

        device_count = torch.cuda.device_count()
        devices = [f'cuda:{i}' for i in range(device_count)] + ['cpu']
        logging.info(f"Доступные устройства: {devices}")

        models = {
            "detection_model": (DETECTION_MODEL_PATH, DETECTION_MODEL_CUDA_DEVICE)
        }

        loaded_models = {
            model_name: YOLO(model_path).to(device)
            for model_name, (model_path, device) in models.items()
        }
    
        logging.info(f"Модели загружены на устройства: {[(name, device) for name, (_, device) in models.items()]}")

        self.model = loaded_models[model_name]
        self.device = models[model_name][1]
        logging.info(f"Модель '{model_name}' загружена на устройство: {self.device.upper()}")


    def predict(self, frame, **kwargs):
        if frame is None:
            logging.warning(f'в блоке predict frame is {None}')
        return self.model(frame, device=self.device, **kwargs)


    @property
    def names(self):
        return self.model.names

