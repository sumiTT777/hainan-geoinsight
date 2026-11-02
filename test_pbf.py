"""Standalone osmium reader: print every walking-road node in a stated core bbox.
No app imports, no fabricated nodes. Run: python test_pbf.py > docs/pbf_nodes.csv
The bbox is a core extent, not an administrative boundary.
"""
from pathlib import Path
import osmium
PBF=Path(__file__).parent/'data/raw/hainan-latest.osm.pbf'
BBOX=(110.05,19.90,110.50,20.15)
nodes={}
class Reader(osmium.SimpleHandler):
 def way(self,w):
  tags=dict(w.tags)
  if not tags.get('highway') or tags.get('highway') in ['motorway','motorway_link','construction','proposed'] or tags.get('foot')=='no' or (tags.get('access') in ['private','no'] and tags.get('foot') not in ['yes','designated','permissive']): return
  for n in w.nodes:
   if not n.location.valid(): continue
   lon,lat=n.lon,n.lat
   if BBOX[0]<=lon<=BBOX[2] and BBOX[1]<=lat<=BBOX[3]: nodes[n.ref]=(lon,lat)
Reader().apply_file(str(PBF),locations=True,idx='flex_mem')
print('osm_node_id,longitude,latitude')
for key,(lon,lat) in sorted(nodes.items()): print(f'{key},{lon},{lat}')
import sys
print(f'PBF={PBF}; bbox={BBOX}; unique walking-road nodes={len(nodes)}',file=sys.stderr)
