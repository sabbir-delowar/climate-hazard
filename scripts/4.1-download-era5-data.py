def main():
    #!/usr/bin/env python
    # coding: utf-8

    # # Import Libraries

    # In[1]:


    import cdsapi
    import xarray as xr
    import rioxarray
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import os



    # # Define Paths

    # In[3]:


    data_dir = "data/interim/heat"
    os.makedirs(data_dir, exist_ok=True)

    aoi_shp = "data/aoi/aoi-multipoly.shp"
    era5_file = os.path.join(data_dir, "era5-heat-monthly.nc")
    annual_mean_tif = os.path.join(data_dir, "annual-mean-temp.tif")
    hazard_csv = "results/individual-hazards/heat-hazard.csv"


    # # Download ERA5 Data

    # In[12]:


    aoi = gpd.read_file(aoi_shp)

    # Ensure it's in EPSG:4326
    aoi = aoi.to_crs("EPSG:4326")

    # Get total bounding box
    minx, miny, maxx, maxy = aoi.total_bounds

    # ERA5 API wants: [North, West, South, East]
    bbox = [maxy, minx, miny, maxx]

    dataset = "derived-era5-land-daily-statistics"
    years = ["2020", "2021", "2022", "2023", "2024"]
    for year in years:
        request = {
            "variable": ["2m_temperature"],
            "year": year,
            "month": [
                "01","02","03","04","05","06",
                "07","08","09","10","11","12"
            ],
            "day": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12",
            "13", "14", "15",
            "16", "17", "18",
            "19", "20", "21",
            "22", "23", "24",
            "25", "26", "27",
            "28", "29", "30",
            "31"
            ],
            "daily_statistic": "daily_maximum",
            "time_zone": "utc+06:00",
            "frequency": "1_hourly",
            "area": bbox,
        }
        target_file = os.path.join(data_dir, f"era5-daily-max-{year}.nc")
        print(f"✅ Downloading {year} to {target_file}")
        client.retrieve(dataset, request, target=target_file)

if __name__ == "__main__":
    main()
