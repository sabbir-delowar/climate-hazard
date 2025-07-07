def main():

    import os
    import xarray as xr
    import rioxarray
    import geopandas as gpd
    import rasterio
    import rasterio.mask
    import pandas as pd
    import numpy as np
    from tqdm import tqdm

    # # Define Paths

    input_nc = "data/interim/era5_precip.nc"
    aoi_shp = "data/aoi/aoi-multipoly.shp"
    output_csv = "results/individual-hazards/rainfall-hazard.csv"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)


    # # Load districts shapefile

    districts = gpd.read_file(aoi_shp)
    districts = districts.to_crs("EPSG:4326")
    districts = districts[['name', 'geometry']].copy()
    districts['heavy_rain_months'] = 0


    # # Extract variable and convert to mm

    ds = xr.open_dataset(input_nc)
    rain_m = ds['tp']
    rain_mm = rain_m * 1000  # m to mm


    # #  Loop once over all months and districts

    all_records = []

    time_dim = rain_mm['valid_time']

    print("✅ Scanning monthly rasters and computing district means...")
    for t in tqdm(time_dim.values, desc="Processing months"):
        month_data = rain_mm.sel(valid_time=t)
        month_tif = "data/interim/temp_month.tif"
        month_data.rio.to_raster(month_tif)

        with rasterio.open(month_tif) as src:
            for idx, row in districts.iterrows():
                geom = [row.geometry]
                try:
                    out_image, _ = rasterio.mask.mask(src, geom, crop=True)
                    data = out_image[0]
                    data = data[data > -100]

                    if data.size > 0:
                        mean_val = data.mean()
                        all_records.append({
                            'month': pd.to_datetime(t),
                            'district': row['name'],
                            'mean_rain': mean_val
                        })
                except ValueError:
                    continue

        os.remove(month_tif)


    # # Compute 75th percentile threshold

    df = pd.DataFrame(all_records)

    RAIN_THRESHOLD_MM = np.percentile(df['mean_rain'], 95)
    print(f"✅ Data-derived rainfall threshold (95th percentile): {RAIN_THRESHOLD_MM:.2f} mm")


    # # Count heavy-rainfall months per district

    counts = df[df['mean_rain'] >= RAIN_THRESHOLD_MM].groupby('district').size()
    counts = counts.reindex(districts['name']).fillna(0).astype(int)

    districts['heavy_rain_months'] = counts.values


    # # Rescale to 0–1 hazard

    min_val = districts['heavy_rain_months'].min()
    max_val = districts['heavy_rain_months'].max()

    districts['rainfall_hazard'] = (
        (districts['heavy_rain_months'] - min_val) / (max_val - min_val)
    ).clip(0, 1)

    districts[['name', 'heavy_rain_months', 'rainfall_hazard']].rename(
        columns={'name':'district'}
    ).to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()
