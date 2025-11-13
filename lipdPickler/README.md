# lipdPickler

* This repo underlies the lipdPickler container (docker pull davidedge/lipd_webapps:lipdPickler)

* The container requires a directory mounted with .lpd files to pickle

* The output requires a volume mount to receive the pickle file(s)

## Formats Supported

### Legacy Format (default)
- **Script**: `makePickle.py`
- **Output**: `lipd.pkl`
- **Structure**: Dictionary with `{'D': D}` where D is from `lipd.readLipd()`
- **Protocol**: pickle protocol 2 (Python 2.x compatible)
- **Usage**: `docker run -v /path/to/output:/output -v /path/to/output/lipd.pkl:/lipd.pkl davidedge/lipd_webapps:lipdPickler`

### CFR Format (cfr-compatible)
- **Script**: `makeCfrPickle.py`
- **Output**: `lipd_cfr.pkl` (also creates `lipd.pkl` for backward compatibility)
- **Structure**: pandas DataFrame with columns compatible with [cfr](https://github.com/fzhu2e/cfr) library
- **Protocol**: pickle protocol 4 (Python 3.4+)
- **Columns**: paleoData_TSid, dataSetName, archiveType, geo_meanLat, geo_meanLon, geo_meanElev, year/age, yearUnits, paleoData_variableName, paleoData_units, paleoData_values, paleoData_proxy
- **Usage**: `docker run -v /path/to/output:/output -v /path/to/output/lipd_cfr.pkl:/lipd_cfr.pkl davidedge/lipd_webapps:lipdPickler makeCfrPickle.py`

## Examples

### Legacy format (backward compatible):
```bash
docker run -v /root/query-container/output:/output -v /root/lipdPy/lipd.pkl:/lipd.pkl davidedge/lipd_webapps:lipdPickler
```

### CFR format:
```bash
docker run -v /root/query-container/output:/output -v /root/query-container/output/lipd_cfr.pkl:/lipd_cfr.pkl davidedge/lipd_webapps:lipdPickler makeCfrPickle.py
```
