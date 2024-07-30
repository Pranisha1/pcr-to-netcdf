import xarray as xr
import numpy as np
import pandas as pd
from netCDF4 import date2num
from datetime import datetime, timedelta
import os
import sys

# Debug: Print script start
print("Starting add_time_nc_1.py script")

if len(sys.argv) != 3:
    print("Usage: python add_time_nc_1.py <file_path> <index>")
    sys.exit(1)

nc_file = sys.argv[1]
file_index = int(sys.argv[2])

# Debug: Print received arguments
print(f"Processing file: {nc_file}, Index: {file_index}")

# Define directories and paths
start_date = datetime(1991, 1, 1)
time_step = timedelta(days=1)

# Calculate the date for the current file
file_date = start_date + file_index * time_step

# Open the NetCDF file
print(f"Opening file: {nc_file}")
ds = xr.open_dataset(nc_file)
print(f"Dataset before modifications:\n{ds}")

# Rename Band1 to prec if it exists
if 'Band1' in ds:
    ds = ds.rename_vars({'Band1': 'pr'})

# Add time dimension and variable
time_num = date2num(pd.to_datetime([file_date]).to_pydatetime(), units='days since 1991-01-01', calendar='gregorian')

if 'time' not in ds.coords:
    ds = ds.expand_dims('time')
ds = ds.assign_coords(time=time_num)
ds['time'] = pd.to_datetime([file_date])

# Add time_bnds variable
start_bound = time_num[0]
end_bound = start_bound + 1  # Assuming daily data
ds['time_bnds'] = (('time', 'bnds'), [[start_bound, end_bound]])

# Create lon_bnds and lat_bnds from coordinate bounds
if 'lon' in ds.coords and 'lat' in ds.coords:
    lon_bnds = np.linspace(ds.lon.min(), ds.lon.max(), len(ds.lon) + 1)
    lat_bnds = np.linspace(ds.lat.min(), ds.lat.max(), len(ds.lat) + 1)
    ds['lon_bnds'] = (('lon', 'bnds'), np.column_stack([lon_bnds[:-1], lon_bnds[1:]]))
    ds['lat_bnds'] = (('lat', 'bnds'), np.column_stack([lat_bnds[:-1], lat_bnds[1:]]))

# Debug: Print dataset after modifications
print(f"Dataset after modifications:\n{ds}")

# Save the modified dataset
try:
    ds.to_netcdf(nc_file, mode='w')  # Use 'w' mode to overwrite the file
    ds.close()
    print(f"Successfully saved modifications to: {nc_file}")
except Exception as e:
    print(f"Error saving file {nc_file}: {e}")

# Debug: Confirm file modification
print(f"Finished processing file: {nc_file}")
