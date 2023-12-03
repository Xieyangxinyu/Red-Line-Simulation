import geopandas as gpd
import numpy as np
import pandas as pd
from geopy.distance import geodesic
import time
import os
import shutil
from itertools import accumulate
from src.util import get_config
from scipy.spatial.distance import cdist

def cumulativeSum(lst):
    return list(accumulate(lst))

def matching(x, y):
    distances = cdist(x, y, metric='euclidean')

    # Find the index of the closest vector in y for each vector in x
    closest_indices = np.argmin(distances, axis=1)
    return closest_indices

config = get_config()

raw_data_path = config["raw_data_path"]
processed_data_path = config["processed_data_path"]

def add_red_line(period, speed, earliest_hour, latest_hour):

    num_of_trips = int((latest_hour - earliest_hour) * 60 / period)

    stations = gpd.read_file(f'{raw_data_path}Baltimore Red Line- Stations.csv', crs=4326)

    segments = gpd.read_file(f'{raw_data_path}Baltimore Red Line- Alignment.csv', crs=4326)

    res = segments.apply(lambda x: [y for y in x['geometry'].coords], axis=1).loc[0]

    shapes = pd.DataFrame()
    shapes['shape_id'] = ["RED" for i in range(len(res))]
    shapes['shape_pt_lat'] = [x for _, x in res]
    shapes['shape_pt_lon'] = [y for y, _ in res]
    shapes['shape_pt_sequence'] = [i + 1 for i in range(len(res))]
    distances = []
    coords_1 = (res[0][1], res[0][0])
    # Compute distance traveled for the shape file
    for y,x in res:
        coords_2 = (x,y)
        distances.append(geodesic(coords_1, coords_2).miles)
        coords_1 = coords_2
    shapes['shape_dist_traveled'] = cumulativeSum(distances)

    stations['lon'] = stations.geometry.x
    stations['lat'] = stations.geometry.y

    stations = stations.sort_values(by=['lon']).reset_index(drop=True)

    longitudes = stations['lon'].to_list()
    latitudes = stations['lat'].to_list()

    res = res + [(latitudes[-1], longitudes[-1])]

    station_points = list(stations.apply(lambda x: x['geometry'].coords[0], axis=1))
    # get all the break points of the segments
    break_points = res
    matches = matching(station_points, break_points)

    distance = 0
    distances = []
    coords_1 = (latitudes[0], longitudes[0])
    n = len(res)
    point = 0
    for idx, station in stations.iterrows():
        station_y = station['lon']
        station_x = station['lat']
        while point < n:
            point += 1
            y,x = res[point]
            if point < matches[idx]:
                coords_2 = (x, y)
                distance += geodesic(coords_1, coords_2).miles
                coords_1 = coords_2
            else:
                coords_2 = (station_x, station_y)
                distance += geodesic(coords_1, coords_2).miles
                distances.append(distance)
                coords_1 = (x, y)
                distance = geodesic(coords_2, coords_1).miles
                break

    # Create dataframe for stops
    stops = pd.DataFrame()
    stops['stop_id'] = list(stations.index + 1)
    stops['stop_name'] = stations['name']
    stops['stop_lat'] = stations['lat']
    stops['stop_lon'] = stations['lon']

    # Create dataframe for trips
    trips = pd.DataFrame()

    trips['route_id'] = [99999 for i in range(num_of_trips * 2)]

    trips['service_id'] = 201
    trips['trip_id'] = [i + 1 for i in range(num_of_trips * 2)]
    trips['trip_headsign'] = ['Centers for Medicare and Medicaid Services' for i in range(num_of_trips)] + ['Bayview MARC' for i in range(num_of_trips)]
    trips['direction_id'] = [0 for i in range(num_of_trips)] + [1 for i in range(num_of_trips)]
    trips['shape_id'] = "RED"

    # Create dataframe for stop times
    stop_times = pd.DataFrame()

    def to_time_str(t):
        time_format = time.strftime("%H:%M:%S", time.gmtime(int(t)))
        return time_format

    start = earliest_hour*60*60

    arrival_time = []
    trip_id = []
    stop_id = []
    stop_sequence = []
    for i in range(num_of_trips):
        start_time = start + i * period * 60
        arrival_time = arrival_time + list(start_time + np.array(cumulativeSum(distances))/ speed * 60 * 60)
        trip_id = trip_id + [i + 1 for _ in range(len(stations))]
        stop_id = stop_id + list(stations.index + 1)
        stop_sequence = stop_sequence + [k + 1 for k in range(len(stations))]

    trip_id = trip_id + list(num_of_trips + np.array(trip_id))
    stop_sequence = stop_sequence + stop_sequence

    reversed_distances = [0] + distances[::-1][:-1]
    for i in range(num_of_trips):
        start_time = start + i * period * 60
        arrival_time = arrival_time + list(start_time + np.array(cumulativeSum(reversed_distances))/ speed * 60 * 60)
        stop_id = stop_id + list(stations.index + 1)[::-1]

    stop_times['trip_id'] = trip_id
    stop_times['arrival_time'] = arrival_time
    stop_times['arrival_time'] = stop_times['arrival_time'].apply(to_time_str)
    stop_times['departure_time'] = stop_times['arrival_time']
    stop_times['stop_id'] = stop_id
    stop_times['stop_sequence'] = stop_sequence

    folder_path = 'redline/'
    os.makedirs(folder_path, exist_ok=True)

    shapes.to_csv(f"{folder_path}shapes.txt", index = False)
    stops.to_csv(f"{folder_path}stops.txt", index = False)
    trips.to_csv(f"{folder_path}trips.txt", index = False)
    stop_times.to_csv(f"{folder_path}stop_times.txt", index = False)

    folder_path_to_zip = "./redline"
    output_zip_path = processed_data_path + "/redline"

    shutil.make_archive(output_zip_path, 'zip', folder_path_to_zip)


if __name__ == "__main__":
    add_red_line(config["period"], config["speed"], config["early_time"], config["late_time"])
