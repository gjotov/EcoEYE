import requests
import threading
import time

_cached_report = "🌡 <b>ПОГОДА:</b> Данные обновляются..."
_cached_humidity = 0
_lock = threading.Lock()

def _weather_updater():
    global _cached_report, _cached_humidity
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.80&longitude=44.75&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m&wind_speed_unit=ms&timezone=Europe%2FMoscow"
    
    while True:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()['current']
                wind_deg = data['wind_direction_10m']
                
                is_danger = 20 <= wind_deg <= 110
                risk = "🔴 ВЕТЕР С ЗАВОДОВ" if is_danger else "🟢 Ветер чистый"
                if data['wind_speed_10m'] < 1: 
                    risk = "🟠 Штиль"
                
                report = (
                    f"🌡 <b>ПОГОДА:</b> {data['temperature_2m']}°C, Вл. {data['relative_humidity_2m']}%\n"
                    f"💨 <b>Ветер:</b> {data['wind_speed_10m']} м/с\n"
                    f"🛡 {risk}"
                )
                
                # Безопасно обновляем кэш
                with _lock:
                    _cached_report = report
                    _cached_humidity = data['relative_humidity_2m']
                    
            else:
                print(f"[Weather] Can't get weather data, status code: {response.status_code}")
        except Exception as e:
            print(f"[Weather] Error to get weather data: {e}")
            
        time.sleep(1800)

threading.Thread(target=_weather_updater, daemon=True).start()

def get_weather_report():
    with _lock:
        return _cached_report, _cached_humidity