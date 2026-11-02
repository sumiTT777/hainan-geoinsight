"""Import a locally downloaded Geofabrik PBF with walking exclusions."""
import osmium
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
from pyproj import Transformer
from src.data.osm_loader import CRS, boundary, clean

def load_pbf(path: str, city: str, radius: int, region_override=None):
    region=region_override if region_override is not None else boundary(city,radius); extent=region
    transformer=Transformer.from_crs(4326,CRS,always_xy=True)
    graph=nx.MultiDiGraph(crs=CRS); rows=[]
    class Handler(osmium.SimpleHandler):
        def node(self,n):
            tags=dict(n.tags)
            if tags.get('amenity') in ['hospital','clinic','pharmacy','school','university','bus_station','community_centre'] or tags.get('highway')=='bus_stop' or tags.get('leisure')=='park':
                x,y=transformer.transform(n.location.lon,n.location.lat)
                if extent.covers(Point(x,y)): rows.append({**tags,'geometry':Point(x,y)})
        def way(self,w):
            tags=dict(w.tags)
            try: coords=[transformer.transform(n.lon,n.lat) for n in w.nodes]
            except osmium.InvalidLocationError: return
            if len(coords)<2: return
            line=LineString(coords)
            if not line.intersects(extent): return
            if tags.get('amenity') in ['hospital','clinic','pharmacy','school','university','bus_station','community_centre'] or tags.get('leisure')=='park': rows.append({**tags,'geometry':line.centroid})
            highway=tags.get('highway')
            if not highway or highway in ['motorway','motorway_link','construction','proposed'] or tags.get('foot')=='no' or (tags.get('access') in ['private','no'] and tags.get('foot') not in ['yes','designated']): return
            for a,b,ca,cb in zip(list(w.nodes),list(w.nodes)[1:],coords,coords[1:]):
                if not extent.covers(LineString([ca,cb])): continue
                graph.add_node(a.ref,x=ca[0],y=ca[1]); graph.add_node(b.ref,x=cb[0],y=cb[1])
                segment=LineString([ca,cb]); length=segment.length
                for u,v in [(a.ref,b.ref),(b.ref,a.ref)]: graph.add_edge(u,v,length=length,geometry=segment,osmid=w.id)
    Handler().apply_file(path,locations=True,idx='flex_mem')
    if not len(graph): raise ValueError('No walking roads found in configured study scope')
    raw=gpd.GeoDataFrame(rows,geometry='geometry',crs=CRS) if rows else gpd.GeoDataFrame(geometry=[],crs=CRS)
    return graph,clean(raw,extent),region
