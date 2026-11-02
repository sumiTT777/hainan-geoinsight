# Final study definition
The rectangular study extent is retired. Boundaries are OSM administrative relations obtained using OSMnx geocode_to_gdf (Haikou 2784613; Sanya 2128284).

Study mask = administrative boundary ∩ OSM-mapped developed land/building polygons ∩ 300 m pedestrian-road proximity, minus mapped water, forest, agricultural and natural undeveloped classes. Only this conservative footprint is sampled. This is not a complete land-cover inventory: missing developed-land tags and OSM errors affect inclusion. It is not valid to claim every real forest or ocean polygon has been independently verified.

Grid polygons are clipped to that mask. Each cell receives one interior representative point; partial cells are equally weighted, without population weighting. Network routes use actual walk-eligible OSM segments wholly inside the administrative boundary. Outside-city paths are excluded. Medical POIs are restricted to the study mask; this deliberately evaluates facilities within the included area.

Walkable Grid Coverage = fraction of included samples within the selected time threshold of a facility. It is a facility-accessibility metric, not population coverage or an inventory of all walkable land. Speed is fixed at 4.8 km/h. Unreachable or unsnappable samples remain missing and stay in the coverage denominator.

City comparison: undirected road kilometers (one count per physical keyed edge), mean medical facilities per grid (not per capita), 15-minute medical grid coverage, and connected components in the whole administrative-city walking graph. Component count is fragmentation, not a normalized connectivity score; comparing cities requires considering network size.

PDF maps use minute bins, distinct hatches, grid-north arrows and UTM-meter scale bars. Grid north differs slightly from geographic true north. Red-green hue alone is not claimed to be color-blind safe; labels/hatching provide redundant encoding.
