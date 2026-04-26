import requests
def get_weather_report():
    url = f"https://api.open-meteo.com/v1/forecast?latitude=48.80&longitude=44.75&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m&wind_speed_unit=ms&timezone=Europe%2FMoscow"
    try:
        data = requests.get(url, timeout=5).json()['current']
        wind_deg = data['wind_direction_10m']
        is_danger = 20 <= wind_deg <= 110
        risk = "🔴 ВЕТЕР С ЗАВОДОВ" if is_danger else "🟢 Ветер чистый"
        if data['wind_speed_10m'] < 1: risk = "🟠 Штиль"
        return (f"🌡 <b>ПОГОДА:</b> {data['temperature_2m']}°C, Вл. {data['relative_humidity_2m']}%\n"
                f"💨 <b>Ветер:</b> {data['wind_speed_10m']} м/с\n"
                f"🛡 {risk}"), data['relative_humidity_2m']
    except: return "⚠️ Нет данных", 0