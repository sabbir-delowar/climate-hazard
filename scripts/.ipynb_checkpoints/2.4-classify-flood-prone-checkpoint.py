def main():
    #!/usr/bin/env python
    # coding: utf-8

    # # Import Libraries

    # In[2]:


    import os
    import numpy as np
    import rasterio
    import rioxarray
    import geopandas as gpd
    import pandas as pd
    import matplotlib.pyplot as plt




    # # Define Paths

    # In[10]:


    # Inputs
    input_hand_tif = "data/interim/hand/hand.tif"
    aoi_shp = "data/aoi/aoi-multipoly.shp"

    # Outputs
    hand_dir = "data/interim/hand"
    os.makedirs(hand_dir, exist_ok=True)
    output_normalised_tif = os.path.join(hand_dir, "hand-normalised.tif")

    results_dir = "results/individual-hazards"
    os.makedirs(results_dir, exist_ok=True)
    output_csv = os.path.join(results_dir, "hand-hazard.csv")


    # # Normalise HAND raster to 0–1

    # In[15]:


    with rasterio.open(input_hand_tif) as src:
        hand_data = src.read(1)
        profile = src.profile.copy()

        # Ignore negative/nodata
        valid_hand = hand_data[hand_data >= 0]
        hand_min = valid_hand.min()
        hand_max = valid_hand.max()

        # Apply relative normalisation
        hand_normalised = (hand_max - hand_data) / (hand_max - hand_min)
        hand_normalised = np.clip(hand_normalised, 0, 1)

    profile.update({
        "dtype": 'float32',
        "count": 1,
        "compress": 'lzw',
        "nodata": None
    })

    with rasterio.open(output_normalised_tif, 'w', **profile) as dst:
        dst.write(hand_normalised, 1)


    # # Zonal statistics: mean HAND hazard per district

    # In[16]:


    aoi = gpd.read_file(aoi_shp)

    with rasterio.open(output_normalised_tif) as src:
        hand_crs = src.crs

    aoi = aoi.to_crs(hand_crs)

    aoi_names = []
    aoi_scores = []

    with rasterio.open(output_normalised_tif) as src:
        for idx, row in aoi.iterrows():
            geom = [row.geometry]
            try:
                out_image, out_transform = rasterio.mask.mask(src, geom, crop=True)
                data = out_image[0]
                data = data[data >= 0]  # exclude negative or nodata
                if data.size > 0:
                    mean_val = round(float(data.mean()), 4)
                else:
                    mean_val = None
            except ValueError:
                # Polygon outside raster
                mean_val = None

            aoi_names.append(row["name"])
            aoi_scores.append(mean_val)


    # # Save district-level hazard CSV

    # In[17]:


    df = pd.DataFrame({
        "district": aoi_names,
        "hand_hazard": aoi_scores
    })

    df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    main()
