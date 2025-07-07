def main():
    
    import os
    import geopandas as gpd
    import requests
    import zipfile
    from tqdm import tqdm

    # # Define Paths

    # AOI and tile grid paths
    aoi_path = "data/aoi/aoi-multipoly.shp"
    tile_grid_path = "data/FABDEM_v1-2_tiles.geojson"

    # Folder to save downloaded tiles
    download_dir = "data/interim/fabdem"
    os.makedirs(download_dir, exist_ok=True)


    # # Load AOI Shapefile & Load FABDEM Tile Grid

    aoi = gpd.read_file(aoi_path)
    tiles = gpd.read_file(tile_grid_path)

    if tiles.crs != aoi.crs:
        aoi = aoi.to_crs(tiles.crs)


    # # Extract Fabdem URLs

    # Perform spatial intersection
    intersection = gpd.overlay(tiles, aoi, how='intersection')

    base_url = "https://data.bris.ac.uk/datasets/s5hqmjcdj8yo2ibzi9b4ew3sn/"

    # FABDEM tiles store full file_name in properties
    file_names = intersection['zipfile_name'].unique().tolist()
    urls = [base_url + fname for fname in file_names]


    # # Download Function

    def download_file(url, out_folder):
        local_filename = os.path.join(out_folder, url.split("/")[-1])
        if os.path.exists(local_filename):
            print(f"✅ Already exists: {local_filename}")
            return
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Downloaded: {local_filename}")
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")


    # # Bulk Download

    print(f"✅ Downloading {len(urls)} tiles to {download_dir}")

    for url in tqdm(urls):
        download_file(url, download_dir)

    print("✅ All downloads attempted!")


    # # Extract Tiles

    zip_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.endswith(".zip")]
    print(f"✅ Found {len(zip_files)} zip files to extract.")
    for z in zip_files:
        print("-", os.path.basename(z))

    for zf in tqdm(zip_files, desc="Unzipping all tiles"):
        with zipfile.ZipFile(zf, 'r') as archive:
            for member in archive.namelist():
                if member.lower().endswith('.tif'):
                    # Flatten folder structure
                    out_filename = os.path.join(download_dir, os.path.basename(member))
                    with archive.open(member) as source, open(out_filename, 'wb') as target:
                        target.write(source.read())

if __name__ == "__main__":
    main()
