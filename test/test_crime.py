from abm_liv.crime import Crime
import unittest
import geopandas as gpd
import pandas as pd
import sys


bounds = gpd.read_file("../data/bounds.gpkg")
crime_api = pd.read_csv("../data/crime_cached.csv")


class TestCrime(unittest.TestCase):

    def setup(self):
        self.crime = Crime(bounds, crime_api)

    def test_init(self):
        self.assertEqual(self.crime.bounds, bounds)
        self.assertEqual(self.crime.crime_api, crime_api)

        self.assertEqual(self.crime.x, [row for row in crime_api.iterrows()
                                        if row.x == self.crime.x])
        self.assertEqual(self.crime.y, [row for row in crime_api.iterrows()
                                        if row.y == self.crime.y])


if __name__ == '__main__':
    unittest.main()
