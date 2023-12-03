from util import get_lodes_file, restrict_to_Baltimore
from src.util import get_config

config = get_config()
raw_path = config['raw_data_path']
processed_path = config['processed_data_path']

# See documentation at https://lehd.ces.census.gov/data/#lodes
# or https://lehd.ces.census.gov/data/lodes/LODES8/LODESTechDoc8.0.pdf

def compute_job_totals(seg = "S000", year = '2020', lodes_type = 'wac'):
    job_totals_file = processed_path + f"job_totals_blocks.csv"
    if lodes_type == 'wac':
        geo_col = 'w_geocode'
    else:
        geo_col = 'h_geocode'
    
    lodes_file = f"md_{lodes_type}_{seg}_JT00_{year}.csv.gz"

    job_data = get_lodes_file(raw_path, lodes_type, lodes_file)
    
    job_data = restrict_to_Baltimore(job_data, geo_col)

    job_data['job_totals'] = job_data['C000']

    job_data['mid_to_lower_job_totals'] = job_data['CE01'] + job_data['CE02']

    job_data = job_data[[geo_col, "job_totals", "mid_to_lower_job_totals"]]
    job_data = job_data.groupby(geo_col).sum().reset_index()
    job_data = job_data.loc[job_data["job_totals"] != 0]
    job_data.to_csv(job_totals_file, index=False)
    print(job_data.describe())
    print(job_data.sum())

    return job_data

compute_job_totals()