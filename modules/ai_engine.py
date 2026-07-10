import cv2
import numpy as np
import time
import traceback
from ultralytics import YOLO
import config
from modules import db

class TrafficAnalyzer:
    def __init__(self):
        print("[*] Initializing AI Engine...")
        try:
            self.model = YOLO(config.CAR_MODEL_PATH)
            print(f"[OK] Model {config.CAR_MODEL_PATH} loaded.")
        except Exception as e:
            print(f"[!!!] Error loading YOLO model: {e}")
            self.model = None
            
        # Dictionary for storing accumulating heatmaps for each camera
        self.heatmaps = {}
        # Masks for polygons (ROI)
        self.masks = {}

    def _init_camera_assets(self, cam_name, frame_shape):          
        h, w, _ = frame_shape
        if cam_name not in self.heatmaps:
            self.heatmaps[cam_name] = np.zeros((h, w), dtype=np.float32)
            
            # Prepare ROI mask
            mask = np.zeros((h, w), dtype=np.uint8)
            polygons = config.ROI_POLYGONS.get(cam_name)
            if polygons:
                for poly in polygons:
                    pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                    cv2.fillPoly(mask, [pts], 255)
            else:
                mask[:] = 255 # If no polygon - see the whole frame
            self.masks[cam_name] = mask

    def process_single_frame(self, cam_name, frame):
        if self.model is None or frame is None:
            return None, 0, 0, 0

        try:
            h, w, _ = frame.shape
            self._init_camera_assets(cam_name, frame.shape)
            
            mask = self.masks[cam_name]
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

            # Fast inference of YOLOv8 on a single frame
            # classes=[2, 5, 7] - cars, buses, trucks
            results = self.model.predict(masked_frame, conf=0.25, classes=[2, 5, 7], verbose=False)[0]
            
            cars = 0
            heavy = 0
            
            for box in results.boxes:
                cls = int(box.cls[0])
                xyxy = box.xyxy[0].cpu().numpy()
                cx = int((xyxy[0] + xyxy[2]) / 2)
                cy = int((xyxy[1] + xyxy[3]) / 2)

                # Check if the point is within the allowed zone
                if mask[min(cy, h-1), min(cx, w-1)] == 0:
                    continue

                label = self.model.names[cls]
                is_heavy = label in ['truck', 'bus']
                
                if is_heavy:
                    heavy += 1
                else:
                    cars += 1

                weight = 5 if is_heavy else 1
                cv2.circle(self.heatmaps[cam_name], (cx, cy), 30, weight, -1)

            co2 = (cars * 0.05 + heavy * 0.15) * 10
            toxic_idx = int(np.sum(self.heatmaps[cam_name]) / 1000)

            db.save_traffic_data(cam_name, cars, heavy, toxic_idx, co2)

            return frame, cars, heavy, toxic_idx

        except Exception as e:
            print(f"[ERR] process_single_frame on {cam_name}: {e}")
            traceback.print_exc()
            return frame, 0, 0, 0

    def get_rendered_heatmap(self, cam_name, current_frame):
        if cam_name not in self.heatmaps or current_frame is None:
            return current_frame

        heatmap = self.heatmaps[cam_name]
        heatmap_clipped = np.clip(heatmap, 0, 255).astype(np.uint8)
        
        final_frame = current_frame.copy()

        if np.max(heatmap_clipped) > 0:
            colored_map = cv2.applyColorMap(heatmap_clipped, cv2.COLORMAP_JET)
            mask = heatmap_clipped > 1
            final_frame[mask] = cv2.addWeighted(final_frame[mask], 0.6, colored_map[mask], 0.4, 0)

        polygons = config.ROI_POLYGONS.get(cam_name)
        if polygons:
            for poly in polygons:
                pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                cv2.polylines(final_frame, [pts], True, (0, 255, 0), 2)

        self.heatmaps[cam_name] = np.zeros_like(heatmap)

        return final_frame