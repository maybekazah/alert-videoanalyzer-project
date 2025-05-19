from configs.logger import setup_logging
import logging
setup_logging()

import base64
import cv2
import os
import httpx


BALANCER_URL = os.getenv('BALANCER_URL')


def get_predict_from_nn_processor(context):
    """
    Кодирует кадр в base64 и отправляет на nn сервер.
    """
    if context.get('frame') is not None:
        try:
            if isinstance(context['frame'], cv2.cuda.GpuMat):
                context['frame'] = context['frame'].download()
            success, encoded_frame = cv2.imencode('.jpg', context['frame'], [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            if not success or encoded_frame is None:
                logging.error("Ошибка кодирования изображения")
                return {"error": "Ошибка кодирования изображения"}
            base64_frame = base64.b64encode(encoded_frame.tobytes()).decode('utf-8')

        except Exception as e:
            logging.error(f"Ошибка при обработке кадра: {e}")
            return {"error": f"Ошибка обработки кадра: {e}"}


        payload = {
                "frame":            base64_frame,
                "class_index_list": context["list_of_detect_classes"],
                "imgsz":            context["detection_model_imgsz"],
                "conf":             context["detection_model_conf"],
                "iou":              context["detection_model_iou"],
                "half":             context["detection_model_half"]
            }


    try:
        response = httpx.post(BALANCER_URL, json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()
        boxes              = result["detect_boxes"]
        boxes_with_classes = result["detect_boxes_with_classes"]

        return boxes, boxes_with_classes
    
    except httpx.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке контекста: {e}")


