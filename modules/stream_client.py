import zmq
import cv2
import numpy as np
import threading
import time

class ZMQStreamClient:
    def __init__(self, address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        
        # ВАЖНО: Мы убрали CONFLATE, чтобы избежать краша си-библиотеки.
        self.subscriber.connect(address)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        
        self.latest_frames = {}
        self.lock = threading.Lock()
        
        # Запускаем фоновый поток для очистки очереди
        self.thread = threading.Thread(target=self._update_frames, daemon=True)
        self.thread.start()
        print("[*] Background ZMQ Client started successfully.")

    def _update_frames(self):
        while True:
            try:
                # В быстром цикле вычитываем абсолютно все пришедшие кадры из буфера,
                # пока они не закончатся (до ошибки zmq.Again)
                while True:
                    try:
                        # Читаем БЕЗ блокировки (flags=zmq.NOBLOCK)
                        cam_id_bytes, frame_bytes = self.subscriber.recv_multipart(flags=zmq.NOBLOCK)
                        cam_id = cam_id_bytes.decode('utf-8')
                        
                        np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
                        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            with self.lock:
                                # Просто перезаписываем кадр — в словаре всегда будет только самый свежий!
                                self.latest_frames[cam_id] = frame
                    except zmq.Again:
                        # Кадры в буфере закончились, выходим из внутреннего цикла
                        break
                
                # Спим 10мс, чтобы не грузить процессор холостым циклом
                time.sleep(0.01)
                
            except Exception as e:
                print(f"[ZMQ ERROR] Error in frame receiver: {e}")
                time.sleep(1)

    def get_frame(self, cam_id):
        """Instantly returns the latest cached frame from memory"""
        with self.lock:
            frame = self.latest_frames.get(cam_id)
            return frame.copy() if frame is not None else None