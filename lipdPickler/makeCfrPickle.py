import lipd
import pickle
import pandas as pd
import os

print("Starting cfr-compatible pickle creation")
print(os.getcwd())
print(os.path.isfile('/lipd.pkl'))

# Read LiPD files
D = lipd.readLipd("/output/")

# Extract time series objects
TS = lipd.extractTs(D)
print(f"Extracted {len(TS)} time series objects")

# Convert TSO list to DataFrame
# Each TSO is a flattened dictionary with all metadata
df = pd.DataFrame(TS)

print(f"Created DataFrame with shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Remove records with missing critical metadata that cfr requires
initial_count = len(df)

# Drop records missing proxy type - this is critical for cfr
if 'paleoData_proxy' in df.columns:
    df = df.dropna(subset=['paleoData_proxy'])
    print(f"Dropped {initial_count - len(df)} records with missing paleoData_proxy")

# Drop records missing archive type - also critical
if 'archiveType' in df.columns:
    df = df.dropna(subset=['archiveType'])
    print(f"Total dropped after archiveType filter: {initial_count - len(df)} records")

# Ensure remaining string columns are proper strings
string_columns = [
    'paleoData_proxy', 'archiveType', 'dataSetName',
    'paleoData_variableName', 'paleoData_units', 'yearUnits'
]

for col in string_columns:
    if col in df.columns:
        # Fill any remaining NaN with 'unknown' for non-critical columns
        if col not in ['paleoData_proxy', 'archiveType']:
            df[col] = df[col].fillna('unknown')
        # Ensure they're strings
        df[col] = df[col].astype(str)

# Handle numeric columns
numeric_columns = ['geo_meanLat', 'geo_meanLon', 'geo_meanElev']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"Final DataFrame shape: {df.shape}")
print(f"Removed {initial_count - len(df)} total records due to missing critical metadata")
print(f"Data types:\n{df.dtypes}")

# Save as cfr-compatible pickle
output_file = '/output/lipd_cfr.pkl'
with open(output_file, 'wb') as f:
    pickle.dump(df, f, protocol=4)  # Use protocol 4 for Python 3.4+ compatibility

print(f"Successfully saved cfr-compatible pickle to {output_file}")

# Also save the traditional format for backward compatibility
all_data = {}
all_data['D'] = D

traditional_file = '/output/lipd.pkl'
with open(traditional_file, 'wb') as f:
    pickle.dump(all_data, f, protocol=2)

print(f"Successfully saved traditional pickle to {traditional_file}")
