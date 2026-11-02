"""Cached real OSM acquisitions."""
from pathlib import Path
import json, logging
import yaml
from datetime import datetime, timezone
import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
from shapely.geometry import Point, LineString, box
BASE=Path(__file__).resolve().parents[2]
CRS='EPSG:32649'
CENTERS=yaml.safe_load((BASE/'config.yaml').read_text())['cities']
TAGS={'amenity':['hospital','clinic','pharmacy','school','university','bus_station','community_centre'], 'highway':'bus_stop','leisure':'park'}
def category(row):
    a=row.get('amenity')
    if a in ['hospital','clinic','pharmacy']: return 'medical'
    if a in ['school','university']: return 'education'
    if a=='bus_station' or row.get('highway')=='bus_stop': return 'transit'
    return 'other'
def boundary(city: str, radius: int):
    lat,lon=CENTERS[city]
    c=gpd.GeoSeries([Point(lon,lat)],crs=4326).to_crs(CRS).iloc[0]
    return box(c.x-radius,c.y-radius,c.x+radius,c.y+radius)
def clean(poi, region):
    if poi.empty: return gpd.GeoDataFrame(columns=['name','category','geometry'],geometry='geometry',crs=CRS)
    poi=poi.to_crs(CRS).copy()
    poi.geometry=poi.geometry.make_valid()
    poi=poi.loc[poi.geometry.notna() & ~poi.geometry.is_empty].copy()
    poi['category']=poi.apply(category,axis=1)
    if 'name' not in poi: poi['name']='Unnamed'
    poi['name']=poi['name'].fillna('Unnamed').astype(str)
    poi.geometry=poi.geometry.representative_point()
    poi=poi[poi.intersects(region)].copy()
    poi['key']=poi.geometry.to_wkb()
    return poi.drop_duplicates(['key','category'])[['name','category','geometry']].reset_index(drop=True)
def load(city: str, radius: int, mode: str='REAL', fetch: bool=False):
    if mode != 'REAL': raise ValueError('Only real OSM data are supported')
    folder=BASE/'data/raw'/f'{city}_final'
    if not (folder/'metadata.json').exists(): raise FileNotFoundError('Run build_final_data.py to prepare real administrative study data')
    return ox.load_graphml(folder/'network.graphml'),gpd.read_parquet(folder/'poi.parquet'),gpd.read_parquet(folder/'boundary.parquet').geometry.iloc[0],json.loads((folder/'metadata.json').read_text())
