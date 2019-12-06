import geopandas as gpd
import pandas as pd
import requests
import random
from pandas.io.json import json_normalize

# read in bounds poly
bounds = gpd.read_file("./data/bounds.gpkg")
# if required dissolve into a single polygon
bounds['dissolve'] = 1
bounds = bounds.dissolve(by='dissolve')
# use mercator projection
bounds = bounds.to_crs({'init': 'epsg:4326'})

# create vector of liv bbox
bounds = bounds.total_bounds

index = [1, 0, 3, 2]
bounds = [bounds[i] for i in index]

index = [0, 3, 2, 1]
bounds = bounds + [bounds[i] for i in index]


coords = [','.join(map(str, bounds[0:2])), ','.join(map(str, bounds[2:4])),
          ','.join(map(str, bounds[4:6])), ','.join(map(str, bounds[6:8]))]

index = [3, 1, 2, 0]
coords = [coords[i] for i in index]
coords_str = ':'.join(map(str, coords))


months = pd.date_range('2018-02-01', '2018-02-01',
                       freq='MS').strftime("%Y-%m").tolist()

print('Retrieving Crime coordinates from data.police.uk API...')
# base police API url
url = "https://data.police.uk/api/crimes-street/all-crime"

response = requests.get(url +
                        "?poly=" +
                        coords_str +
                        "&date=" +
                        random.choice(months))

print('Request sent.')
if response.status_code != 200:
    print("API lookup fail; using cached data.")
    df = pd.read_csv("./data/crime_cached.csv")
else:
    print("API lookup successful!")
    response = response.json()
    data = json_normalize(response)
    data = data[['category', 'location.latitude', 'location.longitude']]
    data = data.rename(columns={'location.latitude': 'latitude',
                                'location.longitude': 'longitude'})
    data = data.dropna()
    data['latitude'] = data['latitude'].astype(float)
    data['longitude'] = data['longitude'].astype(float)
    x = data['longitude']
    y = data['latitude']

    df = pd.DataFrame({'x': x, 'y': y})
    geom = gpd.points_from_xy(df.x, df.y)
    gdf = gpd.GeoDataFrame(df, geometry=geom)
    gdf.crs = {'init': 'epsg:4326'}
    gdf = gdf.to_crs({'init': 'epsg:27700'})


    df = pd.DataFrame({'x': gdf.geometry.x, 'y': gdf.geometry.y})
    df.to_csv("./data/crime_cached.csv", index=False)
