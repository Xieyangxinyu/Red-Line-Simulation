from src.util import get_config, download_file
import shutil

config = get_config()

download_dir = config["raw_data_path"]
api_key = config["api_key"]
bus_feed_link = config["bus_feed_new_april19_june17"]
rail_feed_link = config["rail_feed_link"]
subway_feed_link = config["subway_feed_link"]
commuterbus_feed_link = config["commuterbus_feed_link"]
train_feed_link = config["train_feed_link"]
raw_data_path = config["raw_data_path"]

def get_transit_land_url(feed_link, api_key=api_key):
    return f"https://transit.land/api/v2/rest/feed_versions/{feed_link}/download?apikey={api_key}"

if __name__ == "__main__":
    download_file(get_transit_land_url(bus_feed_link), f"{download_dir}bus.zip")
    # unzip bus.zip
    shutil.unpack_archive(f"{download_dir}bus.zip", f"{raw_data_path}/transitland_bus/")

    download_file(get_transit_land_url(rail_feed_link), f"{download_dir}rail_gtfs.zip")
    download_file(get_transit_land_url(subway_feed_link), f"{download_dir}subway_gtfs.zip")
    download_file(get_transit_land_url(commuterbus_feed_link), f"{download_dir}commuterbus_gtfs.zip")
    download_file(get_transit_land_url(train_feed_link), f"{download_dir}train_gtfs.zip")