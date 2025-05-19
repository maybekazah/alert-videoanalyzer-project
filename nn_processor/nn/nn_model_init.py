
from configs.logger import setup_logging
setup_logging()
import logging


from nn.base_model import BaseYOLOModel
from metaclasses.singletone import Singletone


class DetectionModel(BaseYOLOModel, metaclass=Singletone):
    def __init__(self):
        logging.info(f"инициализация DetectionModel")
        super().__init__('detection_model')


detection_model = DetectionModel()