import asyncio
import cv2
import numpy as np
import base64
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# хранение активных соединений WebSocket
active_connections = []

# HTML-страница для тестирования WebSocket с видео
html_page = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Video Test</title>
    </head>
    <body>
        <h1>WebSocket Video Test</h1>
        <video id="video" width="640" height="480" autoplay></video>
        <script>
            if(navigator.webkitGetUserMedia!=null) { 
                var options = { 
                    video:true, 
                    audio:true 
            }; 
            
            // Запрашиваем доступ к веб-камере
                navigator.webkitGetUserMedia(options, 
                    function(stream) { 
                    // Получаем тег video
                    var video = document.getElementById('video-player'); 
                    // Включаем поток в тег video
                    video.srcObject = stream; 
                    }, 
                    function(e) { 
                    console.log("произошла ошибка"); 
                    } 
                ); 
            }
            
        
            let ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
            video.src = "data:image/jpeg;base64," + event.data;
            };
        </script>
    </body>
</html>
"""

# WebSocket endpoint


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # подключение нового WebSocket
    await websocket.accept()
    # добавление соединения в список активных
    active_connections.append(websocket)
    try:
        # ожидание кадров видео от WebSocket
        while True:
            # чтение кадра видео из WebSocket
            frame_bytes = await websocket.receive_bytes()
            # декодирование кадра видео из байтов в изображение
            # frame_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            # frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)
            # кодирование кадра видео в base64
            # retval, buffer = cv2.imencode('.jpg', frame)
            # frame_bytes = base64.b64encode(buffer).decode('utf-8')
            # отправка кадра видео всем активным соединениям
            for connection in active_connections:
                await connection.send_text(frame_bytes)
    finally:
        # удаление соединения из списка активных
        active_connections.remove(websocket)

# тестовая HTML-страница для WebSocket с видео


@app.get("/")
async def get():
    return HTMLResponse(html_page)
