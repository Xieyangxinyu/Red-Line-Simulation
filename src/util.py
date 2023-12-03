import yaml
import requests
import os
import pandas as pd

def get_config():
    with open('src/config.yaml', "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return config


def download_file(url, local_filename):
    '''
    params:
        url: url of the file to download
        local_filename: local path to save the file.
    '''
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, "wb") as f:
            f.write(response.content)
        print(f"File {local_filename} downloaded successfully.")
    else:
        print("Failed to download the file.")


def get_lodes_file(raw_path, lodes_type, file_name):
    lodes_file = raw_path + file_name
    print("Downloading LODES data into " + lodes_file)
    url = f"https://lehd.ces.census.gov/data/lodes/LODES8/md/{lodes_type}/{file_name}"
    download_file(url, lodes_file)
