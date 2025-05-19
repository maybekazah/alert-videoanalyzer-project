from configs.logger import setup_logging
setup_logging()
import logging


from fastapi import APIRouter
from pydantic import BaseModel

predict_router = APIRouter(prefix="/predict", tags=["predict"])


from services.base64_decode import base64_decode
from services.predict_boxes import get_predict_boxes_result



class PredictRequest(BaseModel):
    frame: str
    class_index_list : list
    imgsz: int
    conf: float
    iou: float
    half: bool



@predict_router.post("/get-predict-boxes")
async def get_predict_boxes(request: PredictRequest) -> dict:
    try:
        frame = await base64_decode(request.frame)
        
        detect_boxes, detect_boxes_with_classes = await get_predict_boxes_result(
            frame,
            request.class_index_list
        )

        return {"detect_boxes": detect_boxes, "detect_boxes_with_classes": detect_boxes_with_classes}

    except Exception as e:
        return {"get_predict_boxes error": str(e)}

