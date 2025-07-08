def main():

    import pandas as pd
    import geopandas as gpd
    import os



    # # Define Paths

    district_shp = "data/aoi/aoi-multipoly.shp"

    flood_csv = "results/individual-hazards/combined-flood-hazard.csv"
    heat_csv = "results/individual-hazards/heat-hazard.csv"

    output_dir = "results/total-hazard/"
    os.makedirs(output_dir, exist_ok=True)

    output_csv = os.path.join(output_dir, "total-hazard.csv")
    output_shp = os.path.join(output_dir, "total-hazard.shp")


    # # Load and merge files

    gdf = gpd.read_file(district_shp)
    gdf = gdf[['name', 'geometry']].copy()
    gdf = gdf.rename(columns={'name': 'district'})

    flood_df = pd.read_csv(flood_csv)
    heat_df = pd.read_csv(heat_csv)

    hazard_df = gdf.merge(flood_df, on='district', how='left')
    hazard_df = hazard_df.merge(heat_df, on='district', how='left')


    # # Total hazard score

    hazard_df['total_hazard'] = (
        hazard_df['combined_flood_hazard'] + 
        hazard_df['heat_hazard']
    )
    
    hazard_df = hazard_df.rename(columns={
        'rainfall_hazard': 'rain_h',
        'hand_hazard': 'hand_h',
        'combined_flood_hazard': 'flood_h',
        'heat_hazard': 'heat_h',
        'total_hazard': 'total_h'
    })


    # Optionally normalize 0–1
    max_total = hazard_df['total_h'].max()
    hazard_df['total_h'] = hazard_df['total_h'] / max_total
    cols = ['district', 'rain_h', 'hand_h', 'flood_h', 'heat_h', 'total_h', 'geometry']
    hazard_df = hazard_df[cols]

    hazard_df_nogeo = hazard_df.drop(columns='geometry')
    hazard_df_nogeo.to_csv(output_csv, index=False)
    hazard_df.to_file(output_shp)


if __name__ == "__main__":
    main()
