import pandas as pd
import os
from datetime import timedelta
from src.util import get_config

config = get_config()
processed_path = config['processed_data_path']

def impedance(time, thresh):
    return max((thresh * 2) / (thresh + time) - 1, 0)

modes = ['transit_status_quo', 'red_line']
time_col = {'transit_status_quo': 'travel_time_before', 'red_line': 'travel_time_after'}

def compute_job_accessibility(travel_time, job_totals, min_thresh, max_thresh, thresh_step, date):

    df = job_totals.merge(travel_time, left_on="w_geocode", right_on="to_id")

    df.drop("w_geocode", axis=1, inplace=True)
    df.rename(columns={"from_id": "h_geocode",}, inplace=True)

    for mode in modes:
        for thresh in range(min_thresh, max_thresh + thresh_step, thresh_step):
            below_df = df[df[time_col[mode]] <= thresh].copy()
            below_df["gravity"] = below_df[time_col[mode]].apply(lambda t: impedance(t, thresh))
            for job_type in ['job_totals', 'mid_to_lower_job_totals']:
                below_df["accessibility"] = below_df["gravity"] * below_df[job_type]

                final_df = below_df.groupby('h_geocode')[[job_type, 'accessibility']].sum().reset_index()

                dir_path = processed_path + f"job_accessibility/{job_type}/{mode}/{date}"

                os.makedirs(dir_path, exist_ok=True)
                final_df.to_csv(f"{dir_path}/{int(thresh)}.csv")


if __name__ == "__main__":
    
    begin_date = config['begin_date']
    end_date = config['end_date']

    # Define the step (in this case, one day)
    step = timedelta(days=1)

    # Iterate through dates from begin_date to end_date
    current_date = begin_date

    while current_date <= end_date:
        date = current_date.strftime('%Y-%m-%d')
        current_date += step
        transit_time_csv = f'{processed_path}/travel_time_matrices/{date}_travel_time.csv'
        if os.path.exists(transit_time_csv):
            print(date)
            transit_time = pd.read_csv(transit_time_csv)
            transit_time = transit_time.fillna(9999)

            job_totals = pd.read_csv(f'{processed_path}/job_totals_blocks.csv')
            min_thresh = 30
            max_thresh = 60
            thresh_step = 15

            compute_job_accessibility(transit_time, job_totals, 
                                    min_thresh, max_thresh,
                                    thresh_step, date)