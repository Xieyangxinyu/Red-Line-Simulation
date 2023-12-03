# Allow 12 GB memory
import sys
sys.argv.append(["--max-memory", "12G"])
import datetime
from r5py import TransportNetwork, TravelTimeMatrixComputer, TransportMode


def compute_travel_time_matrix(origins, destinations, departure_time, transport_network, wait_minutes=30):

    travel_time_matrix_computer = TravelTimeMatrixComputer(
        transport_network,
        origins=origins,
        destinations=destinations,
        departure=departure_time,
        transport_modes=[TransportMode.TRANSIT, TransportMode.WALK],
        departure_time_window = datetime.timedelta(minutes=wait_minutes)
    )
    return travel_time_matrix_computer.compute_travel_times()



def compute_travel_time_matrices(origins, destinations, departure_time, osm_fp: str, GTFS: list[str], newline: str, wait_minutes=30):
    '''
    Compute travel time matrices before and after a new transit line is added.
    
    Parameters:
        origins: geopandas.GeoDataFrame
            - The origins of the travel time matrix; contains columns "geometry" and "id"
        destinations: geopandas.GeoDataFrame
            - The destinations of the travel time matrix; contains columns "geometry" and "id"
        departure_time: datetime.datetime
            - The departure time of the travel time matrix
        osm_fp: str
            - The filepath to the OSM data
        GTFS: list[str]
            - The list of filepath(s) to the GTFS data
        newline: str
            - The filepath to the newline GTFS data
        wait_minutes: int
            - The number of minutes to wait for a bus
    
    Returns:
        matrix_before_newline: r5py.TravelTimeMatrix
            - The travel time matrix before the new transit line is added
        matrix_after_newline: r5py.TravelTimeMatrix
            - The travel time matrix after the new transit line is added
    '''


    print("Preparing the transport network...")

    transport_network_before_newline = TransportNetwork(
        osm_fp,
        GTFS
    )

    print("Computing the travel time matrices...")

    origins["geometry"] = transport_network_before_newline.snap_to_network(origins["geometry"])
    destinations["geometry"] = transport_network_before_newline.snap_to_network(destinations["geometry"])

    matrix_before_newline = compute_travel_time_matrix(origins, destinations, departure_time, transport_network_before_newline, wait_minutes)

    GTFS.append(newline)
    transport_network_after_newline = TransportNetwork(
        osm_fp,
        GTFS
    )

    matrix_after_newline = compute_travel_time_matrix(origins, destinations, departure_time, transport_network_after_newline, wait_minutes)

    return matrix_before_newline, matrix_after_newline