import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Polygon
# Set it None to display all rows in the dataframe
pd.set_option('display.max_rows', None)

# artefacts were further fixed with QGIS, removing inside nodes
bounds = gpd.read_file("./data/bounds.gpkg")

## CREATE GRID POLYGON
# find extents
xmin, ymin, xmax, ymax = bounds.total_bounds

# width and height of grids in crs units
length: int = 1000
wide: int = 1000

# create rounded int values across range of columns and rows
# within max and min extents
cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), wide))
rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), length))
rows.reverse() # reverse rows

# create list of square polgyons defined by extents and length/widths
polygons = []
for x in cols:
    polygons.extend(
        Polygon(
            [(x, y), (x + wide, y), (x + wide, y - length), (x, y - length)]
        )
        for y in rows
    )
##

# convert to gdf and save
grid = gpd.GeoDataFrame({'geometry': polygons})
grid.crs = bounds.crs
grid.to_file("./data/grid.shp")
