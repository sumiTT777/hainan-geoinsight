"""Folium layer composition."""
import folium
import geopandas as gpd
import osmnx as ox
COLORS={'medical':'#f97373','education':'#38bdf8','transit':'#fbbf24','other':'#4ade80'}
def make_map(g,poi,grid=None,column=None):
    center=poi.to_crs(4326).geometry.union_all().centroid if len(poi) else gpd.GeoSeries([grid.geometry.union_all().centroid],crs=grid.crs).to_crs(4326).iloc[0]
    m=folium.Map([center.y,center.x],zoom_start=13,tiles='OpenStreetMap')
    edges=ox.graph_to_gdfs(g,nodes=False).to_crs(4326)
    folium.GeoJson(gpd.GeoSeries([edges.geometry.union_all()],crs=4326).to_json(),name='Walking roads',style_function=lambda f:{'color':'#64748b','weight':2,'opacity':0.6}).add_to(m)
    if grid is not None and column:
        data=grid[['grid_id',column,'geometry']].to_crs(4326)
        if column=='cluster':
            palette=['#38bdf8','#f97373','#4ade80','#c084fc','#fbbf24','#fb7185']
            style=lambda f:{'fillColor':palette[int(f['properties']['cluster'])%len(palette)],'fillOpacity':0.55,'weight':0.4}
        elif column.endswith('_min'):
            def shade(v):
                if v is None: return '#9e9e9e'
                return '#006837' if v<=5 else '#a6d96a' if v<=10 else '#ffffbf' if v<=15 else '#a50026'
            style=lambda f:{'fillColor':shade(f['properties'][column]),'fillOpacity':0.75,'color':'#444444','weight':0.3}
            legend='<div style="position:fixed;bottom:25px;left:10px;background:white;padding:8px;z-index:9999;font-size:12px">Minutes: <b style="color:#006837">0–5</b> | <b style="background:#a6d96a">5–10</b> | <b style="background:#ffffbf">10–15</b> | <b style="color:#a50026">&gt;15</b> | Grey: unavailable</div>'
            m.get_root().html.add_child(folium.Element(legend))
        else:
            import branca.colormap as cm
            values=data[column].dropna(); scale=cm.linear.YlOrRd_09.scale(0,max(float(values.max()) if len(values) else 1,1)); scale.caption=column; scale.add_to(m)
            style=lambda f:{'fillColor':scale(f['properties'][column]) if f['properties'][column] is not None else '#777777','fillOpacity':0.55,'weight':0.4}
        folium.GeoJson(data.to_json(),name=column,style_function=style,tooltip=folium.GeoJsonTooltip(fields=['grid_id',column])).add_to(m)
    import html
    for cat,color in COLORS.items():
        layer=folium.FeatureGroup(name=cat)
        for _,r in poi[poi.category==cat].to_crs(4326).iterrows(): folium.CircleMarker([r.geometry.y,r.geometry.x],radius=4,color=color,fill=True,fill_opacity=0.9,tooltip=html.escape(r['name'])).add_to(layer)
        layer.add_to(m)
    if grid is not None:
        west,south,east,north=grid.to_crs(4326).total_bounds
        m.fit_bounds([[south,west],[north,east]])
    folium.LayerControl().add_to(m)
    return m

