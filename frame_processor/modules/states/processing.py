from configs.logger import setup_logging
import logging
setup_logging()


from metaclasses.singletone import Singletone
from modules.states.use_day_night_contours import use_day_night_contours
from modules.states.send_data_to_bd import send_data_to_bd
from modules.states.send_data_to_redis import send_data_to_redis
from modules.states.draw_context import draw_context
from modules.states.calculate_context_all_boxes_selected_classes import calculate_context_all_boxes_selected_classes
from modules.states.get_alert_status_with_intersection import get_alert_status_with_intersection
from modules.states.get_detection_data_all_selected_classes import get_detection_data_all_selected_classes
from modules.states.get_predict_from_nn_processor import get_predict_from_nn_processor


from typing import List, Tuple, Optional


# главный процесс со всеми состояниями
class Processing(metaclass=Singletone):

    def __init__(self) -> None:
        self.__goout_counter = 0
        self.__goout_status_status = False  # добавляем начальное значение

    def track_objects_on_frame(self, context, detect_boxes_with_classes):
        self.context = context

        # Берём из контекста предыдущие значения
        boxes_with_classes = detect_boxes_with_classes
        track_ids          = context.get("track_ids", [])
        target_track_id    = context.get("target_track_id")
        goout_status       = context.get("goout_status", False)

        # Получаем обновлённые параметры
        track_ids, target_track_id, goout_status = get_track_params(
            boxes_with_classes,
            track_ids,
            target_track_id,
            goout_status,
        )

        # Обновляем счётчик и финальный флаг
        if goout_status:
            self.__goout_counter += 1
        else:
            self.__goout_counter = 0

        # Записываем финальный статус именно в этот атрибут
        self.__goout_status_status = (self.__goout_counter >= 10)

        # Сохраняем обратно в контекст
        context["track_ids"]            = track_ids
        context["target_track_id"]      = target_track_id
        context["goout_status"]         = goout_status

        # Теперь передаём все 5 полей: track_ids, target, goout_status, counter, final_status
        logging.debug(
            "После трекинга: track_ids=%s, target=%s, goout_status=%s, counter=%d, final_status=%s",
            track_ids,
            target_track_id,
            goout_status,
            self.__goout_counter,
            self.__goout_status_status,
        )


    def processing(
            self, 
            context,
            ):
        
        # self.context = context

        detect_boxes, detect_boxes_with_classes = get_predict_from_nn_processor(context)

        # self.track_objects_on_frame(context, detect_boxes_with_classes)

        draw_context(context, detect_boxes, detect_boxes_with_classes)

        calculate_context_all_boxes_selected_classes(context, detect_boxes_with_classes)
 
        use_day_night_contours(context)
        
        get_alert_status_with_intersection(context)

        get_detection_data_all_selected_classes(context, detect_boxes_with_classes)

        send_data_to_redis(context)

        send_data_to_bd(context)



pypeline = Processing()



def get_track_params(
    predict_result_boxes_with_classes: List[Tuple[List[float], int]],
    track_ids: List[int],
    target_track_id: Optional[int],
    goout_status: bool
) -> Tuple[List[int], Optional[int], bool]:
    """
    Проверяет трек авто (классы 5 и 6) на наличие/отсутствие в кадре.

    :param predict_result_boxes_with_classes: список [(bbox, class_id), ...],
           где bbox = [x1, y1, x2, y2], class_id — целочисленный ID класса.
    :param track_ids: предыдущий список отслеживаемых track_id.
    :param target_track_id: ID конкретного авто, которое сейчас отслеживаем.
    :param goout_status: флаг, сигнализирующий, что авто «ушло» из поля зрения.
    :return: обновлённые (track_ids, target_track_id, goout_status).
    """

    try:
        current_ids = [cls for _, cls in predict_result_boxes_with_classes if cls in (0, 1, 2, 3, 5, 7, 15, 16)]

        if target_track_id is None and current_ids:
            target_track_id = current_ids[0]
            logging.info(f"Выбрали новый target_track_id={target_track_id}")

        if target_track_id in current_ids:
            goout_status = False
        else:

            goout_status = True
            target_track_id = None
            logging.info("Объект вышел из кадра, сбрасываем target_track_id")

        track_ids = current_ids

    except Exception as e:
        logging.error(f"Ошибка в get_track_params: {e}")

    return track_ids, target_track_id, goout_status
