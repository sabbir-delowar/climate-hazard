# Bangladesh Climate Hazard Automation Pipeline

This repository contains an automated pipeline for climate hazard mapping at the district level in Bangladesh. The workflow includes downloading, processing, and integrating multiple open-source environmental datasets to generate reproducible flood and heat hazard scores for all 64 districts.

**All data downloads and processing are fully automated—the only user input required is to provide the Area of Interest (AOI) shapefile with an attribute named "name" (string, 100). Once the AOI is supplied, the pipeline runs end-to-end with no manual intervention.**

**All hazard scores are calculated on a *****relative***** basis:**\
Each score (rainfall, flood, heat, etc.) is normalised (min-max or percentile) across all districts, so hazard values represent *relative risk compared to other districts in the same run for data from  2020–2024*. These are *not* absolute risk values.

---

## Methodology Summary

- **Rainfall Hazard**: For each district, the number of months with rainfall above the 95th percentile (across all districts/years) is counted. Scores are then normalised (min-max) across districts.
- **HAND (Height Above Nearest Drainage) Hazard**: The proportion of each district’s area with HAND below a set threshold is used, then normalised (min-max) across districts. This represents low-elevation, flood-prone terrain.
- **Flood Hazard (Combined)**: Rainfall hazard and HAND hazard are combined using a weighted average (no additional scaling is applied at this stage).
- **Heat Hazard**: For each district, the number of days with daily max temperature above the 95th percentile is counted, then normalised (min-max) across districts.
- **Combined Hazard**: The flood and heat hazard scores are simply summed (not weighted) to produce the final combined hazard score. This total is then normalised across districts for comparison.

> *All outputs represent relative hazard within the AOI—higher scores mean higher hazard compared to other districts in your analysis, not compared to a fixed physical scale.*

---

## Project Overview

- Fully automated, script-based workflow (run with `python main.py`)
- Download and process:
  - **ERA5 Rainfall** (monthly means, 2020–2024)
  - **ESA FABDEM DEM** (for HAND/flood risk)
  - **ERA5 Daily Maximum Temperature** (heat hazard, 2020–2024)
- Zonal statistics and hazard scoring for each district (using shapefiles)
- Outputs reproducible CSVs and maps in the `/results` directory

---

## Data Sources

- **ERA5 (Rainfall & Temperature):** [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
- **ESA FABDEM:** [Forest And Buildings removed Copernicus DEM](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Forest_and_buildings_removed_from_Copernicus_DEM)
- **District shapefiles:** Bangladesh official boundaries or any user-supplied AOI

---

## Folder Structure

```
climate-hazard/
├── data/
│   ├── aoi/                # Bangladesh district shapefiles (user AOI goes here)
│   └──  interim/           # Intermediate data
│         ├── hand/         # Downloaded and processed hand data
│         ├── heat/     ``` # Downloaded and processed heat data
│         └── febdem/       # Downloaded and processed DEM tiles
├── scripts/                # All pipeline Python scripts
├── results/                # Output CSVs, shapefiles, hazard maps
├── main.py                 # Pipeline runner
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- See `requirements.txt` for package list
- CDS API key configured (see [CDS API docs](https://cds.climate.copernicus.eu/how-to-api))

### Setup

```bash
# Clone the repository
$ git clone https://github.com/your-username/climate-hazard.git
$ cd climate-hazard

# Install dependencies
$ pip install -r requirements.txt

# Set up CDS API credentials (~/.cdsapirc)

# Place your AOI shapefile in data/aoi/
```

---

## Pipeline Usage

Run the entire pipeline with:

```bash
python main.py
```

This will execute all scripts in order and generate results in `/results`.

Or run scripts individually, e.g.:

```bash
python scripts/2.2-create-hand.py
```

---

## Pipeline Scripts & Steps

- **1.1-download-era5.py**: Download ERA5 monthly rainfall for AOI
- **1.2-compute-heavy-rain-months.py**: Aggregate rainfall to districts, score hazard
- **2.1-download-fabdem-tiles.py**: Identify and download FABDEM tiles intersecting AOI
- **2.2-create-hand.py**: Mosaic, clip, and align DEM
- **2.3-compute-hand.py**: Generate HAND raster (breached depressions)
- **2.4-classify-flood-prone.py**: Classify flood-prone areas, calculate HAND hazard per district
- **3.1-combine-rainfall-hand-hazard.py**: Combine rainfall and HAND scores for flood hazard (weighted average)
- **4.1-download-era5-data.py**: Download ERA5 daily max temperature
- **4.2-compute-heatwave-days.py**: Compute district heatwave days, score heat hazard
- **99-combine-hazards.py**: Combine all hazards by summing, then normalise for final score

---

## Outputs

- CSVs: Hazard scores for all districts (relative/normalised)
- Shapefile: Districts with appended hazard attributes

---

## Notes

- All processing is reproducible and non-interactive once AOI is provided.
- Hazard scores are *relative* and should not be interpreted as absolute risk.
- Some datasets are large and **excluded from version control** (see `.gitignore`)
- To add new hazards, write a script and add to `main.py`
- The pipeline is modular—scripts can be run/modified individually

---

## License

MIT License. Attribution required if reusing workflow or scripts.


