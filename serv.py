import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Создание очереди для буферизации кадров видео
# Задайте максимальный размер очереди по своим потребностям
video_buffer = asyncio.Queue(maxsize=10)
clients = set()  # Множество подключенных клиентов

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Добавление клиента в множество подключенных клиентов
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            # Получение кадра от клиента
            frame_bytes = await websocket.receive_bytes()

            # Добавление кадра в очередь
            await video_buffer.put(frame_bytes)

            # Рассылка кадра другим подключенным клиентам
            for client in clients:
                if client != websocket:
                    await client.send_text(frame_bytes)

    finally:
        # Удаление клиента из множества подключенных клиентов
        clients.remove(websocket)


@app.get("/")
async def get():
    return HTMLResponse("""
        <html>
        <head>
            <title>WebSocket Video Streaming</title>
        </head>
        <body>
            <h1>WebSocket Video Streaming Server</h1>
        </body>
        </html>
    """)
