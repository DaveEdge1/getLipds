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

initial_count = len(df)

# Filter to only proxy measurements (exclude age/year/depth columns)
# These auxiliary columns won't have proxy types, but that's expected
if 'paleoData_variableName' in df.columns:
    # Keep only records that are NOT age/year/depth measurements
    auxiliary_vars = ['age', 'year', 'depth']
    is_proxy = ~df['paleoData_variableName'].isin(auxiliary_vars)
    df = df[is_proxy].copy()
    print(f"Filtered to proxy measurements only: kept {len(df)} of {initial_count} time series")
    print(f"(Removed {initial_count - len(df)} auxiliary time series like age/year/depth)")

# Now check for datasets with missing critical metadata
# Group by dataset to identify problematic datasets
dataset_col = 'dataSetName' if 'dataSetName' in df.columns else 'datasetId'

if dataset_col in df.columns:
    # Identify datasets missing proxy type or archive type
    datasets_missing_proxy = set()
    datasets_missing_archive = set()

    if 'paleoData_proxy' in df.columns:
        # Find datasets where ALL proxy measurements lack proxy type
        for dataset in df[dataset_col].unique():
            dataset_records = df[df[dataset_col] == dataset]
            if dataset_records['paleoData_proxy'].isna().all():
                datasets_missing_proxy.add(dataset)

    if 'archiveType' in df.columns:
        # Find datasets where ALL records lack archive type
        for dataset in df[dataset_col].unique():
            dataset_records = df[df[dataset_col] == dataset]
            if dataset_records['archiveType'].isna().all():
                datasets_missing_archive.add(dataset)

    # Drop entire datasets that lack critical metadata
    datasets_to_drop = datasets_missing_proxy | datasets_missing_archive

    if datasets_to_drop:
        print(f"\nDropping {len(datasets_to_drop)} datasets due to missing critical metadata:")
        print(f"  - {len(datasets_missing_proxy)} datasets missing proxy type")
        print(f"  - {len(datasets_missing_archive)} datasets missing archive type")
        df = df[~df[dataset_col].isin(datasets_to_drop)].copy()
        print(f"Remaining: {len(df)} time series from {df[dataset_col].nunique()} datasets")

# Fill missing proxy/archive types from other records in the same dataset
# (Sometimes one time series in a dataset has the info, others don't)
if dataset_col in df.columns:
    for col in ['paleoData_proxy', 'archiveType']:
        if col in df.columns:
            # Forward fill within each dataset group
            df[col] = df.groupby(dataset_col)[col].transform(lambda x: x.ffill().bfill())

# Handle paleoData_pages2kID - fill with unique identifier if missing
# Not all datasets are from PAGES2k, so we create a fallback ID
if 'paleoData_pages2kID' in df.columns:
    missing_id_count = df['paleoData_pages2kID'].isna().sum()
    if missing_id_count > 0:
        print(f"\nFound {missing_id_count} records missing paleoData_pages2kID, creating fallback IDs")
        # Use paleoData_TSid or create unique identifier for records without PAGES2k ID
        if 'paleoData_TSid' in df.columns:
            df['paleoData_pages2kID'] = df['paleoData_pages2kID'].fillna(df['paleoData_TSid'])
        else:
            # Create sequential IDs if TSid also missing
            mask = df['paleoData_pages2kID'].isna()
            df.loc[mask, 'paleoData_pages2kID'] = ['unknown_' + str(i) for i in range(mask.sum())]
else:
    # Column doesn't exist, create it from TSid or sequential IDs
    print("\npaleoData_pages2kID column missing, creating from paleoData_TSid")
    if 'paleoData_TSid' in df.columns:
        df['paleoData_pages2kID'] = df['paleoData_TSid']
    else:
        df['paleoData_pages2kID'] = ['unknown_' + str(i) for i in range(len(df))]

# Ensure remaining string columns are proper strings
string_columns = [
    'paleoData_proxy', 'archiveType', 'dataSetName',
    'paleoData_variableName', 'paleoData_units', 'yearUnits',
    'paleoData_pages2kID'
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

print(f"\nFinal DataFrame shape: {df.shape}")
print(f"Total removed: {initial_count - len(df)} time series")
print(f"Final datasets: {df[dataset_col].nunique() if dataset_col in df.columns else 'unknown'}")
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
