from configs.logger import setup_logging
setup_logging()
import logging

import cv2
import numpy as np

from metaclasses.singletone import Singletone
from modules.states.resize_box import resize_box


class CalculationFunctions(metaclass=Singletone):
    def __init__(self) -> None:
        logging.info(f"инициализация NeuralProcessingFunctions")


    def get_data_detection_result_service(
        self,
        detect_boxes_with_classes: list, 
        class_index_list: list
    ) -> dict:
        detection_status = {}

        try:
            for item in detect_boxes_with_classes:
                _, class_id = item  # Теперь item = [[x1, y1, x2, y2], class_id]

                if class_id in class_index_list:
                    if class_id not in detection_status:
                        detection_status[class_id] = {
                            "class_index": class_id,
                            "count": 0
                        }
                    detection_status[class_id]["count"] += 1

        except Exception as e:
            logging.error(f'Ошибка: {e} в get_data_detection_result_service')

        return detection_status



    def get_list_of_all_detect_boxes_service(
        self,
        detect_boxes_with_classes: list,
        class_index_list: list,
    ) -> list:
        list_of_detect_boxes = []

        try:
            for item in detect_boxes_with_classes:
                box, class_id = item  # item = [[x1, y1, x2, y2], class_id]

                if class_id in class_index_list:
                    list_of_detect_boxes.append(box)

        except Exception as e:
            logging.error(f'Ошибка: {e} в get_list_of_all_detect_boxes_service')

        return list_of_detect_boxes


    def check_line_intersection(
        self,
        p1, 
        p2, 
        q1, 
        q2
        ):
        """Проверяет, пересекаются ли два отрезка p1-p2 и q1-q2."""
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
    

    def is_box_intersecting_polygon_service(
        self, 
        box, 
        polygon_points,
        resize_detection_boxes
        ):
        try:
            x1, y1, x2, y2 = map(int, box)

            if resize_detection_boxes != 0:
                x1, y1, x2, y2 = resize_box(x1, y1, x2, y2, resize_detection_boxes)
                

            polygon_points = np.array([[int(pt[0]), int(pt[1])] for pt in polygon_points], dtype=np.int32)

            if len(polygon_points) < 3:
                raise ValueError("Многоугольник должен содержать минимум три точки.")

            box_lines = [
                [(x1, y1), (x2, y1)], 
                [(x2, y1), (x2, y2)],
                [(x2, y2), (x1, y2)],
                [(x1, y2), (x1, y1)]
            ]

            for i in range(len(polygon_points)):
                pt1 = tuple(polygon_points[i])
                pt2 = tuple(polygon_points[(i + 1) % len(polygon_points)])
                for box_line in box_lines:
                    box_pt1, box_pt2 = box_line
                    if self.check_line_intersection(box_pt1, box_pt2, pt1, pt2):
                        return True

            box_vertices = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            for vertex in box_vertices:
                if cv2.pointPolygonTest(polygon_points, vertex, False) >= 0:
                    return True

            for vertex in polygon_points:
                if x1 <= vertex[0] <= x2 and y1 <= vertex[1] <= y2:
                    return True

        except Exception as e:
            logging.error(f"Ошибка: {e}")
            return False
        return False


    def get_alert_for_any_box_intersecting_service(
        self,
        list_of_detect_boxes: list,
        polygon_points: list,
        resize_detection_boxes: int
    ) -> bool:
        if list_of_detect_boxes:
            try:
                for box in list_of_detect_boxes:
                    if box is not None:
                        if self.is_box_intersecting_polygon_service(box, polygon_points, resize_detection_boxes):
                            return True
                return False
            except Exception as e:
                logging.error(f'Ошибка: {e} в get_alert_for_any_box_intersecting')
                return False
        return False

