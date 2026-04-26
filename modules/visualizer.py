import cv2
import numpy as np
from datetime import datetime

def draw_gradient_legend(image):
    h, w, _ = image.shape
    box_w, box_h = 140, 230
    x1, y1 = w - box_w - 20, 70
    
    overlay = image.copy()
    cv2.rectangle(overlay, (x1, y1), (x1 + box_w, y1 + box_h), (0, 0, 0), -1)
    image = cv2.addWeighted(overlay, 0.7, image, 0.3, 0)
    cv2.rectangle(image, (x1, y1), (x1 + box_w, y1 + box_h), (100, 100, 100), 1)

    colors = np.array([[0,0,255],[0,255,255],[0,255,0],[255,255,0],[128,0,128],[255,0,0],[10,10,10]], dtype=np.uint8)
    gradient = cv2.resize(colors.reshape(7, 1, 3), (25, 190), interpolation=cv2.INTER_LINEAR)
    image[y1+25:y1+25+190, x1+15:x1+15+25] = gradient
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, "NO2 LEVEL", (x1+10, y1+20), font, 0.4, (255,255,255), 1, cv2.LINE_AA)
    for y, t, c in [(y1+35,"DANGER",(0,0,255)),(y1+120,"MODERATE",(0,255,255)),(y1+205,"CLEAN",(255,100,0))]:
        cv2.putText(image, t, (x1+45, y), font, 0.4, c, 1, cv2.LINE_AA)
    return image

def add_overlay(image, cam_name, title, level="INFO"):
    h, w, _ = image.shape
    cols = {"INFO": (0,255,0), "WARN": (0,165,255), "CRITICAL": (0,0,255)}
    color = cols.get(level, (255,255,255))

    ov = image.copy()
    cv2.rectangle(ov, (0, h-50), (w, h), (0,0,0), -1)
    cv2.rectangle(ov, (0, 0), (w, 5), color, -1)
    image = cv2.addWeighted(ov, 0.8, image, 0.2, 0)

    font = cv2.FONT_HERSHEY_SIMPLEX
    dt = datetime.now().strftime("%H:%M | %d.%m")
    cv2.putText(image, cam_name.upper(), (15, h-15), font, 0.6, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(image, title, (15, h-35), font, 0.5, color, 1, cv2.LINE_AA)
    
    if "SATELLITE" in title.upper(): image = draw_gradient_legend(image)
    return image