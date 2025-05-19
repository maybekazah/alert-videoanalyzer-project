from configs.logger import setup_logging
setup_logging()
import logging

from fastapi import FastAPI
from handlers.ping import ping_router
from handlers.predict import predict_router

import uvicorn

app = FastAPI()

app.include_router(ping_router)
app.include_router(predict_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8546)