from pathlib import Path
import json,pandas as pd,numpy as np, pymupdf
from src.data.osm_loader import load,BASE
from src.spatial.accessibility import analyze
from src.metrics import comparison
from src.report.report_generator import report
out=BASE/'exports';out.mkdir(exist_ok=True);rows=[]
for city in ['Haikou','Sanya']:
 g,p,r,m=load(city,0);grid=analyze(g,p,r,500,4.8)
 assert grid.geometry.difference(r).area.sum()<0.01
 assert grid.geometry.representative_point().within(r).all()
 grid.to_parquet(out/f'{city}_REAL.parquet');grid.drop(columns='geometry').to_csv(out/f'{city}_REAL.csv',index=False,encoding='utf-8-sig')
 pdf=out/f'{city}_REAL_report.pdf';pdf.write_bytes(report(grid,m));rows.append(comparison(city,g,grid))
 doc=pymupdf.open(pdf)
 for i,page in enumerate(doc): page.get_pixmap().save(str(out/f'{city}_report_page{i+1}.png'))
 print(city,'nodes',len(g),'grids',len(grid),'area',r.area/1e6,flush=True)
pd.DataFrame(rows).to_csv(out/'city_comparison.csv',index=False,encoding='utf-8-sig');print(rows,flush=True)
