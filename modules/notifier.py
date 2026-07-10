import queue
import threading
import requests
import os
import config

_alert_queue = queue.Queue()

def _tg_worker():
    while True:
        item = _alert_queue.get()
        if item is None:
            break
        
        img_path, text = item
        url = f"https://api.telegram.org/bot{config.TOKEN}/sendPhoto"
        
        try:
            if img_path and os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    response = requests.post(
                        url, 
                        data={'chat_id': config.CHANNEL_ID, 'caption': text, 'parse_mode': 'HTML'}, 
                        files={'photo': f},
                        timeout=15
                    )
                os.remove(img_path)
            else:
                msg_url = f"https://api.telegram.org/bot{config.TOKEN}/sendMessage"
                response = requests.post(
                    msg_url, 
                    data={'chat_id': config.CHANNEL_ID, 'text': text, 'parse_mode': 'HTML'},
                    timeout=10
                )
            
            if response.status_code != 200:
                print(f"[Notifier] Error to send message: {response.text}")
                
        except Exception as e:
            print(f"[Notifier] Error while sending alert: {e}")
        finally:
            _alert_queue.task_done()

threading.Thread(target=_tg_worker, daemon=True).start()

def send_alert(img_path, text):
    temp_path = None
    if img_path and os.path.exists(img_path):
        import shutil
        temp_path = f"sending_{os.path.basename(img_path)}"
        shutil.copy(img_path, temp_path)
        
    _alert_queue.put((temp_path, text))