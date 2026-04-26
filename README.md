# 🌍 EcoEYE: AI Environmental Monitoring System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-FF1493?style=for-the-badge&logo=ultralytics&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**EcoEYE** — это интеллектуальная система экологического мониторинга города, созданная на базе компьютерного зрения, анализа спутниковых данных и машинного обучения. Система автоматически отслеживает уровни загрязнения, анализирует транспортны�� поток и предупреждает о промышленных выбросах через Telegram.

> ⚠️ **Важный дисклеймер:**
> Это не официальный пост наблюдения и не сертифицированная лаборатория. Это пет-проект, написанный энтузиастами для образовательных и исследовательских целей.
> 
> *Источником видеопотока служат открытые городские камеры провайдера [Powernet](https://cam.powernet.com.ru).*

---

## ✨ Возможности системы

| Функция | Описание |
|---------|---------|
| **🚗 Анализ трафика и расчет CO₂** | Распознавание автомобилей (YOLOv8) на видеопотоке с городских камер в реальном времени, расчет выбросов CO₂ на основе типа и количества ТС |
| **🏭 Детекция промышленных выбросов** | Специально обученная нейросеть (100 эпох, mAP ~0.80) для анализа промзон. ИИ натренирован на обнаружение дыма и видимых загрязнений |
| **🛰️ Спутниковый анализ** | Интеграция данных со спутника **Sentinel-5P** для построения тепловых карт загрязнения диоксидом азота (NO₂) |
| **📱 Telegram-интеграция** | Автоматическая генерация отчетов с кадрами с камер, статистикой по машинам, уровнями загрязнения и графиками |
| **⚡ Высокопроизводительный стриминг** | Захват видеопотока осуществляется с помощью кастомного микросервиса на Go для параллельной обработки потоков |

---

## Демонстрация работы

### 1. Оценка выбросов CO₂ на основе городского трафика

<img width="513" height="412" alt="CO2 Analysis" src="https://github.com/user-attachments/assets/b733d617-e787-4158-bd6d-d398d9a0146a" />

### 2. Спутниковая карта загрязнений NO₂ (Sentinel-5P)

<img width="1024" height="1024" alt="Satellite Map" src="https://github.com/user-attachments/assets/97adf7ab-d24d-4b87-9291-ff61234248dd" />

### 3. Метрики обучения кастомной модели на дым/выбросы

<img width="2400" height="1200" alt="Training Results" src="https://github.com/user-attachments/assets/1888b19c-21ed-4dfa-953b-a5c75a3a9585" />

---

## Структура проекта

```
EcoEYE/
├── main.py                 # Главный модуль, оркестратор всей системы
├── vision.py               # Компьютерное зрение (инференс YOLO)
├── config.py               # Конфигурация (RTSP, Telegram, параметры)
├── requirements.txt        # Зависимости Python
├── streamer/               # Go-сервис для захвата IP-камер
│   ├── main.go
│   └── go.mod
├── modules/                # Вспомогательные скрипты
│   ├── co2_calculator.py
│   ├── satellite_api.py
│   └── utils.py
├── models/
│   ├── yolov8l.pt          # Базовая модель (трафик)
│   └── custom_smoke.pt     # Кастомные веса (дым/выбросы)
├── data/
│   └── basemap.png         # Карта-подложка для визуализации
├── start.bat               # Скрипт запуска на Windows
├── docker-compose.yml      # Конфигурация контейнеризации
└── README.md
```

---

## 🚀 Требования и установка

### Системные требования
- **Python** 3.8 или выше
- **Go** 1.16 или выше
- **Видеокарта** с поддержкой CUDA (рекомендуется для инференса YOLO в реальном времени)
- **ОС**: Linux, Windows, macOS
- **RAM**: Минимум 8 GB
- **Интернет**: Для загрузки моделей и данных со спутников

### Установка зависимостей

#### 1. Клонирование репозитория
```bash
git clone https://github.com/gjotov/EcoEYE.git
cd EcoEYE
```

#### 2. Установка Python зависимостей
```bash
pip install -r requirements.txt
```

#### 3. Загрузка моделей YOLO
```bash
# Базовая модель (автоматически загружается при первом запуске)
# Кастомные веса для дыма нужно поместить в папку models/
```

#### 4. Конфигурация
Отредактируйте `config.py`:
```python
# RTSP потоки с городских камер
RTSP_URLS = [
    "rtsp://camera1.example.com/stream",
    "rtsp://camera2.example.com/stream",
]

# Telegram бот
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# API ключи
SENTINEL_API_KEY = "YOUR_SENTINEL_KEY"
```

#### 5. Запуск Go микросервиса
```bash
cd streamer
go build -o streamer
./streamer
```

---

## Использование

### Запуск на Windows (всё в одном)
```bash
start.bat
```

### Запуск на Linux/macOS
```bash
python main.py
```

### Запуск с Docker
```bash
docker-compose up --build
```

### Примеры использования

```python
from vision import VisionModule
from modules.satellite_api import get_no2_data

# Инициализация модуля зрения
vision = VisionModule(model_path="models/yolov8l.pt")

# Обработка видеопотока
detections = vision.process_frame(frame)

# Получение спутниковых данных
pollution_map = get_no2_data(latitude=55.75, longitude=37.62, date="2026-04-26")
```

---

## API и интеграции

### Telegram бот команды
- `/start` — Начало работы
- `/status` — Статус системы
- `/report` — Получить отчёт за день
- `/maps` — Спутниковые карты загрязнения

### REST API (опционально)
```bash
GET /api/stats          # Получить текущую статистику
GET /api/detections     # Список последних детекций
POST /api/alert         # Создать оповещение
```

---

## Модели и обучение

### YOLOv8 для трафика
- **Модель**: YOLOv8 Large
- **Датасет**: COCO, настроенный на автомобили
- **Accuracy**: mAP 0.85+

### Кастомная модель для дыма/выбросов
- **Эпохи обучения**: 100
- **mAP**: ~0.80
- **Размер входа**: 640x640
- **Фреймворк**: PyTorch

Для переобучения моделей используйте:
```bash
python train_custom_model.py --epochs 100 --dataset ./data/smoke_dataset
```

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    EcoEYE System                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐      ┌──────────────┐     ┌─────────────┐ │
│  │ Go Streamer │──┬──→│ Vision.py    │────→│ Main.py     │ │
│  │ (RTSP)      │  │   │ (YOLOv8)     │     │ (Orchestr.) │ │
│  └─────────────┘  │   └──────────────┘     └─────────────┘ │
│                   │                              │           │
│                   │   ┌──────────────┐          │           │
│                   └──→│ Satellite API │          │           │
│                       │ (Sentinel-5P) │          │           │
│                       └──────────────┘          │           │
│                                                 │           │
│                                     ┌──────────▼───────────┐│
│                                     │  Telegram Bot        ││
│                                     │  (Alerts & Reports) ││
│                                     └──────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Производительность

| Метрика | Значение |
|---------|----------|
| Обработка видеопотока | 30 FPS (RTX 3090) |
| Задержка детекции | ~50 мс |
| Потребление RAM | ~2-3 GB |
| GPU Memory | ~4 GB |
| Время генерации отчёта | ~5 сек |

---

## 🤝 Вклад

Приветствуются pull requests! Для больших изменений сначала откройте issue для обсуждения.

```bash
# Процесс вклада
1. Fork репозитория
2. Создайте ветку (git checkout -b feature/AmazingFeature)
3. Commit изменения (git commit -m 'Add AmazingFeature')
4. Push в ветку (git push origin feature/AmazingFeature)
5. Откройте Pull Request
```

---

## Лицензия

Проект распространяется под лицензией **MIT**. Подробнее см. в файле [LICENSE](LICENSE).

---

## 🙏 Благодарности

- [Ultralytics](https://github.com/ultralytics/ultralytics) за YOLOv8
- [Copernicus](https://scihub.copernicus.eu/) за данные Sentinel-5P
- [Telegram](https://telegram.org/) за API бота
- [Powernet](https://cam.powernet.com.ru) за открытые RTSP потоки

---

## Контакты и поддержка

- **Issues**: [GitHub Issues](https://github.com/gjotov/EcoEYE/issues)
- **Обсуждения**: [GitHub Discussions](https://github.com/gjotov/EcoEYE/discussions)

---

## ⚡ Roadmap

- [ ] Интеграция с OpenWeather для корректировки расчётов
- [ ] Веб-интерфейс на React/Vue
- [ ] Интеграция с системами ПДД для анализа загруженности дорог
- [ ] Machine Learning для предсказания пиков загрязнения
- [ ] Мобильное приложение
- [ ] Поддержка нескольких городов

---

**Сделано с ❤️ для окружающей среды**
