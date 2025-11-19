# getLipds

This repository provides tools to download and convert LiPD (Linked Paleo Data) files from the LiPDverse into various formats suitable for different analysis frameworks.

## Components

### downloadLipds.js
Main script that downloads LiPD data and converts it to the requested format.

**Usage:**
```bash
node downloadLipds.js <uniqueID> <language> [format]
```

**Parameters:**
- `uniqueID`: Unique identifier for the data request
- `language`: Output language (`R` or `Python`)
- `format`: (Optional) Output pickle format, defaults to `legacy`
  - `legacy`: Traditional dictionary-based pickle (backward compatible)
  - `cfr`: pandas DataFrame format compatible with [cfr](https://github.com/fzhu2e/cfr) library

**Examples:**
```bash
# Legacy format (default)
node downloadLipds.js myRequest123 Python

# CFR-compatible format
node downloadLipds.js myRequest123 Python cfr

# R format
node downloadLipds.js myRequest123 R
```

### getLipd.R
R script that queries the LiPDverse and extracts time series data.

### lipdPickler/
Python scripts and Docker container for converting LiPD files to pickle format.

## Output Files

Depending on the parameters, the following files are generated in `/root/presto/userRecons/<uniqueID>/`:

### For Python (`language=Python`):
- **Legacy format** (`format=legacy` or unspecified):
  - `lipd.pkl` - Dictionary with structure `{'D': D}`
  - `lipd_files.zip` - Archive of all .lpd files
  - `lipd.rds` - R serialized data
  - `lipd_tts.rds` - R time series table

- **CFR format** (`format=cfr`):
  - `lipd_cfr.pkl` - pandas DataFrame compatible with cfr library
  - `lipd.pkl` - Legacy format (for backward compatibility)
  - `lipd_files.zip` - Archive of all .lpd files
  - `lipd.rds` - R serialized data
  - `lipd_tts.rds` - R time series table

### For R (`language=R`):
- `lipd.RData` - R data file
- `lipd.rds` - R serialized data
- `lipd_tts.rds` - R time series table

## CFR Format Details

The CFR-compatible format is designed for use with the [cfr (Climate Field Reconstruction)](https://github.com/fzhu2e/cfr) Python package.

**Structure:** pandas DataFrame with the following columns:
- `paleoData_TSid` - Time series unique identifier
- `dataSetName` - Dataset/site name
- `archiveType` - Archive type (marine sediment, tree, ice core, etc.)
- `geo_meanLat` - Latitude
- `geo_meanLon` - Longitude
- `geo_meanElev` - Elevation
- `year` or `age` - Time axis values
- `yearUnits` - Time units
- `paleoData_variableName` - Variable name
- `paleoData_units` - Measurement units
- `paleoData_values` - Actual proxy values
- `paleoData_proxy` - Proxy type

**Loading in cfr:**
```python
import cfr
import pandas as pd

# Load the pickle file
df = pd.read_pickle('lipd_cfr.pkl')

# Create ProxyDatabase from DataFrame
pdb = cfr.ProxyDatabase.from_df(
    df,
    pid_column='paleoData_TSid',
    lat_column='geo_meanLat',
    lon_column='geo_meanLon'
)

print(f"Loaded {len(pdb)} proxy records")
```

## Requirements

- Node.js
- R with lipdR and jsonlite packages
- Docker (for pickle conversion)
- Docker image: `davidedge/lipd_webapps:lipdPickler`

## Related Projects

- [pylipd](https://github.com/LinkedEarth/pylipd) - Modern Python library for LiPD data (RDF-based)
- [cfr](https://github.com/fzhu2e/cfr) - Climate Field Reconstruction toolkit
- [LiPDverse](https://lipdverse.org/) - LiPD data repository
