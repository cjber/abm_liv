import geopandas as gpd  # geographic data manipulation
import random  # pseudorandom numbers
import pandas as pd  # data manipulation

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
        # takes bounds from main.py
        self.bounds = bounds

        # find extent of bounds
        x_min, y_min, x_max, y_max = self.bounds.total_bounds

        while True:
            # random xy from extent of bounds (square)
            self.x = random.uniform(x_min, x_max)
            self.y = random.uniform(y_min, y_max)

            # convert to geodataframe
            df = pd.DataFrame({'x': [self.x], 'y': [self.y]})
            geom = gpd.points_from_xy(df.x, df.y)
            gdf = gpd.GeoDataFrame(df, geometry=geom)

            # check whether point falls within polygon
            within = int(gdf.within(self.bounds))

            # only keep point if within poly, otherwise repeat random coords
            if within == 1:
                self.x = gdf['x']
                self.y = gdf['y']
                self.geom = gdf['geometry']
                break

    def distance_between(self, agent) -> int:
        """Euclidean distance between two geographic points.

         The output represents the distance referring to the geographic
         unit of the projection used.

        Args:
            agent (Crime): A crime object with the attributes x and y.
            Must be the same projection as self.

        Returns:
            int: Returns a float value of distance using the projection values.
        """
        distance = ((self.x - agent.x)**2 +
                    (self.y - agent.y)**2)**0.5
        distance = float(distance)
        return distance

    def random_movement(self, cur_dist: float, crime_list: List[int]):
        """
        Create random movement parameters for each agent.

        :param cur_dist: Distance of a police agent from an active crime.
        :type cur_dist: float
        :param crime_list: List containing all active crime agents
        :type crime_list: List["Crime"]
        """
        dist = []
        if random.random() < 0.5:
            # add 1000 to police x value
            self.x = (self.x + 1000)
            for c in crime_list:
                # find new distance from police to all crimes
                dist.append(self.distance_between(c))
            # move in opposite direction if distance from nearest min(dist)
            # crime to police further than original police x position
            if min(dist) > cur_dist:
                self.x = (self.x - 2000)
        else:
            # repeat the above but take - 1000 x value
            self.x = (self.x - 1000)
            for c in crime_list:
                dist.append(self.distance_between(c))
            if min(dist) > cur_dist:
                self.x = (self.x + 2000)
        dist = []
        if random.random() < 0.5:
            # repeat with + 1000 to y value
            self.y = (self.y + 1000)
            for c in crime_list:
                dist.append(self.distance_between(c))
            if min(dist) > cur_dist:
                self.y = (self.y - 2000)
        else:
            # repeat with - 1000 to y value
            self.y = (self.y - 1000)
            for c in crime_list:
                dist.append(self.distance_between(c))
            if min(dist) > cur_dist:
                self.y = (self.y + 2000)

    def move(self, crime):
        """Move the police semi randomly, head in direction of crimes.

        Police agents will move in a random direction each iteration.
        For each solved crime, if the police moves to an area that is further
        away than its previous position to a crime it will not move.

        Args:
            crime (List[crime.Crime]): List of crime 'agents' with x and y
            coordinates
        """
        # keep only unsolved crimes
        crime_list = [c for c in crime if c.solved == 0]

        i = 0  # for numbering loops
        # while loop to attempt movement of police within bounds polygon
        while True:
            cur_dist = []
            if len(crime_list) > 1:
                for c in crime_list:
                    # find distance from police to crimes
                    cur_dist.append(self.distance_between(c))
                # find min distance
                cur_dist = min(cur_dist)
                # call the random movement function on police
                # which takes current min distance from a crime point to
                # determine whether or not to move the police in the random
                # direction
                self.random_movement(cur_dist, crime_list)
            # create xy dataframe
            df = pd.DataFrame({'x': [self.x], 'y': [self.y]})
            geom = gpd.points_from_xy(df.x, df.y)

            # convert df to gdf
            gdf = gpd.GeoDataFrame(df, geometry=geom)
            # find whether new xy points are within polygon bounds
            within = int(gdf.within(self.bounds))
            # only allow loop to break if new xy are within bounds
            # allow up to 10 times, if over 10 times the police officer is
            # lost outside the bounds
            i += 1
            if i > 10:
                print("Police officer has left the bounds.")
                break
            # if within gives true, allow new xy values to the police
            if within == 1:
                self.x = gdf['x']
                self.y = gdf['y']
                break
