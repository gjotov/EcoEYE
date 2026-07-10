import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eco_eye.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for traffic statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            camera_id TEXT NOT NULL,
            cars_count INTEGER DEFAULT 0,
            heavy_count INTEGER DEFAULT 0,
            toxic_index INTEGER DEFAULT 0,
            co2_emission REAL DEFAULT 0.0
        )
    ''')
    
    # Weather statistics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity INTEGER,
            wind_speed REAL,
            wind_risk TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[OK] Database initialized successfully.")

def save_traffic_data(camera_id, cars, heavy, toxic, co2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO traffic_stats (camera_id, cars_count, heavy_count, toxic_index, co2_emission)
        VALUES (?, ?, ?, ?, ?)
    ''', (camera_id, cars, heavy, toxic, co2))
    conn.commit()
    conn.close()

def save_weather_data(temp, humidity, wind_speed, wind_risk):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather_stats (temperature, humidity, wind_speed, wind_risk)
        VALUES (?, ?, ?, ?)
    ''', (temp, humidity, wind_speed, wind_risk))
    conn.commit()
    conn.close()

def get_latest_stats(camera_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM traffic_stats 
        WHERE camera_id = ? 
        ORDER BY timestamp DESC LIMIT 1
    ''', (camera_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None