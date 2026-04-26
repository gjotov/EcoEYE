import cv2
import numpy as np
import config
import time
import traceback
from ultralytics import YOLO

print("[*] Init AI Engine (NATIVE YOLO MODE)...")
try:
    detection_model = YOLO(config.CAR_MODEL_PATH) 
    print(f"[OK] Модель {config.CAR_MODEL_PATH} загружена.")
except Exception as e:
    print(f"[!!!] Критическая ошибка модели: {e}")
    detection_model = None

def generate_toxic_heatmap(cam_url, cam_name):
    if detection_model is None: return None, 0, 0, 0

    try:
        cap = cv2.VideoCapture(cam_url)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
        ret, first_frame = cap.read()
        
        if not ret: return None, 0, 0, 0
        
        h, w, _ = first_frame.shape
        heatmap = np.zeros((h, w), dtype=np.float32)
        
        # --- ПОДГОТОВКА МАСКИ (ТРАФАРЕТА) ---
        mask_poly = np.zeros((h, w), dtype=np.uint8)
        
        # Проверяем, есть ли полигон для этой камеры
        polygons = config.ROI_POLYGONS.get(cam_name)
        
        if polygons:
            # Если полигоны есть - рисуем их белым на черном фоне
            for poly in polygons:
                pts = np.array(poly, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(mask_poly, [pts], 255)
        else:
            # Если полигонов нет - заливаем всё белым (видим весь кадр)
            mask_poly[:] = 255

        start = time.time()
        max_cars = 0
        max_heavy = 0
        
        final_frame = first_frame.copy()

        while (time.time() - start) < config.HEATMAP_DURATION:
            ret, frame = cap.read()
            if not ret: break
            
            final_frame = frame.copy()
            
            # 1. НАКЛАДЫВАЕМ МАСКУ НА ПОЛНЫЙ КАДР
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask_poly)

            # !!! ДЕБАГ: СОХРАНЯЕМ ТО, ЧТО ВИДИТ РОБОТ !!!
            # Открой этот файл и посмотри. Если он черный - проблема в координатах.
            if "Ленина" in cam_name: # Сохраняем только проблемную камеру
                cv2.imwrite(f"DEBUG_WHAT_AI_SEES_{cam_name[:5]}.jpg", masked_frame)

            # 2. ОТПРАВЛЯЕМ В SAHI
            # Важно: отправляем masked_frame, а не roi
            try:
                result = get_sliced_prediction(
                    masked_frame,
                    detection_model,
                    slice_height=416,
                    slice_width=416,
                    overlap_height_ratio=0.2,
                    overlap_width_ratio=0.2,
                    verbose=False
                )
                
                c, tr = 0, 0
                for pred in result.object_prediction_list:
                    # Порог чуть ниже для надежности
                    if pred.score.value < 0.25: continue
                    
                    label = pred.category.name.lower()
                    if label in ['car', 'truck', 'bus', 'van']:
                        box = pred.bbox.to_voc_bbox()
                        cx = int((box[0] + box[2]) / 2)
                        cy = int((box[1] + box[3]) / 2)
                        
                        # Проверяем, не попали ли мы в черную зону маски
                        # (SAHI может найти "машину" в шуме черного фона, отсекаем)
                        if mask_poly[min(cy, h-1), min(cx, w-1)] == 0:
                            continue

                        weight = 5 if label in ['truck', 'bus'] else 1
                        try: cv2.circle(heatmap, (cx, cy), 30, (weight * 5), -1)
                        except: pass
                        
                        if label == 'car': c += 1
                        else: tr += 1
                
                max_cars = max(max_cars, c)
                max_heavy = max(max_heavy, tr)
            except: pass

        cap.release()
        
        # Рендер
        heatmap = np.clip(heatmap, 0, 255).astype(np.uint8)
        if np.max(heatmap) > 0:
            colored_map = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            mask = heatmap > 1
            final_frame[mask] = cv2.addWeighted(final_frame[mask], 0.6, colored_map[mask], 0.4, 0)
        
        # Рисуем зеленые границы полигона для наглядности
        if polygons:
            for poly in polygons:
                pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                cv2.polylines(final_frame, [pts], True, (0, 255, 0), 2)
        
        toxic_idx = int(np.sum(heatmap) / 1000)
        return final_frame, max_cars, max_heavy, toxic_idx

    except Exception as e:
        print(f"[ERROR] {cam_name}: {e}")
        traceback.print_exc()
        return None, 0, 0, 0