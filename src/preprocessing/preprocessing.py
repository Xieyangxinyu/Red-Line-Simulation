import datetime
import pandas as pd
import os
from src.util import get_config

config = get_config()

raw_data_path = config["raw_data_path"]
processed_data_path = config["processed_data_path"]
bus_accurate_data_path = config["bus_accurate_csv"]

date_range = [config["begin_date"], config["end_date"]]
hour_range = [config["begin_hour"], config["end_hour"]]


class filterTool:

    @staticmethod
    def verify_range(range):
        if len(range) == 2:
            assert range[0] < range[1]

    
    def __init__(self, date_range: list[datetime.date] = [], hour_range: list[int] = []):
        assert (len(date_range) == 0) or (len(date_range) == 2)
        assert (len(hour_range) == 0) or (len(hour_range) == 2)
        self.verify_range(date_range)
        self.verify_range(hour_range)

        self.date_range = date_range
        self.hour_range = hour_range
        
    
    # restrict to all buses within an interval of hours
    def filter_by_time(self, trip_data):

        def filter(trip_data_by_id):
            trip_data_by_id = trip_data_by_id.reset_index()
            start_hour = trip_data_by_id['scheduled_visit_time'][0].hour
            last_row_index = len(trip_data_by_id)
            end_hour = trip_data_by_id['scheduled_visit_time'][last_row_index - 1].hour
            if (end_hour >= self.hour_range[0]) and (start_hour < self.hour_range[1]):
                return trip_data_by_id
            else:
                return None
        
        trip_data = trip_data.groupby("trip_id").apply(filter).reset_index(drop=True)
        return trip_data

    # restrict to all buses within an interval of dates
    def filter_by_date(self, trip_data):
        trip_data = trip_data[trip_data['date'] >= self.date_range[0]]
        trip_data = trip_data[trip_data['date'] <= self.date_range[1]]
        return trip_data
    
    def filter_data(self, trip_data: pd.DataFrame) -> pd.DataFrame:
        if len(self.date_range) == 2:
            trip_data = self.filter_by_date(trip_data)
        if len(self.hour_range) == 2:
            trip_data = self.filter_by_time(trip_data)

        return trip_data


def preprocess_observed_bus_times(bus_data_csv_path: str,
                                  date_range: list[datetime.date] = [], hour_range: list[int] = []):

    observed_times_df = pd.read_csv(raw_data_path + bus_data_csv_path)
    try:
        observed_times_df.rename(columns={'vehicle_stop_id': 'stop_id'}, inplace=True)
    except:
        pass
    
    observed_times_df['scheduled_visit_time'] = pd.to_datetime(observed_times_df['scheduled_visit_time'], format='%Y-%m-%d %H:%M:%S.%f %Z')

    observed_times_df['date'] = observed_times_df['scheduled_visit_time'].dt.date

    filter_tool = filterTool(date_range, hour_range)
    observed_times_df = filter_tool.filter_data(observed_times_df)
    
    observed_times_df['scheduled_visit_time'] = observed_times_df['scheduled_visit_time'].dt.strftime('%H:%M:%S')
    
    observed_mask = observed_times_df['observed_visit_time'].notna()
    observed_times_df.loc[observed_mask, ['observed_visit_time']] = \
        pd.to_datetime(observed_times_df['observed_visit_time'][observed_mask], format='%Y-%m-%d %H:%M:%S.%f %Z').dt.strftime('%H:%M:%S')
    
    observed_times_df = observed_times_df[['trip_id', 'stop_id', 'date', 'observed_visit_time', 
                                                'scheduled_visit_time', 'trip_distance_traveled']]

    os.makedirs(processed_data_path, exist_ok=True)  
    observed_times_df.to_csv(processed_data_path + bus_data_csv_path, index=False)


if __name__ == "__main__":
    preprocess_observed_bus_times(
        bus_accurate_data_path,
        date_range,
        hour_range
    )