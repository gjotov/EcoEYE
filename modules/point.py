import cv2
import numpy as np

# Ссылка на камеру с "грузовиком-ларьком"
STREAM_URL = "http://localhost:8080/frame?id=Aleksandrova_12070" 
# (Или прямая ссылка, если Go не запущен)

points = []

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"[{x}, {y}],")
        points.append([x, y])
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        if len(points) > 1:
            cv2.line(img, tuple(points[-2]), tuple(points[-1]), (0, 255, 0), 2)
        cv2.imshow('Setup ROI', img)

# Для теста качаем картинку через urllib (так как это http поток от Go)
import urllib.request
try:
    resp = urllib.request.urlopen(STREAM_URL)
    arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
except:
    # Если Go не работает, пробуем VideoCapture напрямую
    cap = cv2.VideoCapture("https://flussonic2.powernet.com.ru:444/user36662/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel")
    ret, img = cap.read()
    cap.release()

if img is not None:
    cv2.imshow('Setup ROI', img)
    cv2.setMouseCallback('Setup ROI', click_event)
    print("Кликай по границам ДОРОГИ. Нажми любую кнопку, чтобы выйти.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("\nКОПИРУЙ ЭТО В CONFIG.PY:")
    print(f"[[{p[0]}, {p[1]}] for p in {points}]")