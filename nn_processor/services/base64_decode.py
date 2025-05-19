import base64
import cv2
import numpy as np


async def base64_decode(frame):
    img_bytes = base64.b64decode(frame)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)