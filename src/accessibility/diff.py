import pandas as pd
import os
from datetime import timedelta
from src.util import get_config

config = get_config()
processed_path = config['processed_data_path']

if __name__ == "__main__":
    
    begin_date = config['begin_date']
    end_date = config['end_date']

    # Define the step (in this case, one day)
    step = timedelta(days=1)

    
    for job_type in ['job_totals', 'mid_to_lower_job_totals']:
        for thresh in [30, 45]:
            diff_dfs = []

            # Iterate through dates from begin_date to end_date
            current_date = begin_date
            while current_date <= end_date:
                date = current_date.strftime('%Y-%m-%d')
                current_date += step

                dir_path = processed_path + f"job_accessibility/{job_type}/transit_status_quo/{date}/{int(thresh)}.csv"
                if os.path.exists(dir_path):
                    status_quo_df = pd.read_csv(dir_path)
                    red_line_df = pd.read_csv(processed_path + f"job_accessibility/{job_type}/red_line/{date}/{int(thresh)}.csv")

                    diff = pd.DataFrame()
                    diff['diff'] = (red_line_df['accessibility'] - status_quo_df['accessibility'])/status_quo_df['accessibility']
                    diff['h_geocode'] = red_line_df['h_geocode']
                    diff_dfs.append(diff)

            all_data = pd.concat(diff_dfs, ignore_index=True)

            diff_df = pd.DataFrame()
            diff_df['median'] = all_data.groupby('h_geocode')['diff'].median()
            diff_df['25'] = all_data.groupby('h_geocode')['diff'].quantile(0.25)
            diff_df['75'] = all_data.groupby('h_geocode')['diff'].quantile(0.75)

            diff_df.to_csv(processed_path + f'job_accessibility/{job_type}/{thresh}_diff.csv')
