import cv2
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def draw_text_cyrillic(image, text, position, font_size, color_bgr):

    cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)
    draw = ImageDraw.Draw(pil_im)
    
    font_names = ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    font = None
    for name in font_names:
        try:
            font = ImageFont.truetype(name, font_size)
            break
        except IOError:
            continue
            
    if font is None:
        font = ImageFont.load_default()

    color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])
    
    draw.text(position, text, font=font, fill=color_rgb)
    
    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def draw_gradient_legend(image):
    h, w, _ = image.shape
    box_w, box_h = 160, 240
    x1, y1 = w - box_w - 20, 70
    
    overlay = image.copy()
    cv2.rectangle(overlay, (x1, y1), (x1 + box_w, y1 + box_h), (0, 0, 0), -1)
    image = cv2.addWeighted(overlay, 0.7, image, 0.3, 0)
    cv2.rectangle(image, (x1, y1), (x1 + box_w, y1 + box_h), (100, 100, 100), 1)

    colors = np.array([[0,0,255],[0,255,255],[0,255,0],[255,255,0],[128,0,128],[255,0,0],[10,10,10]], dtype=np.uint8)
    gradient = cv2.resize(colors.reshape(7, 1, 3), (25, 180), interpolation=cv2.INTER_LINEAR)
    image[y1+35:y1+35+180, x1+15:x1+15+25] = gradient
    
    image = draw_text_cyrillic(image, "УРОВЕНЬ NO2", (x1+15, y1+10), 14, (255, 255, 255))
    
    legend_labels = [
        (y1+40, "ОПАСНО", (0, 0, 255)),
        (y1+115, "УМЕРЕННО", (0, 255, 255)),
        (y1+195, "ЧИСТО", (255, 100, 0))
    ]
    
    for y, text, color in legend_labels:
        image = draw_text_cyrillic(image, text, (x1 + 50, y), 12, color)
        
    return image

def add_overlay(image, cam_name, title, level="INFO"):
    h, w, _ = image.shape
    cols = {"INFO": (0,255,0), "WARN": (0,165,255), "CRITICAL": (0,0,255)}
    color = cols.get(level, (255,255,255))

    ov = image.copy()
    cv2.rectangle(ov, (0, h-60), (w, h), (0,0,0), -1)
    cv2.rectangle(ov, (0, 0), (w, 6), color, -1)
    image = cv2.addWeighted(ov, 0.8, image, 0.2, 0)

    display_cam_name = cam_name.replace("_", " ").upper()
    dt = datetime.now().strftime("%H:%M | %d.%m.%Y")
    
    image = draw_text_cyrillic(image, display_cam_name, (15, h-28), 16, (255, 255, 255))
    image = draw_text_cyrillic(image, title, (15, h-50), 13, color)
    image = draw_text_cyrillic(image, dt, (w - 150, h-28), 14, (180, 180, 180))
    
    if "SATELLITE" in title.upper() or "СПУТНИК" in title.upper(): 
        image = draw_gradient_legend(image)
        
    return image