import cv2
import asyncio
import websockets
import base64
import numpy as np
from queue import Queue
import threading

SERVER_URI = "ws://localhost:8000/ws"


class VideoStreamer:
    def __init__(self, queue):
        self.queue = queue
        self.active = False

    def start(self):
        self.active = True
        cap = cv2.VideoCapture(0)
        while self.active:
            ret, frame = cap.read()
            if ret:
                self.queue.put(frame)

    def stop(self):
        self.active = False


async def send_video(websocket, queue):
    while True:
        frame = queue.get()
        _, encoded_frame = cv2.imencode('.jpg', frame)
        base64_frame = base64.b64encode(
            encoded_frame.tobytes()).decode('utf-8')
        await websocket.send(base64_frame)


async def receive_video(websocket):
    while True:
        base64_frame = await websocket.recv()
        decoded_frame = base64.b64decode(base64_frame)
        np_frame = np.frombuffer(decoded_frame, dtype=np.uint8)
        frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
        cv2.imshow('Received Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def start_video_stream(queue):
    video_streamer = VideoStreamer(queue)
    video_streamer.start()


def show_local_video(queue):
    while True:
        frame = queue.get()
        cv2.imshow('Local Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


async def main():
    queue = Queue()
    threading.Thread(target=start_video_stream, args=(queue,)).start()
    threading.Thread(target=show_local_video, args=(queue,)).start()

    async with websockets.connect(SERVER_URI) as websocket:
        send_task = asyncio.create_task(send_video(websocket, queue))
        receive_task = asyncio.create_task(receive_video(websocket))

        await asyncio.gather(send_task, receive_task)

if __name__ == "__main__":
    asyncio.run(main())
