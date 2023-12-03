import geopandas as gpd
from shapely.ops import unary_union
import pandas as pd
import folium
from census import Census
from us import states

# Census Data API: Variables in /data/2021/acs/acs5/variables https://api.census.gov/data/2021/acs/acs5/variables.html
c = Census("your cencus api key")


def load_LODES_data(path, geocode_col):
    df = pd.read_csv(path)
    df[geocode_col] = df[geocode_col].astype(str)
    df = df[df[geocode_col].str[:5] == '24510']
    return df

def load_Baltimore_blocks():
    # Load LODES data
    md_rac_df = load_LODES_data('../../raw_data/md_rac_S000_JT00_2020.csv.gz', 'h_geocode')
    md_wac_df = load_LODES_data('../../raw_data/md_wac_S000_JT00_2020.csv.gz', 'w_geocode')

    # Load Baltimore blocks
    gdf_Baltimore = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2022/TABBLOCK20//tl_2022_24_tabblock20.zip")
    gdf_Baltimore = gdf_Baltimore[gdf_Baltimore['COUNTYFP20'] == '510']
    gdf_Baltimore = gdf_Baltimore[['geometry', 'GEOID20']]

    # Take union of md_rac_df['h_geocode'] and md_wac_df['w_geocode']
    study_area = pd.concat([md_rac_df['h_geocode'], md_wac_df['w_geocode']]).unique()
    # Filter gdf_Baltimore to only include blocks in study_area
    gdf_Baltimore = gdf_Baltimore[gdf_Baltimore['GEOID20'].isin(study_area)]
    return gdf_Baltimore, md_rac_df, md_wac_df

def get_service_area(gdf_Baltimore: gpd.GeoDataFrame, stations: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    stations.crs = "NAD83"
    stations = stations.to_crs(26985)

    buf = stations.buffer(distance = 1320)
    buf = buf.to_crs("NAD83")
    union_buffer = unary_union(buf)
    return gdf_Baltimore[gdf_Baltimore.intersects(union_buffer)]

def get_Baltimore_city_map(stations = None, segments = None, zoom_start=13, location=[39.299236, -76.609383]):
    city_map = folium.Map(location=location, zoom_start=zoom_start)
    
    if stations is not None:
        for _, station in stations.iterrows():
            folium.Marker(
                location=[station.geometry.y, station.geometry.x],  # Extract latitude and longitude from the geometry
                icon=folium.Icon(color='red'),  # Specify the custom icon
            ).add_to(city_map)

    if segments is not None:
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in segments['geometry'][0].coords],
            color='red',
            weight=6,         # Adjust the line thickness
            opacity=1,      # Adjust the opacity
            dash_array='5, 10'
        ).add_to(city_map)

    return city_map

    return city_map

def save_png(city_map, path):
    png_data = city_map._to_png()
    with open(f'{path}.png', 'wb') as f:
        f.write(png_data)


def get_poverty_gdf(stations):
    
    cencus_blocks_groups = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2020/BG/tl_2020_24_bg.zip")
    baltimore_census = c.acs5.state_county_blockgroup(fields = ('NAME', 'C17002_001E', 'C17002_002E', 'C17002_003E', 'B01003_001E'),
                                      state_fips = states.MD.fips,
                                      county_fips = "510",
                                      tract = "*",
                                      blockgroup = "*",
                                      year = 2021)
    baltimore_df = pd.DataFrame(baltimore_census)
    baltimore_df["GEOID"] = baltimore_df["state"] + baltimore_df["county"] + baltimore_df["tract"] + baltimore_df['block group']

    cencus_blocks_groups = cencus_blocks_groups[(cencus_blocks_groups['GEOID'].str[:5] == '24510')]


    cencus_blocks_groups = get_service_area(cencus_blocks_groups, stations)
    baltimore_merge = cencus_blocks_groups.merge(baltimore_df, on = "GEOID")

    # We use ratio of income to poverty in the past 12 months (C17002_001E, total; C17002_002E, < 0.50; and C17002_003E, 0.50 - 0.99) variables and the total population (B01003_001E) variable.
    baltimore_poverty_bg = baltimore_merge[["GEOID", "geometry", "C17002_001E", "C17002_002E", "C17002_003E", "B01003_001E"]]
    baltimore_poverty_bg = baltimore_poverty_bg[baltimore_poverty_bg['B01003_001E'] > 0]
    baltimore_poverty_bg["Poverty_Rate"] = (baltimore_poverty_bg["C17002_002E"] + baltimore_poverty_bg["C17002_003E"]) / baltimore_poverty_bg["B01003_001E"] * 100
    return baltimore_poverty_bg