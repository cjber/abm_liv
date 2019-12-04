import geopandas as gpd
import random
import pandas as pd
import crime

from typing import List


class Police:
    def __init__(self, bounds: gpd.GeoDataFrame):
        """Initial stat and variables for the police agents.

        Takes the bounds input which determines where agents may be created.
        Agents may be spawned within the extent of bounds, but to determine
        whether they fall within a bounds polygon this must be checked with a
        geographic function gpd.within().

        Args:
            bounds (gpd.GeoDataFrame): GeoDataFrame with the input polygon.
        """
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

    def distance_between(self, agent: crime.Crime) -> int:
        """Euclidean distance between two geographic points.

         The output represents the distance referring to the geographic 
         unit of the projection used.

        Args:
            agent (crime.Crime): A crime object with the attributes x and y. Must
            be the same projection as self.

        Returns:
            int: Returns a float value of distance using the projection values.
        """
        distance = ((self.x - agent.x)**2 +
                    (self.y - agent.y)**2)**0.5
        distance = float(distance)
        return(distance)

    def move(self, crime):
        """Move the police semi randomly, head in direction of crimes.

        Police agents will move in a random direction each iteration.
        For each solved crime, if the police moves to an area that is further
        away than its previous position to a crime it will not move.

        Args:
            crime (List[crime.Crime]): List of crime 'agents' with x and y
            coordinates
        """
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
                # print(cur_dist)
                if random.random() < 0.5:
                    self.x = (self.x + 1000)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.x = (self.x - 1000)
                else:
                    self.x = (self.x - 1000)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.x = (self.x + 1000)
                if random.random() < 0.5:
                    self.y = (self.y + 1000)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.y = (self.y - 1000)
                else:
                    self.y = (self.y - 1000)
                    dist = []
                    for c in crime_list:
                        dist.append(self.distance_between(c))
                    if min(dist) > cur_dist:
                        self.y = (self.y + 1000)

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
