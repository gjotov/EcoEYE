import time
import cv2
import os
import traceback
from datetime import datetime
from modules import ai_engine, logger, notifier, satellite, weather, visualizer, reporter
import config

def run_loop():
    print(f"[{datetime.now()}] 🚨 РЕЖИМ ОТЛАДКИ: Шлю всё подряд без фильтров!")
    print("Для остановки нажми Ctrl+C")
    
    # Сбрасываем таймеры
    last_alerts = {} 

    while True:
        try:
            # --- ТРАФИК ---
            for name, url in config.CITY_CAMS.items():
                print(f"\n[*] Обработка камеры: {name}...")
                
                # 1. ОТКЛЮЧАЕМ КУЛДАУН (комментируем проверку)
                # if time.time() - last_alerts.get(name, 0) < 3600: continue
                
                try:
                    # Генерируем карту
                    img, cars, heavy, toxic = ai_engine.generate_toxic_heatmap(url, name)
                    
                    # Пишем в консоль, что видит ИИ
                    total = cars + heavy
                    print(f"   >>> ИИ видит: {total} авто (Toxic: {toxic})")
                    
                    if img is None:
                        print("   [!] Ошибка: Пустой кадр от камеры")
                        continue

                    # 2. ОТКЛЮЧАЕМ ПОРОГИ (Шлем всегда, если кадр есть)
                    # Было: if toxic > config.TOXIC_THRESHOLD ...
                    # Стало:
                    if True: 
                        weather_full, _ = weather.get_weather_report()
                        co2 = (cars * 0.05 + heavy * 0.15) * 10
                        
                        # Формируем сообщение (даже если машин 0)
                        msg, level = reporter.format_traffic_report(name, cars, heavy, toxic, co2, weather_full)
                        
                        # Добавляем пометку DEBUG на фото
                        final_img = visualizer.add_overlay(img, name, "DEBUG FORCE SEND", "WARN")
                        
                        fname = f"debug_{datetime.now().strftime('%H%M%S')}.jpg"
                        cv2.imwrite(fname, final_img)
                        
                        print(f"   [+] Отправляю фото в Telegram...")
                        notifier.send_alert(fname, msg)
                        
                        if os.path.exists(fname): os.remove(fname)
                        
                        # Маленькая пауза, чтобы телеграм не забанил за спам (2 секунды)
                        time.sleep(2)
                        
                except Exception as e: 
                    print(f"   [ERR] Ошибка внутри цикла камеры: {e}")
                    traceback.print_exc()

            print("--- Круг пройден. Жду 10 секунд и по новой ---")
            time.sleep(10) # Быстрый перезапуск

        except KeyboardInterrupt:
            print("Стоп.")
            break
        except Exception as e:
            print(f"[CRITICAL] {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_loop()