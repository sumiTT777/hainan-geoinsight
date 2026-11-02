import osmnx as ox
from pathlib import Path
ox.settings.requests_timeout=30
for city in ['Haikou','Sanya']:
 try:
  g=ox.geocode_to_gdf(city+', Hainan, China'); g.to_file('data/raw/'+city+'_admin.geojson',driver='GeoJSON'); print(city,g[['display_name','osm_id']].to_string(),flush=True)
 except Exception as e: print(city,repr(e),flush=True)
