# Django сервис

# nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

FROM python:3.10.13

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONHASHSEED=0 

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx supervisor

# 🔹 Устанавливаем часовой пояс без интерактивного выбора
ENV TZ=Europe/Moscow
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

RUN pip install --upgrade pip

RUN pip install \
    redis==5.2.1 \
    requests==2.32.3 \
    pytest==8.3.4 \
    rich==13.9.4

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
RUN pip install opencv-python==4.11.0.86
RUN pip install -U ultralytics==8.3.70
RUN pip install celery==5.4.0
RUN pip install lapx==0.5.11
RUN pip install shapely==2.0.5
RUN pip install fastapi uvicorn
RUN pip install shapely==2.0.7
RUN pip install kornia==0.8.0
RUN pip install onnxruntime==1.21.0
RUN pip install super-gradients==3.7.1


COPY . .
EXPOSE 8546
