import geopandas as gpd
import pandas as pd
import requests

import random
from pandas.io.json import json_normalize

bounds = gpd.read_file("./data/liv_shp/Liverpool_lsoa11.shp")
bounds['dissolve'] = 1
bounds = bounds.dissolve(by='dissolve')
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
coords = ':'.join(map(str, coords))


months = pd.date_range('2018-02-01', '2018-02-01',
                       freq='MS').strftime("%Y-%m").tolist()

# base police API url
url = "https://data.police.uk/api/crimes-street/all-crime"

response = requests.get(url +
                        "?poly=" +
                        coords +
                        "&date=" +
                        random.choice(months))

if response.status_code != 200:
    print("API lookup fail; using cached data.")
    data = pd.read_csv("./data/crime_cached.csv")
else:
    response = response.json()
    data = json_normalize(response)
    data = data[['category', 'location.latitude', 'location.longitude']]
    data = data.rename(columns={'location.latitude': 'latitude',
                                'location.longitude': 'longitude'})
    data = data.dropna()
    data['latitude'] = data['latitude'].astype(float)
    data['longitude'] = data['longitude'].astype(float)

    data.to_csv("./data/crime_cached.csv", index=False)
