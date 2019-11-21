import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Polygon
# Set it None to display all rows in the dataframe
pd.set_option('display.max_rows', None)

# liverpool shp
bounds = gpd.read_file("./data/liv_shp/Liverpool_lsoa11.shp")
bounds['dissolve'] = 1
bounds = bounds.dissolve(by='dissolve')

bounds.to_file("./data/liverpool_bounds.shp")


# artefacts were further fixed with QGIS, removing inside nodes
bounds = gpd.read_file("./data/liverpool_bounds_fixed.gpkg")
# create grid polygon
xmin, ymin, xmax, ymax = bounds.total_bounds
length = 1000
wide = 1000

cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), wide))
rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), length))

rows.reverse()

polygons = []
for x in cols:
    for y in rows:
        polygons.append(
            Polygon([(x, y), (x+wide, y), (x+wide, y-length), (x, y-length)]))

grid = gpd.GeoDataFrame({'geometry': polygons})
grid.crs = bounds.crs
grid.to_file("./data/liv_grid.shp")
