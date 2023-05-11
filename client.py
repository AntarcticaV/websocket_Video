import asyncio
import numpy as np
import cv2
import websockets
import base64
import pygame

test = 1
type_Video = None

# pygame.init()

# screen = pygame.display.set_mode((500, 400))


async def send_video(websocket):
    # открытие видеофайла для чтения кадров
    global test
    global type_Video
    cap = cv2.VideoCapture(0)
    # чтение и отправка каждого кадра видео по WebSocket
    while True:
        ret, frame = cap.read()
        # cv2.imshow("Video", frame)
        # print(frame.dtype)
        if not ret:
            break
        # кодирование кадра видео в JPEG и отправка по WebSocket
        frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
        if test == 0:
            break
        await websocket.send(frame_bytes)
    # закрытие видеофайла и WebSocket-соединения
    # cv2.destroyAllWindows()
    cap.release()


async def receive_video(websocket):
    # подключение к серверу WebSocket
    global test
    global type_Video
    # ожидание и прием кадров видео от сервера WebSocket
    while True:
        # чтение кадра видео из WebSocket
        frame_bytes = await websocket.recv()
        frame_arr = np.frombuffer(frame_bytes, dtype='uint8')
        frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)
        # frame.reshape(480, 640, 3)

        # frame = np.frombuffer(frame_bytes, dtype='uint8')

        # frame = np.reshape(frame, (480, 640, 3))

        # surf = pygame.surfarray.make_surface(frame)

        # screen.fill('black')
        # screen.blit(surf, (0, 0))
        # pygame.display.flip()
        # отображение кадра видео в окне
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) == ord('q'):
            break
        if websocket.closed:
            break
    # закрытие окна и WebSocket-соединения
    print("out")
    test = 0
    cv2.destroyAllWindows()


async def main():
    # подключение к серверу WebSocket
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        # создание двух тасков для отправки и приема видео
        send_task = asyncio.create_task(send_video(websocket))
        receive_task = asyncio.create_task(receive_video(websocket))
        # ожидание завершения тасков
        await asyncio.gather(send_task, receive_task)
        await websocket.close()

# запуск главного асинхронного цикла
asyncio.run(main())
