import pandas as pd
import geopandas as gpd
import random


class Crime:
    def __init__(self, bounds, crime_api):
        self.bounds = bounds

        self.col = "Red"
        self.solved = 0

        while True:
            i = random.randint(0, len(crime_api))
            x = crime_api['longitude'].loc[i]
            y = crime_api['latitude'].loc[i]

            df = pd.DataFrame({'x': [x], 'y': [y]})
            geom = gpd.points_from_xy(df.x, df.y)

            gdf = gpd.GeoDataFrame(df, geometry=geom)
            within = int(gdf.within(self.bounds))
            if within is 1:
                self.x = gdf['x']
                self.y = gdf['y']
                self.geom = gdf['geometry']
                break

    def distance_between(self, agent) -> int:
        distance = ((self.x - agent.x)**2 +
                    (self.y - agent.y)**2)**0.5
        return(distance)

    def solve(self, police_list):
        for pol in police_list:
            distance = float(self.distance_between(pol))
            if random.random() < 0.5:
                if distance < 0.01:
                    self.col = "Green"
                    self.solved = 1
