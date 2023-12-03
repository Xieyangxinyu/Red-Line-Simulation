from datetime import datetime
import pandas as pd
import random


def to_time(time_string):
    return datetime.strptime(time_string, "%H:%M:%S")

def get_time_diff(before, after):
    return datetime.strptime(after, "%H:%M:%S") - datetime.strptime(before, "%H:%M:%S")

def get_time_diff_rev(after, before):
    return datetime.strptime(after, "%H:%M:%S") - datetime.strptime(before, "%H:%M:%S")

def impute_partial_times(trip_df):
    observed_times = trip_df.dropna(subset=["arrival_time"])
    if (len(observed_times) == len(trip_df)) or len(observed_times) == 0:
        return trip_df
    
    # Iterate through known time points to calculate and apply estimated times
    for i in range(1, len(observed_times)):
        prev_row = observed_times.iloc[i - 1]
        next_row = observed_times.iloc[i]
        mask = (trip_df["arrival_time"].isna()) & \
            (trip_df["trip_distance_traveled"] >= prev_row["trip_distance_traveled"]) & \
                (trip_df["trip_distance_traveled"] <= next_row["trip_distance_traveled"])
        if len(trip_df[mask]) > 0:
            # Calculate time difference and speed for this segment
            time_difference = get_time_diff(prev_row["arrival_time"], next_row["arrival_time"])
            distance_difference = next_row["trip_distance_traveled"] - prev_row["trip_distance_traveled"]
            speed = distance_difference / time_difference.total_seconds()
            
            # Calculate and update estimated arrival and departure times for missing rows within the segment
            trip_df.loc[mask, "arrival_time"] = to_time(prev_row["arrival_time"]) + \
                pd.to_timedelta((trip_df.loc[mask, "trip_distance_traveled"] - prev_row["trip_distance_traveled"]) / speed, unit="s")
            trip_df.loc[mask, "arrival_time"] = pd.to_datetime(trip_df['arrival_time'][mask]).dt.strftime('%H:%M:%S')
    
    observed_times.reset_index(inplace=True)

    # Impute up to the first stop
    cur_row = observed_times.iloc[0]
    mask = (trip_df["arrival_time"].isna()) & (trip_df["trip_distance_traveled"] <= cur_row["trip_distance_traveled"])
    if len(trip_df[mask]) > 0:
        
        trip_df.loc[mask, "arrival_time"] = \
            (to_time(cur_row['arrival_time']) - \
             trip_df["scheduled_visit_time"][mask].apply(get_time_diff, args = (cur_row["scheduled_visit_time"],))).dt.strftime('%H:%M:%S')

    # Impute down to the last stop
    cur_row = observed_times.iloc[len(observed_times) - 1]
    mask = (trip_df["arrival_time"].isna()) & (trip_df["trip_distance_traveled"] >= cur_row["trip_distance_traveled"])
    if len(trip_df[mask]) > 0:

        trip_df.loc[mask, "arrival_time"] = \
            (to_time(cur_row['arrival_time']) + \
             trip_df["scheduled_visit_time"][mask].apply(get_time_diff_rev, args = (cur_row["scheduled_visit_time"],))).dt.strftime('%H:%M:%S')
    
    return trip_df

def impute_full_times(trip_id, file_paths):
    file_rand = random.sample(file_paths, len(file_paths))
    for file_path in file_rand:
        df = pd.read_csv(f'processed_data/stop_times_temp/{file_path}')
        trip_ids_to_replace = df.loc[df.arrival_time.isna()].trip_id.unique()
        if trip_id not in trip_ids_to_replace:
            return df.loc[df.trip_id == trip_id] 