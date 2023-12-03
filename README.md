# An Assessment of the Impact of the Baltimore Red Line on Job Accessibility

This is the codebase accompanying our report [An Assessment of the Impact of the Baltimore Red Line on Job Accessibility]().

## The working group
- [Yangxinyu Xie](https://xieyangxinyu.github.io), PhD Candidate, Department of Statistics, University of Pennsylvania
- [James Pizzurro](https://aries.dcmetrohero.com/faq#about), ARIES for Transit Project
- [Fadil Santosa](https://snfagora.jhu.edu/person/fadil-santosa/), Professor, Department of Applied Mathematics and Statistics, Johns Hopkins University
- [Elizabeth O’Reilly](https://sites.google.com/view/eliza-oreilly/home), Assistant Professor, Department of Applied Mathematics and Statistics, Johns Hopkins University 

We acknowledge the contributions of the following individuals to this report:
- Adam Lee, Energage
- Craig Gross, Michigan State University
- Kethaki Varadan, Lawrence Livermore National Laboratory
- Meghan Weil Latshaw, Associate Scientist, Johns Hopkins University
- Eliora Bard, Howard County Community College
- Thomas Li, Johns Hopkins University


## Requirements

We use poetry for maintaining package dependencies. In particular, we use Python 3.10. Dependency can be installed using the following command:
```
poetry install
```

To activate the virtual environment, run
```
poetry shell
```

To deactivate, run
```
exit
```

## List of resources we used for this project
- [r5py](https://r5py.readthedocs.io/en/stable/)
- [Transitland Source Feeds](https://www.transit.land/feeds)
     - [API key signup link](https://app.interline.io/products/tlv2_api/orders/new)
- [Adherence + Reliability + Integrity Evaluation System for Transit](https://aries.dcmetrohero.com)
- US Census API:
     - [census](https://pypi.org/project/census/)
     - [us](https://pypi.org/project/us/)
          - [API key signup link](https://api.census.gov/data/key_signup.html)
          - API Variables in [/data/2021/acs/acs5/variables](https://api.census.gov/data/2021/acs/acs5/variables.html)
- [LEHD Origin-Destination Employment Statistics (LODES)](https://lehd.ces.census.gov/data/)
- [Red Line Routes](https://www.google.com/maps/d/viewer?mid=1-nQTrR-62ggDsL5BaeBK20_X8wA&hl=en_US)

# Steps to Reproduce the Results

Please refer to the project directory tree below.

### Download the Raw Data.
The raw data are downloaded from various sources listed above. We prepared a [Box Drive link](https://upenn.box.com/s/08a0r28gho4ahxfoxmatqsjnz1tyg303) with all the raw and processed data we used for this project. GTFS data from Transit Land can be downloaded from the script, by providing your API key in `src/config.yaml` and running 
```
python src/prepare_GTFS/download_GTFS.py
```
LODES data can also be downloaded from the script, by running 
```
python src/data visualisation/download_lodes_data.py
```
### Generate the processed data:
- Step 0: Change to the root directory of this project. You can change the parameters for the scripts below in `src/config.yaml`.
- Step 1: Preprocess historical bus data. Run
```
python src/preprocess.py
```
- Step 2: Prepare GTFS data. Run 
```
python src/prepare_GTFS/real_time_bus_data_imputation.py
python src/prepare_GTFS/add_red_line.py
```
- Step 3: Compute Job Accessibility. Run
```
python src/accessibility/job_data.py
python src/accessibility/job_accessibility.py
python src/accessibility/quantile.py
python src/accessibility/diff.py
```
`job_data.py` computes the number of jobs at each census block; `job_accessibility.py` computes the gravity-based job accessibility of each census block for each business day from January to March; `quantile.py` computes the 25%, 50% and 75% quantile of the job accessibility across these business days in this study; `diff.py` computes the 25%, 50% and 75% quantile of the change in job accessibility across these business days.

### Visualize the Results

All results in the report can be reproduced by running the notebooks under `src/data visualization`.


## Project Directory Tree

```
├── README.md
├── poetry.lock
├── processed_data
│   ├── bus_accurate_data.csv
│   ├── job_accessibility
│   │   ├── job_totals
│   │   │   ├── 30_diff.csv
│   │   │   ├── 45_diff.csv
│   │   │   ├── red_line
│   │   │   │   ├── 2023-01-03
│   │   │   │   │   ├── 30.csv
│   │   │   │   │   ├── 45.csv
│   │   │   │   │   └── 60.csv
│   │   │   │   ├── ...
│   │   │   ├── red_line_30_accessibility.csv
│   │   │   ├── red_line_45_accessibility.csv
│   │   │   ├── transit_status_quo
│   │   │   │   ├── 2023-01-03
│   │   │   │   │   ├── 30.csv
│   │   │   │   │   ├── 45.csv
│   │   │   │   │   └── 60.csv
│   │   │   │   ├── ...
│   │   │   ├── transit_status_quo_30_accessibility.csv
│   │   │   └── transit_status_quo_45_accessibility.csv
│   │   └── mid_to_lower_job_totals
│   │       ├── 30_diff.csv
│   │       ├── 45_diff.csv
│   │       ├── red_line
│   │       │   ├── 2023-01-03
│   │       │   │   ├── 30.csv
│   │       │   │   ├── 45.csv
│   │       │   │   └── 60.csv
│   │       │   ├── ...
│   │       ├── red_line_30_accessibility.csv
│   │       ├── red_line_45_accessibility.csv
│   │       ├── transit_status_quo
│   │       │   ├── 2023-01-03
│   │       │   │   ├── 30.csv
│   │       │   │   ├── 45.csv
│   │       │   │   └── 60.csv
│   │       │   ├── ...
│   │       ├── transit_status_quo_30_accessibility.csv
│   │       └── transit_status_quo_45_accessibility.csv
│   ├── job_totals_blocks.csv
│   ├── mid_to_lower_job_centers.pkl
│   ├── redline.zip
│   ├── residents.pkl
│   ├── service_area.pkl
│   ├── travel_time_matrices
│   │   ├── 2023-01-03_travel_time.csv
│   │   ├── ...
│   │   ├── 2023-05-31_travel_time.csv
│   │   └── rewrite.py
│   ├── updated_gtfs
│   │   ├── 2023-01-03.zip
│   │   ├── ...
│   │   └── 2023-05-31.zip
│   ├── walking_service_area.pkl
│   └── workplace.pkl
├── pyproject.toml
├── raw_data
│   ├── Baltimore Red Line- Alignment.csv
│   ├── Baltimore Red Line- Stations.csv
│   ├── bus.zip # downloaded from TransitLand
│   ├── bus_accurate_data.csv # historical bus data at the stop level, provided by ARIES for Transit
│   ├── commuterbus_gtfs.zip # downloaded from TransitLand
│   ├── maryland-latest.osm.pbf # OpenStreetMap
│   ├── md_od_main_JT00_2020.csv.gz # LODES Data
│   ├── md_rac_S000_JT00_2020.csv.gz # LODES Data
│   ├── md_wac_S000_JT00_2020.csv.gz # LODES Data
│   ├── rail_gtfs.zip # downloaded from TransitLand
│   ├── subway_gtfs.zip # downloaded from TransitLand
│   ├── train_gtfs.zip # downloaded from TransitLand
│   └── transitland_bus # downloaded from TransitLand
│       ├── agency.txt
│       ├── calendar.txt
│       ├── calendar_attributes.txt
│       ├── calendar_dates.txt
│       ├── directions.txt
│       ├── fare_containers.txt
│       ├── fare_leg_rules.txt
│       ├── fare_products.txt
│       ├── fare_transfer_rules.txt
│       ├── feed_info.txt
│       ├── rider_categories.txt
│       ├── routes.txt
│       ├── shapes.txt
│       ├── stop_times.txt
│       ├── stops.txt
│       └── trips.txt
├── redline # Simulated GTFS for Red Line
│   ├── agency.txt
│   ├── calendar.txt
│   ├── calendar_dates.txt
│   ├── fare_containers.txt
│   ├── fare_leg_rules.txt
│   ├── fare_products.txt
│   ├── fare_transfer_rules.txt
│   ├── pathways.txt
│   ├── rider_categories.txt
│   ├── routes.txt
│   ├── shapes.txt
│   ├── stop_times.txt
│   ├── stops.txt
│   └── trips.txt
├── src
│   ├── accessibility
│   │   ├── diff.py
│   │   ├── job_accessibility.py
│   │   ├── job_data.py
│   │   ├── quantile.py
│   │   └── util.py
│   ├── config.yaml
│   ├── data visualization
│   │   ├── case studies.ipynb
│   │   ├── download_lodes_data.py
│   │   ├── job centers.ipynb
│   │   ├── job_accessibility.ipynb
│   │   ├── network.ipynb
│   │   └── util.py
│   ├── prepare_GTFS
│   │   ├── add_red_line.py
│   │   ├── download_GTFS.py
│   │   ├── real_time_bus_data_imputation.py
│   │   └── util.py
│   ├── preprocessing
│   │   └── preprocessing.py
│   ├── travel_time_computation
│   │   ├── prepare_data.py
│   │   ├── travel_time_Baltimore.py
│   │   └── travel_time_computation.py
│   └── util.py
└── tree.txt
```