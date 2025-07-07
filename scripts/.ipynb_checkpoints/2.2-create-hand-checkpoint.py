def main():

    import shutil
    import os
    import glob
    import geopandas as gpd
    import rasterio
    from rasterio.merge import merge
    from rasterio.mask import mask
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    import numpy as np
    import matplotlib.pyplot as plt
    from tqdm import tqdm



    # # Define Paths

    aoi_path = "data/aoi/aoi-multipoly.shp"
    tiles_folder = "data/interim/fabdem"
    output_dir = "data/interim/hand"
    os.makedirs(output_dir, exist_ok=True)
    output_mosaic = os.path.join(output_dir, "hand-dem.tif")


    # # Load All Files

    aoi = gpd.read_file(aoi_path)
    aoi = aoi.to_crs("EPSG:4326")

    tif_files = glob.glob(os.path.join(tiles_folder, "*.tif"))


    # # Mosaic Tiles

    print("✅ Mosaicking tiles. This may take a few minutes...")

    src_files_to_mosaic = [rasterio.open(fp) for fp in tif_files]
    mosaic, out_transform = merge(src_files_to_mosaic)

    print("✅ Mosaic complete!")


    # # Clip Mosaic to AOI

    aoi_geom = [feature["geometry"] for feature in aoi.__geo_interface__["features"]]

    meta = src_files_to_mosaic[0].meta.copy()
    meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform,
        "crs": "EPSG:4326"
    })

    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:
            dataset.write(mosaic)
            clipped_image, clipped_transform = mask(
                dataset=dataset,
                shapes=aoi_geom,
                crop=True
            )

    clipped_meta = meta.copy()
    clipped_meta.update({
        "height": clipped_image.shape[1],
        "width": clipped_image.shape[2],
        "transform": clipped_transform,
        "compress": None
    })

    # ✅ Step 2: Save clipped WGS84 temporarily
    temp_clipped_path = output_mosaic.replace(".tif", "_clipped_wgs84.tif")
    with rasterio.open(temp_clipped_path, "w", **clipped_meta) as dest:
        dest.write(clipped_image)


    # # Convert to UTM

    # ✅ Ask user for target CRS
    print("⭐ Enter the target EPSG code for reprojection.")
    print("Example options for Bangladesh:")
    print("- EPSG:32646 = UTM Zone 46N (Western Bangladesh)")
    print("- EPSG:32647 = UTM Zone 47N (Eastern Bangladesh)")

    # User input with a default fallback
    user_epsg = input("Enter EPSG code (default 32646): ").strip()
    if user_epsg == "":
        user_epsg = "32646"

    dst_crs = f"EPSG:{user_epsg}"
    print(f"✅ Using {dst_crs} for reprojection.")


    # In[9]:


    with rasterio.open(temp_clipped_path) as src:
        # Calculate the new transform, width, height for reprojection
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )

        # Create new profile for output GeoTIFF
        kwargs = {
            'driver': 'GTiff',
            'dtype': 'float32',
            'count': 1,
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'nodata': -32768       # Common elevation NoData value
        }

        for key, val in kwargs.items():

            # Perform reprojection and save
            with rasterio.open(output_mosaic, "w", **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.bilinear
                    )


    # # Delete the fabdem folder

    target_folder = "data/interim/fabdem"

    if os.path.exists(target_folder):
        confirm = input(f"⚠️ Are you sure you want to delete the entire folder {target_folder}? Type YES to confirm: ")
        if confirm == "YES":
            shutil.rmtree(target_folder)
            print(f"✅ Folder {target_folder} deleted.")
        else:
            print("❌ Deletion cancelled.")
    else:
        print(f"❌ Folder {target_folder} does not exist.")

if __name__ == "__main__":
    main()
