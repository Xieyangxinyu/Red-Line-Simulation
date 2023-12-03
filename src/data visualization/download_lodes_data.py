from src.util import get_config, get_lodes_file

config = get_config()

raw_path = config['raw_data_path']

def download_LODES_data():
    lodes_type = 'rac'
    seg = 'S000'
    year = '2020'

    for lodes_type in ['rac', 'wac']:
        lodes_file = f"md_{lodes_type}_{seg}_JT00_{year}.csv.gz"
        get_lodes_file(raw_path, lodes_type, lodes_file)
    
    lodes_type = 'od'
    seg = 'main'
    lodes_file = f"md_{lodes_type}_{seg}_JT00_{year}.csv.gz"
    get_lodes_file(raw_path, lodes_type, lodes_file)

download_LODES_data()