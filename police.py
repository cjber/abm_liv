import geopandas as gpd
import random
import pandas as pd


class Police:
    def __init__(self, bounds):
        self.bounds = bounds

        x_min, y_min, x_max, y_max = self.bounds.total_bounds

        while True:
            self.x = random.uniform(x_min, x_max)
            self.y = random.uniform(y_min, y_max)
            df = pd.DataFrame({'x': [self.x], 'y': [self.y]})
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
        distance = float(distance)
        return(distance)

    def move(self, crime):
        crime_list = []
        for c in crime:
            if c.solved == 0:
                crime_list.append(c)
        i = 0
        while True:
            cur_dist = []
            if len(crime_list) > 1:
                for c in crime_list:
                    cur_dist.append(self.distance_between(c))
                cur_dist = min(cur_dist)
                #print(cur_dist)
                if random.random() < 0.5:
                    self.x = (self.x + .005)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.x = (self.x - .005)
                else:
                    self.x = (self.x - .005)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.x = (self.x + .005)
                if random.random() < 0.5:
                    self.y = (self.y + .005)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.y = (self.y - .005)
                else:
                    self.y = (self.y - .005)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.y = (self.y + .005)

            df = pd.DataFrame({'x': [self.x], 'y': [self.y]})
            geom = gpd.points_from_xy(df.x, df.y)

            gdf = gpd.GeoDataFrame(df, geometry=geom)
            within = int(gdf.within(self.bounds))
            i += 1
            if i > 10:
                break
            if within is 1:
                #print(i, sep=' ', end='', flush=True)
                self.x = gdf['x']
                self.y = gdf['y']
                break
