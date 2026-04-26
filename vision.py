import cv2
import numpy as np
import urllib.request
from ultralytics import YOLO
import config

cam_name = list(config.CITY_CAMS.keys())[0]
url = list(config.CITY_CAMS.values())[0]

print(f"[*] ТЕСТ ЗРЕНИЯ: {cam_name}")
print(f"[*] Источник: {url}")

try:
    model = YOLO("yolov8l.pt")
except Exception as e:
    print(f"Ошибка модели: {e}")
    exit()
try:
    # Если ссылка ведет на localhost (Go), качаем как файл
    if "localhost" in url:
        resp = urllib.request.urlopen(url, timeout=5)
        arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(arr, -1)
    else:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        cap.release()
        if not ret: frame = None

    if frame is None:
        print("Кадр не получен (пустой).")
        exit()
        
    print(f"Кадр есть! Размер: {frame.shape}")
    
    cv2.imwrite("DEBUG_SOURCE.jpg", frame)

except Exception as e:
    print(f"Ошибка скачивания: {e}")
    exit()

results = model.predict(frame, conf=0.10, classes=[2, 5, 7], verbose=True)[0]

print(f"\n>>> НАЙДЕНО ОБЪЕКТОВ: {len(results.boxes)} <<<")

res_plotted = results.plot()
cv2.imwrite("DEBUG_RESULT.jpg", res_plotted)