"""Metric grid sampling and directed multi-source shortest paths."""
import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
from shapely.geometry import box
from scipy.spatial import cKDTree

def analyze(g, poi, region, size: int=300, speed: float=4.8, max_snap: float=300):
    if size<=0 or speed<=0: raise ValueError('Grid size and walking speed must be positive')
    cells=[]; x0,y0,x1,y1=region.bounds
    for x in np.arange(x0,x1,size):
        for y in np.arange(y0,y1,size):
            geom=box(x,y,min(x+size,x1),min(y+size,y1)).intersection(region)
            if geom.area>0: cells.append(geom)
    grid=gpd.GeoDataFrame({'grid_id':range(len(cells))},geometry=cells,crs=g.graph['crs'])
    grid['area_km2']=grid.area/1e6
    ids=list(g.nodes); coords=np.array([(g.nodes[i]['x'],g.nodes[i]['y']) for i in ids]); tree=cKDTree(coords)
    centers=grid.geometry.representative_point()
    snap,idx=tree.query(np.array([(q.x,q.y) for q in centers]))
    for cat in ['medical','education','transit','other']:
        selected=poi[poi.category==cat]
        joined=gpd.sjoin(selected,grid[['grid_id','geometry']],predicate='intersects')
        joined=joined.reset_index().sort_values('grid_id').drop_duplicates('index')
        grid[cat+'_count']=grid.grid_id.map(joined.groupby('grid_id').size()).fillna(0).astype(int)
        h=g.reverse(copy=True); source='__facility_source__'; h.add_node(source)
        if len(selected):
            ds,ii=tree.query(np.array([(q.x,q.y) for q in selected.geometry]))
            for d,i in zip(ds,ii):
                if d<=max_snap: h.add_edge(source,ids[i],length=float(d))
        dist=nx.single_source_dijkstra_path_length(h,source,weight='length')
        values=np.array([dist.get(ids[i],np.inf)+d if d<=max_snap else np.inf for d,i in zip(snap,idx)])
        grid[cat+'_m']=np.where(np.isfinite(values),values,np.nan)
        grid[cat+'_min']=grid[cat+'_m']/(speed*1000/60)
        grid[cat+'_status']=np.where(snap>max_snap,'outside_snap_limit',np.where(np.isfinite(values),'reachable','no_connected_facility'))
    if g.number_of_edges()==0:
        grid['road_km_per_km2']=0.0
        grid['facility_density']=grid[[c+'_count' for c in ['medical','education','transit','other']]].sum(axis=1)/grid.area_km2
        return grid
    edges=ox.graph_to_gdfs(ox.convert.to_undirected(g),nodes=False).reset_index()
    lengths=[]
    for cell in cells:
        subset=edges.iloc[edges.sindex.query(cell,predicate='intersects')]
        lengths.append(subset.intersection(cell).length.sum()/1000)
    grid['road_km_per_km2']=np.array(lengths)/grid.area_km2
    grid['facility_density']=grid[[c+'_count' for c in ['medical','education','transit','other']]].sum(axis=1)/grid.area_km2
    return grid
