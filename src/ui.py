"""Six-page interactive research dashboard."""
import json, logging
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
from src.data.osm_loader import load,BASE
from src.spatial.accessibility import analyze
from src.ml.clustering import cluster,FEATURES
from src.visualization.map_builder import make_map
from src.report.report_generator import report
logging.basicConfig(level=logging.INFO)
PAGES=['Overview Dashboard','Spatial Distribution','Accessibility Analysis','Regional Comparison','Machine Learning','Research Report']
@st.cache_resource(show_spinner=False)
def dataset(city,radius,mode): return load(city,radius,mode)
@st.cache_data(show_spinner=False)
def calculate(city,radius,mode,size,speed):
    g,p,r,m=dataset(city,radius,mode)
    result=analyze(g,p,r,size,speed)
    from src.data.data_storage import save_analysis
    save_analysis(result,f'{city}_{mode}_{radius}_{size}_{speed}')
    return result
def main():
    st.set_page_config(page_title='Hainan GeoInsight',page_icon='🌐',layout='wide')
    st.markdown('<style>.stApp{background:#f5f7fb}h1{color:#12304a}div[data-testid="stMetric"]{background:white;padding:16px;border-radius:12px;border:1px solid #e2e8f0}</style>',unsafe_allow_html=True)
    st.sidebar.title('🌐 GeoInsight'); st.sidebar.caption('HAINAN · SPATIAL RESEARCH')
    page=st.sidebar.radio('Workspace',PAGES)
    city=st.sidebar.selectbox('City',['Haikou','Sanya'])
    mode='REAL'
    radius=0
    st.sidebar.caption('Administrative boundary + mapped developed pedestrian area')
    size=st.sidebar.select_slider('Grid size (m)',[300,500,1000],value=500)
    speed=4.8
    st.sidebar.caption('Walking speed: 4.8 km/h (constant)')
    with st.sidebar.expander('Data Limitations'):
        st.markdown('- OSM data may have missing facilities.\n- The grid analysis uses uniform sampling points, not actual population weights.\n- Walking speed is set as a constant (4.8 km/h), ignoring terrain and age differences.\n- Study area includes only OSM-mapped developed land near walking roads; unmapped developed areas may be omitted.')
    cat=st.sidebar.selectbox('Facility category',['medical','education','transit','other'])
    threshold=st.sidebar.select_slider('Walking threshold (min)',[5,10,15],value=15)
    st.title('Hainan GeoInsight')
    st.caption('Real local OpenStreetMap PBF · urban core walking accessibility')
    st.subheader(page)
    try:
        with st.spinner('Loading and computing spatial indicators...'):
            g,poi,region,meta=dataset(city,radius,mode); grid=calculate(city,radius,mode,size,speed)
    except Exception as e: st.error(str(e)); st.stop()
    st.caption(f'{city} · mapped developed area {meta["study_area_km2"]:.2f} km² · EPSG:32649')
    st.caption('Excludes ocean and undeveloped areas; calculates pure pedestrian network coverage.')
    st.caption('Operational definition: only mapped developed polygons inside the city, excluding mapped water/forest/undeveloped classes. OSM completeness limits this exclusion; coverage is grid sampling, not population.')
    if page==PAGES[0]:
        cols=st.columns(4)
        for c,label,value in zip(cols,['Network nodes','Directed edges (buffer included)','Facilities (buffer included)','Walkable Grid Coverage'],[len(g),g.number_of_edges(),len(poi),f'{(grid[cat+"_min"]<=threshold).mean():.1%}']): c.metric(label,value)
        a,b=st.columns([2,1])
        with a: st_folium(make_map(g,poi,grid,cat+'_min'),height=520,use_container_width=True,returned_objects=[])
        with b: st.plotly_chart(px.bar(poi.groupby('category').size().rename('count').reset_index(),x='category',y='count'),use_container_width=True)
    elif page==PAGES[1]: st_folium(make_map(g,poi,grid),height=650,use_container_width=True,returned_objects=[])
    elif page==PAGES[2]:
        st.caption('Grey = unavailable; endpoint offsets included. Facility categories group hospitals/clinics/pharmacies and schools/universities.')
        cols=st.columns(3)
        for c,t in zip(cols,[5,10,15]): c.metric(f'{t} min grid coverage',f'{(grid[cat+"_min"]<=t).mean():.1%}')
        grid['covered']=((grid[cat+'_min']<=threshold)&grid[cat+'_min'].notna()).astype(int)
        show=st.radio('Map metric',['Minutes','Service coverage'],horizontal=True)
        st_folium(make_map(g,poi,grid,cat+'_min' if show=='Minutes' else 'covered'),height=570,use_container_width=True,returned_objects=[])
        st.dataframe(grid.drop(columns='geometry'),use_container_width=True)
    elif page==PAGES[3]:
        from src.metrics import comparison
        rows=[]
        for c in ['Haikou','Sanya']:
            cg,cp,cr,cm=dataset(c,radius,mode)
            rows.append(comparison(c,cg,calculate(c,radius,mode,size,speed)))
        table=pd.DataFrame(rows)
        st.caption('Medical facilities per grid is not per capita. Road length and components describe the complete within-city walking graph.')
        cols=st.columns(2)
        for i,metric in enumerate(table.columns[1:]):
            with cols[i%2]: st.plotly_chart(px.bar(table,x='city',y=metric,color='city',barmode='group'),use_container_width=True)
        st.dataframe(table,use_container_width=True)
        frames=[]
        for c in ['Haikou','Sanya']:
            try:
                f=calculate(c,radius,mode,size,speed).drop(columns='geometry'); f['city']=c; frames.append(f)
            except Exception: st.warning(f'{c}: matching real data scope not cached; download it first.')
        if frames:
            combined=pd.concat(frames); st.plotly_chart(px.box(combined,x='city',y=cat+'_min',color='city'),use_container_width=True)
            st.plotly_chart(px.histogram(combined,x='facility_density',color='city',barmode='overlay'),use_container_width=True)
            st.caption('Lowest accessibility: unavailable distances first, followed by largest finite travel times.')
            st.dataframe(combined.sort_values(cat+'_min',ascending=False,na_position='first').head(30),use_container_width=True)
    elif page==PAGES[4]:
        k=st.slider('Clusters',2,6,3)
        try:
            clustered,score=cluster(grid,k); st.metric('Silhouette score',f'{score:.3f}')
            st.caption('Median imputation + standardization; seed 42. Clusters describe feature similarity, not poverty or development level.')
            st_folium(make_map(g,poi,clustered,'cluster'),height=480,use_container_width=True,returned_objects=[])
            st.plotly_chart(px.scatter(clustered,x='PC1',y='PC2',color='cluster',hover_data=['grid_id']),use_container_width=True)
            st.dataframe(clustered.groupby('cluster')[FEATURES].mean(),use_container_width=True)
        except ValueError as e: st.warning(str(e))
    else:
        st.json(meta); st.markdown((BASE/'docs/methodology.md').read_text(encoding='utf-8'))
        st.download_button('Export PDF research report',report(grid,{**meta,'grid_size_m':size,'speed_kmh':speed}),file_name=f'{city}_{mode}_report.pdf',mime='application/pdf')
    st.divider(); a,b=st.columns(2)
    a.download_button('Export CSV',grid.drop(columns='geometry').to_csv(index=False).encode('utf-8-sig'),f'{city}_{mode}.csv','text/csv')
    b.download_button('Export GeoJSON',grid.to_crs(4326).to_json(),f'{city}_{mode}.geojson','application/geo+json')
    st.caption('Source: local OpenStreetMap PBF, contributors (ODbL). No population coverage claims.')
