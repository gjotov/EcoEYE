import ee
import requests
import config
import os
import threading
from datetime import datetime, timedelta
from staticmap import StaticMap, CircleMarker
from PIL import Image
from modules import notifier, reporter

_satellite_lock = threading.Lock()
_is_processing = False

def init_gee():
    try: 
        ee.Initialize(project=config.GEE_PROJECT)
    except Exception: 
        try:
            ee.Authenticate()
            ee.Initialize(project=config.GEE_PROJECT)
        except Exception as e:
            print(f"[Satellite GEE] Initialization error: {e}")

def _generate_base_map(filename="basemap.png"):
    if os.path.exists(filename): 
        return filename
    try:
        m = StaticMap(1024, 1024, url_template='http://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
        bbox = config.ROI_SATELLITE
        m.add_marker(CircleMarker((bbox[0], bbox[1]), '#000000', 0))
        m.add_marker(CircleMarker((bbox[2], bbox[3]), '#000000', 0))
        image = m.render()
        image.save(filename)
        return filename
    except Exception as e: 
        print(f"[Satellite] Error generating base map: {e}")
        return None

def _run_satellite_pipeline():
    global _is_processing
    
    init_gee()
    roi = ee.Geometry.Rectangle(config.ROI_SATELLITE)
    today = datetime.now()
    d_start = (today - timedelta(days=5)).strftime('%Y-%m-%d')
    d_end = today.strftime('%Y-%m-%d')

    try:
        col = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')\
                .filterBounds(roi)\
                .filterDate(d_start, d_end)\
                .select('NO2_column_number_density')
                
        if col.size().getInfo() == 0: 
            print("[Satellite] No available fresh satellite images.")
            _is_processing = False
            return
        
        vis = {'min': 0, 'max': 0.00015, 'palette': ['000000', '0000FF', '800080', '00FFFF', '00FF00', 'FFFF00', 'FF0000']}
        url = col.mean().visualize(**vis).getThumbURL({'dimensions': 1024, 'region': roi, 'format': 'png'})
        
        gas_temp_path = 'gas_temp.png'
        with open(gas_temp_path, 'wb') as f: 
            f.write(requests.get(url).content)
            
        map_file = _generate_base_map()
        if not map_file: 
            _is_processing = False
            return
        
        base = Image.open(map_file).convert("RGBA")
        overlay = Image.open(gas_temp_path).convert("RGBA")
        
        if overlay.size != base.size:
            overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)
        
        data = overlay.getdata()
        new_data = [(0,0,0,0) if item[:3] == (0,0,0) else (*item[:3], 160) for item in data]
        overlay.putdata(new_data)
        
        final = Image.alpha_composite(base, overlay).convert("RGB")
        final_path = "final_gas_map.jpg"
        final.save(final_path)
        
        if os.path.exists(gas_temp_path): 
            os.remove(gas_temp_path)
            
        msg = reporter.format_satellite_report(today.strftime("%d.%m.%Y"))
        print("[Satellite] Photo generated, sending to Telegram...")
        notifier.send_alert(final_path, msg)
        
    except Exception as e:
        print(f"[Satellite ERROR] Error generating satellite map: {e}")
    finally:
        with _satellite_lock:
            _is_processing = False

def trigger_satellite_analysis():
    global _is_processing
    with _satellite_lock:
        if _is_processing:
            print("[Satellite] Analysis already running in the background, skipping duplicate launch.")
            return False
        _is_processing = True
        
    print("[Satellite] Launching background thread for Google Earth Engine...")
    threading.Thread(target=_run_satellite_pipeline, daemon=True).start()
    return True