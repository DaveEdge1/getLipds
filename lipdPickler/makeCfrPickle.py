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

# Group by dataset to identify problematic datasets
dataset_col = 'dataSetName' if 'dataSetName' in df.columns else 'datasetId'

if dataset_col in df.columns:
    # Identify datasets missing proxy type or archive type
    # Only check non-auxiliary variables (age/year/depth are expected to lack proxy type)
    datasets_missing_proxy = set()
    datasets_missing_archive = set()

    if 'paleoData_proxy' in df.columns and 'paleoData_variableName' in df.columns:
        # Find datasets where ALL non-auxiliary measurements lack proxy type
        for dataset in df[dataset_col].unique():
            dataset_records = df[df[dataset_col] == dataset].copy()
            # Filter to only proxy variables (not age/year/depth)
            auxiliary_vars = ['age', 'year', 'depth']
            proxy_records = dataset_records[~dataset_records['paleoData_variableName'].isin(auxiliary_vars)]
            if len(proxy_records) > 0 and proxy_records['paleoData_proxy'].isna().all():
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
        print(f"\nDatasets being dropped:")
        for ds in sorted(datasets_to_drop):
            print(f"  - {ds}")
        df = df[~df[dataset_col].isin(datasets_to_drop)].copy()
        print(f"\nRemaining: {len(df)} time series from {df[dataset_col].nunique()} datasets")

# Fill missing proxy/archive types from other records in the same dataset
# (Sometimes one time series in a dataset has the info, others don't)
if dataset_col in df.columns:
    for col in ['paleoData_proxy', 'archiveType']:
        if col in df.columns:
            # Forward fill within each dataset group
            df[col] = df.groupby(dataset_col)[col].transform(lambda x: x.ffill().bfill())

# Handle paleoData_pages2kID at the DATASET level (not individual time series)
# One unique ID per dataset, not per time series
if dataset_col in df.columns:
    if 'paleoData_pages2kID' in df.columns:
        # Get one pages2kID per dataset (using the first non-null value from each dataset)
        dataset_pages2k_map = df.groupby(dataset_col)['paleoData_pages2kID'].first()
        missing_datasets = dataset_pages2k_map[dataset_pages2k_map.isna()].index

        if len(missing_datasets) > 0:
            print(f"\nFound {len(missing_datasets)} datasets missing paleoData_pages2kID, creating fallback IDs")
            # Try to use datasetId or TSid pattern for fallback
            if 'datasetId' in df.columns:
                for dataset_name in missing_datasets:
                    dataset_id = df[df[dataset_col] == dataset_name]['datasetId'].iloc[0]
                    dataset_pages2k_map[dataset_name] = dataset_id
            elif 'paleoData_TSid' in df.columns:
                # Use first TSid from each dataset
                for dataset_name in missing_datasets:
                    tsid = df[df[dataset_col] == dataset_name]['paleoData_TSid'].iloc[0]
                    dataset_pages2k_map[dataset_name] = tsid
            else:
                # Create sequential IDs
                for i, dataset_name in enumerate(missing_datasets):
                    dataset_pages2k_map[dataset_name] = f'unknown_{i}'

        # Map the dataset-level IDs back to all time series
        df['paleoData_pages2kID'] = df[dataset_col].map(dataset_pages2k_map)
    else:
        # Column doesn't exist, create it at dataset level
        print("\npaleoData_pages2kID column missing, creating from datasetId or dataSetName")
        if 'datasetId' in df.columns:
            # Use datasetId as the pages2kID
            dataset_id_map = df.groupby(dataset_col)['datasetId'].first()
            df['paleoData_pages2kID'] = df[dataset_col].map(dataset_id_map)
        else:
            # Use dataset name as the ID
            df['paleoData_pages2kID'] = df[dataset_col]

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
