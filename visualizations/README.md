# HRF Asylum DS Notebooks

## Description
This folder contains `.ipynb` notebooks and `.py` scripts exploring various visualizations.


## Notebooks

| Filename                       | Created | Description                                                                                                                                                                                                                                                     | Dependencies                                                        | Data File(s)                            |
|--------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|-----------------------------------------|
| CircuitLevelChoropleth.ipynb   | Labs 34 | Shows how to create customized GeoJSON file, grouping districts into circuits, and using Plotly to create a choropleth.                                                                                                                                         | `plotly` (4.14.3 or 4.5.0 works), `geopandas`, `geojson`, `shapely` | US_District_Court_Jurisdictions.geojson |
| CorrelationMatrixHeatmap.ipynb | Labs 34 | Explores the idea of a "correlation matrix heatmap" that is frequently used to show the strength of relationships between quantititave variables. A similar idea for categorical data would show the strength of the association between categorical variables. | `dython`, `scipy`                                                   | KL_Lambda_Report_2.csv                  |
| feature_heatmap.ipynb          |         |                                                                                                                                                                                                                                                                 |                                                                     |                                         |
| judge_heat_matrix.ipynb        |         |                                                                                                                                                                                                                                                                 |                                                                     |                                         |
| Labs32_visualization.ipynb     |         |                                                                                                                                                                                                                                                                 |                                                                     |                                         |
| map_vis_test.ipynb             |         |                                                                                                                                                                                                                                                                 |                                                                     |                                         |

## Scripts

| Filename              | Created | Description | Dependencies |
|-----------------------|---------|-------------|--------------|
| brainstorm_visuals.py |         |             |              |
| par_cat.py            |         |             |              |


## Data
- `test_data_v4.csv` contains ? ()
- `KL_Lambda_Report_2.csv` contains case data gathered in Labs 33 & 34
- `US_District_Court_Jurisdictions.geojson` contains boundaries for 94 district courts for making choropleths

## Contribute
Please contribute to this document so that future team members can quickly gain insight into what work has been done and which avenues have been explored already.
You can help by
- filling out information about a file after you review its contents,
- adding and filling out a new row in the appropriate table every time you add a new notebook or script.