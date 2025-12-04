FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .

CMD ["python", "app.py"]

# docker run -it --rm -d -e DISPLAY=$env:DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ${PWD}/data/bind_mount:/app/data/bind_mount -v text-data:/app/data/volume text-monitor
# docker cp "C:\Users\reth7\OneDrive\Desktop\Docker3\text).txt" "01f3851ec880fd2623c81257c3ef38f8d6df8e98daae43e7fe034ed8ce720ff4:/app/data/volume/text.txt"