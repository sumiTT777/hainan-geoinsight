"""Real-data reports with projected scale, grid north, explicit bins and hatches."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

def report(grid,meta):
 b=BytesIO(); styles=getSampleStyleSheet(); story=[]
 def para(s): story.extend([Paragraph(escape(str(s)),styles['BodyText']),Spacer(1,9)])
 story.append(Paragraph('Hainan GeoInsight | '+meta['city'],styles['Title']))
 para('REAL OpenStreetMap data | Walking speed 4.8 km/h | EPSG:32649')
 for key in ['source','downloaded_at','study_area_km2','scope']: para(f'{key}: {meta.get(key,"Unknown")}')
 para('Methods: administrative boundary intersected with mapped developed polygons and 300 m proximity to walking roads, minus mapped water, forest and undeveloped classes. Each clipped grid receives one interior representative sampling point. Directed multi-source Dijkstra includes straight endpoint offsets, maximum snapping distance 300 m. Coverage denominator: all included grid samples, not population.')
 rows=[['Facility','Grid samples','Reachable','Median min','15-min coverage']]
 for cat in ['medical','education','transit']:
  s=grid[cat+'_min'];rows.append([cat,str(len(s)),str(s.notna().sum()),f'{s.median():.2f}',f'{(s<=15).mean():.1%}'])
 story.append(Table(rows,hAlign='LEFT'));story.append(Spacer(1,12))
 para('Data Limitations: OSM data may have missing facilities. The grid analysis uses uniform sampling points, not actual population weights. Walking speed is set as a constant (4.8 km/h), ignoring terrain and age differences.')
 para(meta.get('limitations','OSM mapped-developed footprints are incomplete.'))
 para('Medical facilities per grid is an unweighted cell mean, never a per-capita measure. Grid north differs slightly from true north due to UTM convergence. Routes remain within city limits; barriers and facility entrances are not fully modeled.')
 story.append(PageBreak())
 fig,ax=plt.subplots(figsize=(8,7))
 vals=grid.medical_min
 masks=[vals.le(5),vals.gt(5)&vals.le(10),vals.gt(10)&vals.le(15),vals.gt(15),vals.isna()]
 colors=['#006837','#a6d96a','#ffffbf','#a50026','#9e9e9e'];labels=['0–5 min','5–10 min','10–15 min','>15 min','Unavailable'];hatches=['','..','//','xx','++']
 for mask,c,h in zip(masks,colors,hatches):
  if mask.any(): grid.loc[mask].plot(ax=ax,color=c,edgecolor='#555555',linewidth=0.12,hatch=h)
 ax.legend(handles=[Patch(facecolor=c,hatch=h,label=l) for c,h,l in zip(colors,hatches,labels)],loc='lower right',fontsize=8)
 ax.annotate('N\n(grid)',xy=(.08,.94),xytext=(.08,.80),xycoords='axes fraction',ha='center',arrowprops={'facecolor':'black','width':3,'headwidth':10})
 xmin,ymin,xmax,ymax=grid.total_bounds;span=xmax-xmin
 length=1000*max(1,round(span/6000));x=xmin+span*.06;y=ymin+(ymax-ymin)*.04
 ax.plot([x,x+length],[y,y],color='black',linewidth=4);ax.text(x+length/2,y+(ymax-ymin)*.015,f'{length/1000:g} km',ha='center',bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
 ax.set_title(meta['city']+' | Medical walking accessibility');ax.set_axis_off()
 img=BytesIO();fig.savefig(img,format='png',dpi=170,bbox_inches='tight');plt.close(fig);img.seek(0)
 from reportlab.lib.utils import ImageReader
 iw,ih=ImageReader(img).getSize(); factor=min(460/iw,500/ih)
 story.append(Image(img,width=iw*factor,height=ih*factor));para('Discrete thresholds and distinct hatches encode travel time independently of color. Grey cross-hatch indicates unavailable routes; it is not zero travel time.')
 SimpleDocTemplate(b).build(story);return b.getvalue()
