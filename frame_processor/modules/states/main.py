from configs.logger import setup_logging
setup_logging()
import logging

from metaclasses.singletone import Singletone
from datetime import time as dt

import time
import cv2
import os
import json
import numpy as np

from services.redis import RedisService
redis_service = RedisService()

from modules.states.processing import pypeline
import threading
import queue
from cv2 import cudacodec
from copy import deepcopy

# номер контейнера (=камеры) frame_collector реплики
CONTAINER_ID = os.getenv("CONTAINER_ID")

# автоматический запуск видео с камер
# -----------------------------------
DEFAULT_RUN = os.getenv("DEFAULT_RUN", "True").lower() == "true"



# включить пропуск по времени и время в секундах (пропускает на обработку один кадр в N секунд)
# будет пропускать кадры, и пропускать 1 кадр в заданное время
TIME_PAUSE_FOR_PROCESSING_FRAME = float(os.getenv("TIME_PAUSE_FOR_PROCESSING_FRAME", 0.0))
USE_TIME_PAUSE_FOR_PROCESSING_FRAME = os.getenv("USE_TIME_PAUSE_FOR_PROCESSING_FRAME", "False").lower() == "true"


# сохранять обнаруженные объекты в бд, не более раз в n секунд
# ------------------------------------------------------------
DEFAULT_ALERT_SAVE_TIMEOUT = int(os.getenv("DEFAULT_ALERT_SAVE_TIMEOUT", 5))


# сохранять ли оригинальные кадры 
SAVE_ORIGINAL_FRAME = os.getenv(f"SAVE_ORIGINAL_FRAME_{CONTAINER_ID}", "False").lower() == "true" 



# настройки для нейронной сети, уверенность и другие параметры
# ------------------------------------------------------------
DEFAULT_DETECTION_MODEL_IMGSZ = int(os.getenv(f'DEFAULT_DETECTION_MODEL_IMGSZ_{CONTAINER_ID}'))
DEFAULT_DETECTION_MODEL_CONF = float(os.getenv(f'DEFAULT_DETECTION_MODEL_CONF_{CONTAINER_ID}'))
DEFAULT_DETECTION_MODEL_IOU = float(os.getenv(f'DEFAULT_DETECTION_MODEL_IOU_{CONTAINER_ID}'))
DEFAULT_DETECTION_MODEL_HALF = os.getenv(f'DEFAULT_DETECTION_MODEL_HALF_{CONTAINER_ID}', "True").lower() == "true"


# список детектируемых стандартных yolo классов
# ---------------------------------------------
DEFAULT_LIST_OF_DETECT_CLASSES = json.loads(os.getenv(f'DEFAULT_LIST_OF_DETECT_CLASSES_{CONTAINER_ID}')) if os.getenv(f'DEFAULT_LIST_OF_DETECT_CLASSES_{CONTAINER_ID}') else [0]

# детектировать ли вообще объекты, с пересечением с рамкой периметра (если задан False то алёрты срабатывают по всему кадру)
# --------------------------------------------------------------------------------------------------------------------------
DEFAULT_DETECT_WITH_INTERSECTION = os.getenv("DEFAULT_DETECT_WITH_INTERSECTION", "False").lower() == "true"


# настройки отрисовки детектируемых объектов и рамки периметра
# ------------------------------------------------------------
# отрисовывать ли вообще результаты
DEFAULT_DRAW_RESULT = os.getenv("DEFAULT_DRAW_RESULT", "True").lower() == "true"
DEFAULT_DRAW_DETECT_BOXES = os.getenv("DEFAULT_DRAW_DETECT_BOXES", "False").lower() == "true"
DEFAULT_DRAW_PERIMETER = os.getenv("DEFAULT_DRAW_PERIMETER", "False").lower() == "true"


# настройки для отображения для стандартной отрисовки через yolo ultralytics
# --------------------------------------------------------------------------
USE_ULTRALITYCS_PLOT_VISUALISATION_BOXES_AND_LABELS = os.getenv("USE_ULTRALITYCS_PLOT_VISUALISATION_BOXES_AND_LABELS", "True").lower() == "true"
DRAW_LABELS = os.getenv("DRAW_LABELS", "True").lower() == "true"
SHOW_CONF = os.getenv("SHOW_CONF", "False").lower() == "true"
LABELS_FONT_SIZE = float(os.getenv(f'LABELS_FONT_SIZE'))


# цвета контура детекции и рамки периметра
# ----------------------------------------
DRAW_LINE_THICKLESS = int(os.getenv("DRAW_LINE_THICKLESS", 16))
BOX_COLOR = tuple(map(int, os.getenv("BOX_COLOR", "255,0,0").split(',')))
COUNTOR_COLOR = tuple(map(int, os.getenv("COUNTOR_COLOR", "255,0,0").split(',')))


# настройки возвращаемых кадров и миниатюр камер на страницу интерфейса для фронтенда и их качество/сжатие
# --------------------------------------------------------------------------------------------------------
THUMBNAIL_SIZE = tuple(map(int, os.getenv("THUMBNAIL_SIZE", "1920,1080").split(',')))
FRAME_SIZE = tuple(map(int, os.getenv("FRAME_SIZE", "1920,1080").split(',')))
THUMBNAIL_QUALITY = int(os.getenv("THUMBNAIL_QUALITY", 100))
FRAME_QUALITY = int(os.getenv("FRAME_QUALITY", 100))


# настройки для контура границ детекции по кадру
# ----------------------------------------------
DAY_CONTOUR = json.loads(os.getenv(f'DAY_CONTOUR')) if os.getenv(f'DAY_CONTOUR') else [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]
NIGHT_CONTOUR = json.loads(os.getenv(f'NIGHT_CONTOUR')) if os.getenv(f'NIGHT_CONTOUR') else [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]
DEFAULT_CONTOUR = json.loads(os.getenv(f'DEFAULT_CONTOUR_{CONTAINER_ID}')) if os.getenv(f'DEFAULT_CONTOUR_{CONTAINER_ID}') else [[0, 0], [1920, 0], [1920, 1080], [0, 1080]]

USE_DAY_COUNTOR = os.getenv("USE_DAY_COUNTOR", "True").lower() == "true"
DAY_COUNTOR_TIME_START = tuple(map(int, os.getenv("DAY_COUNTOR_TIME_START", "12,00,00").split(',')))
DAY_COUNTOR_TIME_END = tuple(map(int, os.getenv("DAY_COUNTOR_TIME_END", "16,00,00").split(',')))

USE_NIGHT_COUNTOR = os.getenv("USE_NIGHT_COUNTOR", "True").lower() == "true"
NIGHT_COUNTOR_TIME_START = tuple(map(int, os.getenv("NIGHT_COUNTOR_TIME_START", "21,00,00").split(',')))
NIGHT_COUNTOR_TIME_END = tuple(map(int, os.getenv("NIGHT_COUNTOR_TIME_END", "8,00,00").split(',')))


# параметр для настройки размера пересекаемого бокса и его отображения
# -------------------------------------------------
RESIZE_PERCENT_OF_DETECTED_BOX = int(os.getenv(f"RESIZE_PERCENT_OF_DETECTED_BOX_{CONTAINER_ID}"))
DRAW_RESIZED_BOXES = os.getenv(f"DRAW_RESIZED_BOXES_{CONTAINER_ID}", "False").lower() == "true"



if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    logging.info("CUDA доступна, включаем GPU-ускорение")
    USE_CUDA = True
else:
    logging.info("CUDA не доступна, работаем на CPU")
    USE_CUDA = False


class MainProcessing(metaclass=Singletone):
    def __init__(
            self, 
            camera_id: int,
            video_path: str
            ):
        self.camera_id = camera_id
        self.video_path = video_path
        if USE_CUDA:
            self.gpu_frame = cv2.cuda_GpuMat()
        self.pypeline = pypeline
        self.frame_queue = queue.Queue(maxsize=5)
        self._stop_event = threading.Event()


    def define_params(self):
        
        self.context = {}
        self.context['frame_counter'] = 0
        self.context['frame'] = None
        self.context['cap'] = None
        self.context['processed_frame'] = None
        self.context['alert_status'] = False

        self.context['run'] = DEFAULT_RUN
        self.context['camera_id'] = CONTAINER_ID
        self.context['video_path'] = self.video_path
        self.context['alert_save_timeout'] = DEFAULT_ALERT_SAVE_TIMEOUT
        self.context['detect_with_perimeter_intersection'] = DEFAULT_DETECT_WITH_INTERSECTION
        self.context['draw_result'] = DEFAULT_DRAW_RESULT
        self.context['draw_detect_boxes'] = DEFAULT_DRAW_DETECT_BOXES
        self.context['draw_perimeter'] = DEFAULT_DRAW_PERIMETER
        self.context['detection_model_imgsz'] = DEFAULT_DETECTION_MODEL_IMGSZ
        self.context['detection_model_conf'] = DEFAULT_DETECTION_MODEL_CONF
        self.context['detection_model_iou'] = DEFAULT_DETECTION_MODEL_IOU
        self.context['detection_model_half'] = DEFAULT_DETECTION_MODEL_HALF
        self.context['list_of_detect_classes'] = DEFAULT_LIST_OF_DETECT_CLASSES
        self.context['contour_points_list'] = DEFAULT_CONTOUR
        self.context['day_contour'] = DAY_CONTOUR
        self.context['night_contour'] = NIGHT_CONTOUR

        self.context['box_color'] = BOX_COLOR
        self.context['countour_color'] = COUNTOR_COLOR
        self.context['thumbnail_size'] = THUMBNAIL_SIZE
        self.context['frame_size'] = FRAME_SIZE
        self.context['thumbnail_quality'] = THUMBNAIL_QUALITY
        self.context['frame_quality'] = FRAME_QUALITY
        self.context['draw_line_thickless'] = DRAW_LINE_THICKLESS
        self.context['use_day_countour'] = USE_DAY_COUNTOR
        self.context['day_countour_time_start'] = DAY_COUNTOR_TIME_START
        self.context['day_countour_time_end'] = DAY_COUNTOR_TIME_END
        self.context['use_night_countour'] = USE_NIGHT_COUNTOR
        self.context['night_countour_time_start'] = NIGHT_COUNTOR_TIME_START
        self.context['night_countour_time_end'] = NIGHT_COUNTOR_TIME_END

        self.context['time_pause_for_processing_frame'] = TIME_PAUSE_FOR_PROCESSING_FRAME
        self.context['use_time_pause_for_processing_frame'] = USE_TIME_PAUSE_FOR_PROCESSING_FRAME

        self.context['draw_labels'] = DRAW_LABELS
        self.context['show_conf'] = SHOW_CONF
        self.context['labels_font_size'] = LABELS_FONT_SIZE

        self.context['use_ultralitycs_plot_visualisation_boxes_and_labels'] = USE_ULTRALITYCS_PLOT_VISUALISATION_BOXES_AND_LABELS
        
        self.context['save_original_frame'] = SAVE_ORIGINAL_FRAME
        self.context['original_frame'] = None

        self.context['resize_detection_boxes'] = RESIZE_PERCENT_OF_DETECTED_BOX
        self.context['draw_resized_boxes'] = DRAW_RESIZED_BOXES


        self.time_params =['current_time']
        self.param_checks = {
            'list_of_detect_classes': (list, lambda x: len(x) >= 1),
            'detection_model_conf': (float, lambda x: x >= 0.0),
            'detection_model_iou': (float, lambda x: x >= 0.0),
            
            'detection_model_imgsz': (int, lambda x: x >= 0),
            'alert_save_timeout': (int, lambda x: x > 0),
            'labels_font_size': (float, lambda x: x >= 0),
            'camera_id': (int, lambda x: x > 0),
            'thumbnail_quality': (int, lambda x: x > 0),
            'frame_quality': (int, lambda x: x > 0),
            'draw_line_thickless': (int, lambda x: x > 0),
            'contour_points_list': (list, lambda x: len(x) >= 3),
            
            'day_contour': (list, lambda x: len(x) >= 3),
            'night_contour': (list, lambda x: len(x) >= 3),

            'box_color': (list, lambda x: isinstance(x, list) and len(x) == 3),
            'countour_color': (list, lambda x: isinstance(x, list) and len(x) == 3),
            'thumbnail_size': (list, lambda x: isinstance(x, list) and len(x) == 2),
            'frame_size': (list, lambda x: isinstance(x, list) and len(x) == 2),


            'day_countour_time_start': (list, lambda x: isinstance(x, list) and len(x) == 3),
            'day_countour_time_end': (list, lambda x: isinstance(x, list) and len(x) == 3),

            'night_countour_time_start': (list, lambda x: isinstance(x, list) and len(x) == 3),
            'night_countour_time_end': (list, lambda x: isinstance(x, list) and len(x) == 3),

            'time_pause_for_processing_frame': (float, lambda x: x >= 0.0)

        }

        self.bool_params = [
            'detection_model_half',
            'draw_result',
            'draw_detect_boxes',
            'draw_perimeter',
            'run', 
            'detect_with_perimeter_intersection',
            'show_debug_list_in_terminal',
            'draw_labels',
            'use_day_countour',
            'use_night_countour',
            'use_time_pause_for_processing_frame', 
            'show_conf',
            'use_ultralitycs_plot_visualisation_boxes_and_labels',
            'save_original_frame',
            'draw_resized_boxes'

        ]
        self.time_params =['current_time']
        self.str_params = ['video_path']


    def parse_time_tuple(self, time_tuple):
        if isinstance(time_tuple, tuple) and len(time_tuple) == 3:
            return dt(*time_tuple)
        return None


    def parse_control_params(self, context):
        params_from_frontend = redis_service.get_params_from_frontend(self.camera_id)
        if params_from_frontend is None:
            logging.debug("нет данных для управления циклом обработки с фронтенда")
            return

        if "data" in params_from_frontend:
            params_from_frontend = params_from_frontend["data"]

        for param, (expected_type, validator) in self.param_checks.items():
            if param in params_from_frontend:
                try:
                    value = expected_type(params_from_frontend[param])
                    if validator(value):

                        if param in {
                            'box_color', 
                            'countour_color', 
                            'thumbnail_size', 
                            'frame_size',
                            'day_countour_time_start',
                            'day_countour_time_end',
                            'night_countour_time_start',
                            'night_countour_time_end'
                            }:
                            
                            self.context[param] = tuple(value)
                        else:
                            self.context[param] = value
                    else:
                        logging.warning(f"{param} имеет недопустимое значение. Используется предыдущее: {self.context.get(param, 'не определено')}")
                except (ValueError, TypeError):
                    logging.warning(f"{param} имеет неверный тип данных.")

        for param in self.bool_params:
            if param in params_from_frontend:
                value = params_from_frontend[param]
                if isinstance(value, bool):
                    self.context[param] = value
                else:
                    logging.warning(f"{param} должен быть булевым значением. Используется предыдущее: {self.context.get(param, 'не определено')}")

        for param in self.str_params:
            if param in params_from_frontend:
                value = params_from_frontend[param]
                if isinstance(value, str) and value.strip():
                    self.context[param] = value
                else:
                    logging.warning(f"{param} должен быть непустой строкой. Используется предыдущее: {self.context.get(param, 'не определено')}")


        if 'show_debug_list_in_terminal' in self.context and self.context['show_debug_list_in_terminal']:
            for param in self.param_checks.keys():
                logging.debug(f"'{param}' : {self.context.get(param, 'Ошибка ключа: нет значения')}")
            for param in self.bool_params:
                logging.debug(f"'{param}' : {self.context.get(param, 'Ошибка ключа: нет значения')}")
            for param in self.str_params:
                logging.debug(f"'{param}' : {self.context.get(param, 'Ошибка ключа: нет значения')}")
            for param in self.time_params:
                logging.debug(f"'{param}' : {self.context.get(param, 'Ошибка ключа: нет значения')}") 


    def run(self) -> None:
        while True:
            try:
                self.define_params()
                while True:
                    try:
                        self.parse_control_params(self.context)
                        if self.context.get('run', False):
                            self.open_with_nvdec()
                        time.sleep(5)
                    except Exception as e:
                        logging.error(f'main process run: ошибка: {e}')
                        logging.info(f'main process run: повторная попытка через 5 секунд')
                        time.sleep(5)
                    finally:
                        cap = self.context.get('cap')
                        if cap:
                            cap.release()
                            logging.info("ожидание команды запуска видеообработки...")
            except Exception as main_e:
                logging.critical(f'ГЛАВНЫЙ ЦИКЛ УПАЛ: {main_e}, перезапускаем...')
                time.sleep(5)


    def open_with_nvdec(self):
        last_param_update_time = time.time()
        reader = cudacodec.createVideoReader(self.video_path)
        last_time = time.time()

        while self.context.get('run', True):
            ok, gpu_mat = reader.nextFrame()
            if not ok:
                break

            if USE_TIME_PAUSE_FOR_PROCESSING_FRAME and time.time() - last_time < TIME_PAUSE_FOR_PROCESSING_FRAME:
                continue
            last_time = time.time()

            if time.time() - last_param_update_time >= 2:
                self.parse_control_params(self.context)
                last_param_update_time = time.time()

            try:
                gpu_resized = cv2.cuda.resize(
                    gpu_mat,
                    (1920, 1080),
                    interpolation=cv2.INTER_LINEAR
                )

            except cv2.error as e:
                logging.warning(f"CUDA-resize не поддерживается, ресайз на CPU: {e}")
                cpu_tmp = gpu_mat.download()
                cpu_resized = cv2.resize(cpu_tmp, (1920, 1080), interpolation=cv2.INTER_LINEAR)
                cpu_frame = cpu_resized
            else:
                cpu_frame = gpu_resized.download()

            self.context['frame'] = cpu_frame
            self.context['thumbnail'] = None
            self.context['original_frame'] = deepcopy(cpu_frame)

            try:
                self.pypeline.processing(self.context)
            except Exception as e:
                logging.error(f"Ошибка в Pypeline: {e}")