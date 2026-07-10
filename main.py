import time
import cv2
import os
import traceback
from datetime import datetime

import config
from modules import db, ai_engine, stream_client, weather, notifier, visualizer, reporter

def run_loop():
    print(f"[{datetime.now()}] 🚀 Запуск EcoEYE v2.0...")
    
    # 1. Инициализируем базу данных
    db.init_db()
    
    # 2. Инициализируем ZMQ-клиент и ИИ-движок
    client = stream_client.ZMQStreamClient("tcp://127.0.0.1:5555")
    analyzer = ai_engine.TrafficAnalyzer()
    
    # Даем ZMQ-клиенту 2 секунды, чтобы накопить первые кадры
    print("[*] Прогрев видеопотоков...")
    time.sleep(2)
    
    # Словари для контроля времени
    last_processed_time = {} # Для ограничения FPS обработки
    last_alert_time = {}     # Для контроля частоты отправки репортов

    # Интервал отправки отчетов (в секундах). 
    # Для тестов поставим 60 секунд. В продакшене можно поставить 3600 (1 час)
    REPORT_INTERVAL = 60 

    print("[OK] EcoEYE успешно запущен и анализирует улицы!")
    print("Для остановки нажмите Ctrl+C\n")

    while True:
        try:
            for name in config.CITY_CAMS.keys():
                now = time.time()

                if now - last_processed_time.get(name, 0) < 0.2:
                    continue
                frame = client.get_frame(name)
                if frame is None:
                    continue
                
                _, cars, heavy, toxic = analyzer.process_single_frame(name, frame)
                last_processed_time[name] = now

                if now - last_alert_time.get(name, 0) >= REPORT_INTERVAL:
                    print(f"\n[📊] Время репорта для камеры: {name}")
                    
                    rendered_frame = analyzer.get_rendered_heatmap(name, frame)
                    
                    if rendered_frame is None:
                        print(f"[-] No rendered frame for {name}")
                        continue
                    
                    weather_text, _ = weather.get_weather_report()
                    
                    co2 = (cars * 0.05 + heavy * 0.15) * 10
                    
                    msg, level = reporter.format_traffic_report(name, cars, heavy, toxic, co2, weather_text)
                    
                    final_img = visualizer.add_overlay(rendered_frame, name, "АНАЛИЗ ЭКОЛОГИИ И ТРАФИКА", level)
                    
                    temp_filename = f"report_{name}_{int(now)}.jpg"
                    cv2.imwrite(temp_filename, final_img)
                    
                    print(f"[+] Отправка отчета в Telegram...")
                    notifier.send_alert(temp_filename, msg)
                    
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                        
                    last_alert_time[name] = now
                    
            time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n[!] EcoEYE stopped by user.")
            break
        except Exception as e:
            print(f"\n[critical error]: {e}")
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    run_loop()