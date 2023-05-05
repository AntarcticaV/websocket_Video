import asyncio
import numpy as np
import cv2
import websockets
import base64
import pygame

test = 1

pygame.init()

screen = pygame.display.set_mode((500, 400))


def c2ImageToSurface(cvImage):
    if cvImage.dtype.name == 'uint16':
        cvImage = (cvImage / 256).astype('uint8')
    size = cvImage.shape[1::-1]
    if len(cvImage.shape) == 2:
        cvImage = np.repeat(cvImage.reshape(size[1], size[0], 1), 3, axis=2)
        format = 'RGB'
    else:
        format = 'RGBA' if cvImage.shape[2] == 4 else 'RGB'
        cvImage[:, :, [0, 2]] = cvImage[:, :, [2, 0]]
    surface = pygame.image.frombuffer(cvImage.flatten(), size, format)
    return surface.convert_alpha() if format == 'RGBA' else surface.convert()


async def send_video(websocket):
    # открытие видеофайла для чтения кадров
    global test
    cap = cv2.VideoCapture(0)
    # чтение и отправка каждого кадра видео по WebSocket
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # кодирование кадра видео в JPEG и отправка по WebSocket
        # frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
        if test == 0:
            break
        await websocket.send(frame.tobytes())
    # закрытие видеофайла и WebSocket-соединения
    cap.release()


async def receive_video(websocket):
    # подключение к серверу WebSocket
    global test
    # ожидание и прием кадров видео от сервера WebSocket
    while True:
        # чтение кадра видео из WebSocket
        frame_bytes = await websocket.recv()

        frame = np.frombuffer(frame_bytes, dtype='uint8')

        frame = np.reshape(frame, (480, 640, 3))

        surf = pygame.surfarray.make_surface(frame)

        screen.fill('black')
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        # отображение кадра видео в окне
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        if websocket.closed:
            break
    # закрытие окна и WebSocket-соединения
    print("out")
    test = 0


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
