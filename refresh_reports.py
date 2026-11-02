import geopandas as gpd,json,pymupdf
from src.data.osm_loader import BASE
from src.report.report_generator import report
for c in ['Haikou','Sanya']:
 grid=gpd.read_parquet(BASE/'exports'/f'{c}_REAL.parquet');m=json.loads((BASE/'data/raw'/f'{c}_final/metadata.json').read_text());p=BASE/'exports'/f'{c}_REAL_report.pdf';p.write_bytes(report(grid,m));doc=pymupdf.open(p)
 for i,page in enumerate(doc): page.get_pixmap().save(str(BASE/'exports'/f'{c}_report_page{i+1}.png'))
 print(c,'PDF verified',len(doc),flush=True)
