def main():
    
    import os
    from whitebox.whitebox_tools import WhiteboxTools
    import rasterio
    import matplotlib.pyplot as plt

    # # Define Paths


    input_dem = "hand-dem.tif"
    output_dir = "data/interim/hand"
    os.makedirs(output_dir, exist_ok=True)
    
    old_dir = os.getcwd()

    breached_dem = "hand_breached.tif"
    flow_dir = "hand_flowdir.tif"
    flow_acc = "hand_flowacc.tif"
    streams = "hand_streams.tif"
    hand_output = "hand.tif"


    # # Initialise WhiteboxTools

    wbt = WhiteboxTools()
    wbt.verbose = False


    # # Breach Depressions

    print("✅ Breaching depressions in DEM...")
    wbt.set_working_dir(output_dir)
    wbt.breach_depressions(input_dem, breached_dem)


    # # D8 Flow Direction

    print("✅ Calculating D8 Flow Direction...")
    wbt.d8_pointer(
        dem=breached_dem,
        output=flow_dir
    )


    # # Flow Accumulation

    print("✅ Calculating Flow Accumulation...")
    wbt.d8_flow_accumulation(
        i=breached_dem,
        output=flow_acc,
        out_type='cells'
    )


    # # Extract Streams

    threshold = 5000
    print(f"✅ Extracting streams with threshold: {threshold}")
    wbt.extract_streams(
        flow_accum=flow_acc,
        output=streams,
        threshold=threshold
    )


    # # Compute HAND

    print("✅ Computing HAND...")
    wbt.elevation_above_stream(
        dem=breached_dem,
        streams=streams,
        output=hand_output
    )
    wbt.set_working_dir(old_dir) 

if __name__ == "__main__":
    main()
