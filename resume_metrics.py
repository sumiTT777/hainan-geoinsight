import json
import pandas as pd
import geopandas as gpd
import osmnx as ox
from src.data.osm_loader import load
from src.ml.clustering import cluster
results={}
for c in ['Haikou','Sanya']:
 g,p,r,m=load(c,0); df=pd.read_csv('exports/'+c+'_REAL.csv')
 d={'nodes':len(g),'directed_edges':g.number_of_edges(),'poi_total':len(p),'poi_categories':p.category.value_counts().to_dict(),'grids':len(df),'area_km2':r.area/1e6,'categories':{}}
 for cat in ['medical','education','transit','other']:
  s=df[cat+'_min'];d['categories'][cat]={'count_in_grids':int(df[cat+'_count'].sum()),'reachable':int(s.notna().sum()),'unavailable':int(s.isna().sum()),'mean_min':float(s.mean()),'median_min':float(s.median()),'coverage':{str(t):{'samples':int(s.le(t).sum()),'percent':float(s.le(t).mean()*100)} for t in [5,10,15]}}
 try:
  out,score=cluster(gpd.read_parquet('exports/'+c+'_REAL.parquet'),3);d['clustering']={'k':3,'silhouette':score,'sizes':out.cluster.value_counts().to_dict()}
 except Exception as e:d['clustering']={'error':str(e)}
 results[c]=d
print(json.dumps(results,ensure_ascii=False,indent=2))
open('exports/verified_resume_metrics.json','w',encoding='utf-8').write(json.dumps(results,ensure_ascii=False,indent=2))
