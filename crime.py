import pandas as pd
import geopandas as gpd
import random

from typing import List


class Crime:
    def __init__(self, bounds: gpd.GeoDataFrame, crime_api: pd.DataFrame):
        """Initial x y values for crimes.

        Crime xy values are taken from the data.police.uk API and selected
        based on the extent of the bounds polygon. To determine whether points
        fall within the polygon bounds, the function gpd.within() is used.

        Args:
            bounds (gpd.GeoDataFrame): Input bounds polygon.
            crime_api (pd.DataFrame): xy coordinates for bounds extent from
            police api.
        """
        # takes bounds from main.py
        self.bounds = bounds

        # initial variables
        self.col = "Red"
        self.solved = 0

        # loop to take random crime point from api that falls within bounds
        # polygon
        while True:
            # int for random row
            i = random.randint(0, len(crime_api) - 1)
            x = crime_api['x'].loc[i]
            y = crime_api['y'].loc[i]

            # convert point to geodatafame
            df = pd.DataFrame({'x': [x], 'y': [y]})
            geom = gpd.points_from_xy(df.x, df.y)
            gdf = gpd.GeoDataFrame(df, geometry=geom)

            # find if point falls within polygon
            within = int(gdf.within(self.bounds))
            # while loop breaks only if point is within
            if within == 1:
                self.x = gdf['x']
                self.y = gdf['y']
                self.geom = gdf['geometry']
                break

    def distance_between(self, agent) -> int:
        """Euclidean distance between two geographic points.

        The output represents the distance referring to the geographic unit
        of the projection used.

        Args:
            agent (Police): A police object with coordinates xy.

        Returns:
            int: Distance with values associated with the projection.
        """
        distance = ((self.x - agent.x)**2 +
                    (self.y - agent.y)**2)**0.5
        return(distance)

    def solve(self, police_list):
        """Solve a crime by proximity to police.

        A crime is determined to be solved if within a specified distance from
        a police officer, and given a random 50% chance.

        Args:
            police_list ([TODO:type]): [TODO:description]
        """
        # solve a crime if police is within a certain distance
        for pol in police_list:
            distance = float(self.distance_between(pol))
            if distance < 500:
                self.col = "Green"
                self.solved = 1
