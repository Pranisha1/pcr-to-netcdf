import os
import xarray as xr
import numpy as np
import pandas as pd
from netCDF4 import date2num
from datetime import datetime, timedelta

# Define directories and paths
output_dir = '/scratch/depfg/pokhr002/SPHY3.0/input/netcdf_forcing'
start_date = datetime(1991, 1, 1)
time_step = timedelta(days=1)

# List of NetCDF files to process
nc_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('_r.nc')]

# Process each file in the output directory
for i, nc_file in enumerate(nc_files):
    # Open the NetCDF file
    ds = xr.open_dataset(nc_file)
    
    # Rename Band1 to prec
    if 'Band1' in ds:
        ds = ds.rename_vars({'Band1': 'prec'})    
    
    # Add time dimension and variable
    file_date = start_date + i * time_step
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
    
    # Save the modified dataset
    ds.to_netcdf(nc_file)
    ds.close()

print("All files have been processed and attributes added.")
print("Done!")
