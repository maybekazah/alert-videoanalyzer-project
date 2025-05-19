from configs.logger import setup_logging
setup_logging()
import logging

import cv2
import numpy as np
import cupy as cp 
import os


from metaclasses.singletone import Singletone


class VisualizationFunctions(metaclass=Singletone):
    def __init__(self) -> None:
        logging.info(f"✅ инициализация VisualizationFunctions")
    
    
    def draw_detection_model_result_without_plot_service(
        self,
        frame,
        boxes_with_classes: list,
        class_index_list: list,
        color: tuple[int, ...] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:

        if not isinstance(frame, np.ndarray):
            raise TypeError(f"frame должен быть np.ndarray, а пришёл {type(frame)}")
        
        try:
            for item in boxes_with_classes:
                box      = item[0]                 # [x1, y1, x2, y2]
                class_id = int(item[1])

                if class_id not in class_index_list:
                    continue

                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        except Exception as e:
            logging.error(f"Ошибка: {e} в draw_detection_model_result_service")

        return frame
 

    def draw_day_night_contour_service(
        self,
        frame,
        contour_points_list: list,
        color: tuple[int, ...] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        
        if not isinstance(frame, np.ndarray):
            raise TypeError(f"frame должен быть np.ndarray, а пришёл {type(frame)}")

        try:
            contour_points = np.array(contour_points_list, dtype=np.int32)
            contour_points = contour_points.reshape((-1, 1, 2))
            cv2.polylines(frame, [contour_points], isClosed=True, color=color, thickness=thickness)

        except Exception as e:
            logging.error(f'Ошибка: {e} в draw_day_night_contour_service')
        return frame
