from modules import db

def get_historical_comparison(camera_id, current_cars):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(cars_count) as avg_cars FROM traffic_stats 
            WHERE camera_id = ? AND timestamp >= datetime('now', '-2 hours')
        ''', (camera_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row['avg_cars'] is not None:
            avg_cars = row['avg_cars']
            if avg_cars == 0: 
                return ""
            
            # Считаем разницу в процентах
            diff_percent = int(((current_cars - avg_cars) / avg_cars) * 100)
            
            if diff_percent > 15:
                return f" (📈 на {diff_percent}% выше нормы)"
            elif diff_percent < -15:
                return f" (📉 на {abs(diff_percent)}% ниже нормы)"
                
    except Exception as e:
        print(f"[Reporter Stats Error] {e}")
        
    return " (в пределах нормы)"

def get_health_advice(toxic_idx):
    if toxic_idx < 1000:
        return "✅ <b>Зеленая зона.</b> Воздух в норме. Можно проветривать и гулять."
    elif toxic_idx < 3000:
        return "⚠️ <b>Внимание.</b> У дороги дышать тяжело. Закройте окна, если живете на перекрестке."
    elif toxic_idx < 5000:
        return "🟠 <b>Вредно.</b> Высокая концентрация выхлопов. Не рекомендуются прогулки вдоль трасс."
    else:
        return "⛔️ <b>ОПАСНО.</b> Эффект «газовой камеры». Максимально ограничьте пребывание на улице."

def format_traffic_report(cam_name, cars, heavy, toxic_idx, co2, weather_text):
    status = "🟡 Плотное движение"
    level = "INFO"
    
    if toxic_idx > 2000: 
        status = "🟠 ЗАТОР"
        level = "WARN"
    if toxic_idx > 4000: 
        status = "🔴 ТРАНСПОРТНЫЙ КОЛЛАПС"
        level = "CRITICAL"

    comparison = get_historical_comparison(cam_name, cars)
    advice = get_health_advice(toxic_idx)

    display_name = cam_name.replace("_", " ")

    return (
        f"{status}\n"
        f"➖➖➖➖➖➖➖➖\n"
        f"📍 <b>{display_name.upper()}</b>\n"
        f"🚙 Легковых: <b>{cars}</b>{comparison}\n"
        f"🚛 Грузовых: <b>{heavy}</b>\n"
        f"☁️ Выброс CO2: <b>~{co2:.2f} кг</b> (за 10 мин)\n"
        f"🌡 Индекс токсичности: {toxic_idx}\n"
        f"➖➖➖➖➖➖➖➖\n"
        f"{weather_text}\n"
        f"👨‍⚕️ <b>Совет:</b> {advice}\n"
        f"#EcoEye #Трафик"
    ), level

def format_satellite_report(d_now):
    return (
        f"🛰 <b>ИЗОБРАЖЕНИЕ С ОРБИТЫ</b>\n"
        f"📅 Дата: {d_now}\n"
        f"Спутник: Sentinel-5P\n"
        f"➖➖➖➖➖➖➖➖\n"
        f"Карта загрязнения <b>NO2 (Диоксид азота)</b>.\n"
        f"Анализ атмосферы над городом и поймой.\n"
        f"➖➖➖➖➖➖➖➖\n"
    )