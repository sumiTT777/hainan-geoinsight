"""Create administrative-clipped, mapped-developed pedestrian study masks."""
import json
from datetime import datetime,timezone
import osmium, geopandas as gpd, osmnx as ox
from shapely import wkb
from shapely.ops import unary_union
from src.data.osm_loader import BASE,CRS
from src.data.pbf_loader import load_pbf
factory=osmium.geom.WKBFactory(); developed=[]; excluded=[]
class Areas(osmium.SimpleHandler):
 def area(self,a):
  t=dict(a.tags)
  built=t.get('landuse') in ['residential','commercial','retail','industrial','institutional','education','civic','recreation_ground'] or t.get('building') not in [None,'no'] or t.get('amenity') in ['school','university','hospital','clinic']
  banned=t.get('natural') in ['water','wood','wetland','scrub','heath','grassland','beach','bare_rock','sand'] or t.get('landuse') in ['forest','farmland','orchard','plant_nursery','meadow','reservoir','basin'] or t.get('water') is not None
  if not (built or banned): return
  try: geom=wkb.loads(factory.create_multipolygon(a),hex=True)
  except Exception: return
  (excluded if banned else developed).append(geom)
Areas().apply_file(str(BASE/'data/raw/hainan-latest.osm.pbf'),locations=True,idx='flex_mem')
print('Mapped developed polygons',len(developed),'excluded polygons',len(excluded),flush=True)
built=gpd.GeoSeries(developed,crs=4326).to_crs(CRS).make_valid().union_all()
ban=gpd.GeoSeries(excluded,crs=4326).to_crs(CRS).make_valid().union_all()
for city in ['Haikou','Sanya']:
 admin=gpd.read_file(BASE/'data/raw'/f'{city}_admin.geojson').to_crs(CRS).geometry.make_valid().union_all()
 g,poi,_=load_pbf(str(BASE/'data/raw/hainan-latest.osm.pbf'),city,0,region_override=admin)
 edges=ox.graph_to_gdfs(ox.convert.to_undirected(g),nodes=False)
 # Conservative inclusion: only mapped developed polygons near actual walking roads.
 region=built.intersection(admin).difference(ban).intersection(edges.geometry.buffer(300).union_all()).buffer(0)
 if region.is_empty: raise ValueError('No valid mapped developed pedestrian area: '+city)
 poi=poi[poi.intersects(region)].copy()
 folder=BASE/'data/raw'/f'{city}_final';folder.mkdir(exist_ok=True)
 ox.save_graphml(g,folder/'network.graphml');poi.to_parquet(folder/'poi.parquet')
 gpd.GeoDataFrame({'city':[city]},geometry=[region],crs=CRS).to_parquet(folder/'boundary.parquet')
 gpd.GeoDataFrame({'city':[city]},geometry=[region],crs=CRS).to_crs(4326).to_file(folder/'study_boundary.geojson',driver='GeoJSON')
 meta={'mode':'REAL','city':city,'source':'User local hainan-latest.osm.pbf; administrative boundaries from OSM Nominatim','downloaded_at':datetime.now(timezone.utc).isoformat(),'crs':CRS,'study_area_km2':region.area/1e6,'scope':'OSM administrative polygon intersect mapped developed land/buildings and 300m walking-road proximity; subtract mapped water/forest/agriculture/natural undeveloped classes','limitations':'Conservative mapped-developed footprint, not complete city land cover. Unmapped developed areas omitted; OSM classification errors possible. Network is full administrative-city walking graph; no outside-city paths. Relation POIs omitted.'}
 (folder/'metadata.json').write_text(json.dumps(meta,indent=2));print(city,len(g),len(poi),region.area/1e6,flush=True)
