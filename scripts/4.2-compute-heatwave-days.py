def main():
    
    import os
    import xarray as xr
    import geopandas as gpd
    import rasterio
    import rasterio.mask
    import numpy as np
    import pandas as pd
    from tqdm import tqdm



    # # Define Paths

    data_dir = "data/interim/heat"
    aoi_shp = "data/aoi/aoi-multipoly.shp"
    output_csv = "results/individual-hazards/heat-hazard.csv"

    years = ["2020", "2021", "2022", "2023", "2024"]


    # # Load districts shapefile

    districts = gpd.read_file(aoi_shp)
    districts = districts.to_crs("EPSG:4326")
    districts = districts[['name', 'geometry']].copy()
    districts['heatwave_days'] = 0


    # # Collect district daily means

    all_records = []

    for year in years:
        nc_file = os.path.join(data_dir, f"era5-daily-max-{year}.nc")
        print(f"✅ Reading {nc_file}")

        ds = xr.open_dataset(nc_file)

        # Get temperature variable
        if '2m_air_temperature_maximum' in ds.data_vars:
            temp_K = ds['2m_air_temperature_maximum']
        elif 't2m' in ds.data_vars:
            temp_K = ds['t2m']
        else:
            raise ValueError("No valid temperature variable found!")

        temp_C = temp_K - 273.15

        for single_day in tqdm(temp_C['valid_time'].values, desc=f"Year {year}"):
            day_slice = temp_C.sel(valid_time=single_day)
            day_tif = os.path.join(data_dir, "temp_day.tif")
            day_slice.rio.to_raster(day_tif)

            with rasterio.open(day_tif) as src:
                for idx, row in districts.iterrows():
                    geom = [row.geometry]
                    try:
                        out_image, _ = rasterio.mask.mask(src, geom, crop=True)
                        data = out_image[0]
                        data = data[data > -100]

                        if data.size > 0:
                            max_val = data.max()
                            all_records.append({
                                'date': pd.to_datetime(single_day),
                                'district': row['name'],
                                'max_temp': max_val
                            })
                    except ValueError:
                        continue

            os.remove(day_tif)

    df = pd.DataFrame(all_records)
    df.to_csv("data/interim/heat/heat-hazard-records.csv", index=False)
    df = pd.read_csv("data/interim/heat/heat-hazard-records.csv")


    # # Compute 75th percentile threshold

    HEATWAVE_THRESHOLD_C = np.percentile(df['max_temp'], 95)
    print(f"✅ Data-derived heatwave threshold (95th percentile): {HEATWAVE_THRESHOLD_C:.2f} °C")


    # # Count heatwave days per district

    counts = df[df['max_temp'] >= HEATWAVE_THRESHOLD_C].groupby('district').size()
    counts = counts.reindex(districts['name']).fillna(0).astype(int)

    districts['heatwave_days'] = counts.values


    # # Rescale to 0–1 hazard

    min_days = districts['heatwave_days'].min()
    max_days = districts['heatwave_days'].max()

    districts['heat_hazard'] = (
        (districts['heatwave_days'] - min_days) / (max_days - min_days)
    ).clip(0, 1)

    districts[['name', 'heatwave_days', 'heat_hazard']].rename(
        columns={'name':'district'}
    ).to_csv(output_csv, index=False)


# In[ ]:
if __name__ == "__main__":
    main()