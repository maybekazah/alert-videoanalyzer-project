from configs.logger import setup_logging
setup_logging()
import logging


from nn.nn_model_init import detection_model
import numpy as np
import os


DEFAULT_DETECTION_MODEL_IMGSZ_NN_PROCESSOR = int(os.getenv('DEFAULT_DETECTION_MODEL_IMGSZ_NN_PROCESSOR'))
DEFAULT_DETECTION_MODEL_CONF_NN_PROCESSOR = float(os.getenv('DEFAULT_DETECTION_MODEL_CONF_NN_PROCESSOR'))
DEFAULT_DETECTION_MODEL_IOU_NN_PROCESSOR = float(os.getenv('DEFAULT_DETECTION_MODEL_IOU_NN_PROCESSOR'))
DEFAULT_DETECTION_MODEL_HALF_NN_PROCESSOR = os.getenv('DEFAULT_DETECTION_MODEL_HALF_NN_PROCESSOR', "False").lower() == "true"


amimal = ['cat', 'dog']
vehicle = ['bicycle', 'car', 'motorcycle', 'bus', 'truck']

async def get_predict_boxes_result(
        frame,
        class_index_list: list = None,
        imgsz:int = DEFAULT_DETECTION_MODEL_IMGSZ_NN_PROCESSOR,
        conf:float = DEFAULT_DETECTION_MODEL_CONF_NN_PROCESSOR,
        iou:float = DEFAULT_DETECTION_MODEL_IOU_NN_PROCESSOR,
        half:bool = DEFAULT_DETECTION_MODEL_HALF_NN_PROCESSOR
    ) -> tuple[list, list] | tuple[None, None]:
    if not isinstance(frame, np.ndarray):
        logging.error("Ошибка: frame не является np.ndarray в get_predict_result()")
        return []

    if frame is not None:
        results = detection_model.predict(
            frame,
            imgsz=imgsz,
            conf=conf,
            iou=iou,
            half=half
        )


    for result in results:
        updated_names = {}
        for cls_id, name in result.names.items():
            if name in amimal:
                updated_names[cls_id] = 'animal'
            elif name in vehicle:
                updated_names[cls_id] = 'vehicle'
            else:
                updated_names[cls_id] = name
        result.names = updated_names


        detect_boxes = []
        detect_boxes_with_classes = []

        for box in results[0].boxes:
            box_coords = box.xyxy.cpu().numpy().tolist()[0]
            class_id = int(box.cls.item())

            if class_index_list:
                if class_id in class_index_list:
                    detect_boxes.append(box_coords)
                    detect_boxes_with_classes.append((box_coords, class_id))
            else:
                detect_boxes.append(box_coords)
                detect_boxes_with_classes.append((box_coords, class_id))
        return detect_boxes, detect_boxes_with_classes
    
    else:
        logging.error(f"get_predict_result:  frame is {None}")
        return None, None




