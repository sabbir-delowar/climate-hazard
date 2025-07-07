def main():
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    # # Define Paths

    rainfall_csv = "results/individual-hazards/rainfall-hazard.csv"
    hand_csv = "results/individual-hazards/hand-hazard.csv"

    output_dir = "results/individual-hazards"
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, "combined-flood-hazard.csv")


    # # Compute combined hazard

    rainfall_df = pd.read_csv(rainfall_csv)
    hand_df = pd.read_csv(hand_csv)

    combined_df = pd.merge(
        rainfall_df,
        hand_df,
        on='district',
        how='inner'
    )

    combined_df['combined_flood_hazard'] = (
        0.5 * combined_df['rainfall_hazard'] + 0.5 * combined_df['hand_hazard']
    )

    combined_df['combined_flood_hazard'] = combined_df['combined_flood_hazard'].clip(0, 1)

    combined_df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()