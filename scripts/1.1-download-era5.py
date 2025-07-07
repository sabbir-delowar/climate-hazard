def main():
    
    import os
    import geopandas as gpd
    import cdsapi


    # AOI shapefile path
    aoi_path = "data/aoi/aoi-multipoly.shp"

    # Output path
    output_dir = "data/interim"
    os.makedirs(output_dir, exist_ok=True)
    output_nc = os.path.join(output_dir, "era5_precip.nc")


    # # Read AOI Shapefile and Calculate Bounding Box

    # Load AOI
    aoi_gdf = gpd.read_file(aoi_path)

    # Ensure it's in EPSG:4326
    aoi_gdf = aoi_gdf.to_crs("EPSG:4326")

    # Get total bounding box
    minx, miny, maxx, maxy = aoi_gdf.total_bounds

    # ERA5 API wants: [North, West, South, East]
    bbox = [maxy, minx, miny, maxx]


    # # Define Years and Months

    years = [str(y) for y in range(2020, 2025)]
    months = [f"{m:02d}" for m in range(1, 13)]


    # # Download ERA5-Land Monthly Means

    dataset = "reanalysis-era5-single-levels-monthly-means"
    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["total_precipitation"],
        "year": years,
        "month": months,
        "time": ["00:00"],
        "data_format": "netcdf",
        "area": bbox,
        "download_format": "unarchived"
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request, target= output_nc)

if __name__ == "__main__":
    main()
