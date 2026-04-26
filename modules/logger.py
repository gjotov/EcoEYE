import csv
import os
from datetime import datetime

def log_event(event_type, location, value):
    file = 'eco_stats.csv'
    exists = os.path.isfile(file)
    with open(file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not exists: writer.writerow(['time', 'type', 'location', 'value'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, location, value])