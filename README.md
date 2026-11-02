# Hainan GeoInsight

A Python GIS dashboard for exploring pedestrian accessibility to public services in **Haikou and Sanya, Hainan** using real OpenStreetMap data.

## Project highlights

- **183,426 network nodes** and **391,452 directed edges** across the two administrative-city walking networks.
- **4,784 clipped analysis grids**, covering **241.79 km²** of mapped developed study land.
- Nearest-facility routing, **5 / 10 / 15-minute** grid coverage, KMeans clustering and PCA.
- Six interactive Streamlit workspaces with CSV, GeoJSON and PDF exports.

These are outputs from one local OSM snapshot, not independently validated inventories. Network statistics and study-land statistics use different extents. Coverage is **grid sampling coverage, not population coverage**.

## Results and documentation

- [Methods and limitations](docs/methodology.md)
- [Data dictionary](docs/data_dictionary.md)
- [Verified metrics](docs/results/verified_resume_metrics.json)
- [City comparison](docs/results/city_comparison.csv)
- [Haikou report](docs/results/Haikou_REAL_report.pdf)
- [Sanya report](docs/results/Sanya_REAL_report.pdf)

## Setup and reproduce

Python **3.12** is recommended. Install dependencies before building data:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-lock.txt
New-Item -ItemType Directory -Force data/raw, data/processed, data/cache
```

Obtain a Hainan OSM PBF extract from [Geofabrik](https://download.geofabrik.de/asia/china.html) or another OSM distribution source. Place it at `data/raw/hainan-latest.osm.pbf`. Original data and generated graph caches are deliberately excluded from Git. The filename does not guarantee freshness; preserve your source date and hash.

```powershell
.\.venv\Scripts\python fetch_boundaries.py
.\.venv\Scripts\python build_final_data.py
.\.venv\Scripts\python export_final.py
.\.venv\Scripts\python -m streamlit run app.py
```

After data preparation, double-click `run.bat` or use `run.ps1`. The app opens on localhost:8501. Without prepared real data it shows a clear error; there is no synthetic fallback. Boundary acquisition requires network access. Fresh OSM snapshots will produce different results.

## Methods

The study mask intersects actual city administrative polygons, OSM-mapped developed land/buildings and 300 m walking-road proximity, then subtracts mapped water, forest and undeveloped classes. It is a conservative footprint, not a complete land-cover inventory.

Distances use EPSG:32649, a bidirectional walk-filtered graph and reverse multi-source Dijkstra, including straight endpoint connectors capped at 300 m. Walking speed is fixed at 4.8 km/h. Unavailable routes remain missing. KMeans uses eight standardized features, median imputation, seed 42 and 20 initializations.

## Structure

`src/data`: PBF loading and persistence; `src/spatial`: grid and accessibility; `src/ml`: clustering; `src/visualization`: maps; `src/report`: PDF export; `src/ui.py`: six workspaces; `tests`: real-data smoke test.

```powershell
# Run after preparing real data
.\.venv\Scripts\python -m pytest tests -q
.\.venv\Scripts\python check_final_pages.py
```

## Limitations and attribution

OSM may omit facilities or land-use labels. Relation-based POIs, complete pedestrian restrictions, entrances, terrain, opening hours and capacity are not fully modeled. Equal-weight grid samples are not population weights. Medical facilities per grid is not a per-capita measure. Cluster labels do not represent poverty or development ranks. Validation is limited and does not establish policy impact.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under ODbL. Included derived reports and aggregate results retain this attribution. No separate open-source license is granted for the project code at this time.
