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
        for mode in ['transit_status_quo', 'red_line']:
            for thresh in [30, 45]:
                accessibility_df = pd.DataFrame()

                file_paths = []

                # Iterate through dates from begin_date to end_date
                current_date = begin_date
                while current_date <= end_date:
                    date = current_date.strftime('%Y-%m-%d')
                    current_date += step

                    dir_path = processed_path + f"job_accessibility/{job_type}/{mode}/{date}/{int(thresh)}.csv"

                    if os.path.exists(dir_path):
                        file_paths.append(dir_path)

                all_data = pd.concat([pd.read_csv(file) for file in file_paths], ignore_index=True)
                # Compute the median & quantile job accessibility for each h_geocode

                accessibility_df['median'] = all_data.groupby('h_geocode')['accessibility'].median()
                accessibility_df['75'] = all_data.groupby('h_geocode')['accessibility'].quantile(0.75)
                accessibility_df['25'] = all_data.groupby('h_geocode')['accessibility'].quantile(0.25)

                accessibility_df.to_csv(processed_path + f'job_accessibility/{job_type}/{mode}_{thresh}_accessibility.csv')
