import requests
import config

def send_alert(img_path, text):
    url = f"https://api.telegram.org/bot{config.TOKEN}/sendPhoto"
    try:
        if img_path:
            with open(img_path, 'rb') as f:
                requests.post(url, data={'chat_id': config.CHANNEL_ID, 'caption': text, 'parse_mode': 'HTML'}, files={'photo': f})
        else:
            requests.post(f"https://api.telegram.org/bot{config.TOKEN}/sendMessage", data={'chat_id': config.CHANNEL_ID, 'text': text, 'parse_mode': 'HTML'})
    except Exception as e:
        print(f"Ошибка TG: {e}")