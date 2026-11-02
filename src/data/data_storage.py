"""Persist computed spatial data and query summary using DuckDB."""
import duckdb
from src.data.osm_loader import BASE

def save_analysis(grid, key: str):
    folder=BASE/'data/processed'; folder.mkdir(exist_ok=True,parents=True)
    grid.to_parquet(folder/(key+'.parquet'))
    table=grid.drop(columns='geometry')
    with duckdb.connect(str(folder/'analysis.duckdb')) as con:
        con.register('current_grid',table)
        con.execute('CREATE OR REPLACE TABLE latest_analysis AS SELECT * FROM current_grid')
        return con.execute('SELECT count(*) AS grid_count, avg(facility_density) AS mean_facility_density FROM latest_analysis').fetchdf()
