import ee
import requests
import config
import os
from datetime import datetime, timedelta
from staticmap import StaticMap, CircleMarker
from PIL import Image

def init_gee():
    try: ee.Initialize(project=config.GEE_PROJECT)
    except: ee.Authenticate(); ee.Initialize(project=config.GEE_PROJECT)

def generate_base_map(filename="basemap.png"):
    if os.path.exists(filename): return filename
    try:
        m = StaticMap(1024, 1024, url_template='http://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
        bbox = config.ROI_SATELLITE
        m.add_marker(CircleMarker((bbox[0], bbox[1]), '#000000', 0))
        m.add_marker(CircleMarker((bbox[2], bbox[3]), '#000000', 0))
        image = m.render()
        image.save(filename)
        return filename
    except: return None

def get_combined_map():
    init_gee()
    roi = ee.Geometry.Rectangle(config.ROI_SATELLITE)
    today = datetime.now()
    d_start = (today - timedelta(days=5)).strftime('%Y-%m-%d')
    d_end = today.strftime('%Y-%m-%d')

    try:
        col = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2').filterBounds(roi).filterDate(d_start, d_end).select('NO2_column_number_density')
        if col.size().getInfo() == 0: return None
        
        vis = {'min': 0, 'max': 0.00015, 'palette': ['000000', '0000FF', '800080', '00FFFF', '00FF00', 'FFFF00', 'FF0000']}
        url = col.mean().visualize(**vis).getThumbURL({'dimensions': 1024, 'region': roi, 'format': 'png'})
        
        with open('gas.png', 'wb') as f: f.write(requests.get(url).content)
        map_file = generate_base_map()
        if not map_file: return None
        
        base = Image.open(map_file).convert("RGBA")
        overlay = Image.open('gas.png').convert("RGBA")
        
        if overlay.size != base.size:
            overlay = overlay.resize(base.size, Image.Resampling.LANCZOS)
        
        data = overlay.getdata()
        new_data = [(0,0,0,0) if item[:3] == (0,0,0) else (*item[:3], 160) for item in data]
        overlay.putdata(new_data)
        
        final = Image.alpha_composite(base, overlay).convert("RGB")
        final.save("final_gas_map.jpg")
        if os.path.exists('gas.png'): os.remove('gas.png')
        return "final_gas_map.jpg"
    except: return None

def get_weekly_satellite_report(): return None