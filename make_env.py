import geopandas as gpd
import csv

bounds = gpd.read_file("./data/liverpool_bounds.shp")

x_min, y_min, x_max, y_max = bounds.total_bounds

x_min = int(round(x_min/1000))
x_max = int(round(x_max/1000))

y_min = int(round(y_min/1000))
y_max = int(round(y_max/1000))

env = []
for _ in range(x_min, x_max):
    row = []
    for _ in range(y_min, y_max):
        row.append(50)
    env.append(row)

print(env)

with open('env.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(env)
f.close()
