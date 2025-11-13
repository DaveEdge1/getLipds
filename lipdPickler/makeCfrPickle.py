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

# Save as cfr-compatible pickle
output_file = '/lipd_cfr.pkl'
with open(output_file, 'wb') as f:
    pickle.dump(df, f, protocol=4)  # Use protocol 4 for Python 3.4+ compatibility

print(f"Successfully saved cfr-compatible pickle to {output_file}")

# Also save the traditional format for backward compatibility
all_data = {}
all_data['D'] = D

traditional_file = '/lipd.pkl'
with open(traditional_file, 'wb') as f:
    pickle.dump(all_data, f, protocol=2)

print(f"Successfully saved traditional pickle to {traditional_file}")
