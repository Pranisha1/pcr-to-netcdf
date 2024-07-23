# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 12:44:01 2024

@author: Pokhr002


THIS CODE IS TO READ THE FORCING FILES IN PCRASTER FORMAT CHANGE THEM TO NETCDF WHILE
ADDING THE TIME ATTRIBUTE AND THEN COMBINE THEM TO ONE NETCDF FILE

"""

import pandas as pd
import os
import xarray as xr
import numpy as np
import dask
import subprocess
from netCDF4 import date2num
from datetime import datetime, timedelta


dir_forcing = 'C:/SPHY_input/forcing/'
input_dir = 'C:/Users/pokhr002/OneDrive - Universiteit Utrecht/06Programming/01Python/07_Lentis/input_data/'
output_dir = 'C:/Users/pokhr002/OneDrive - Universiteit Utrecht/06Programming/01Python/07_Lentis/output_data/'
#%% 

# Define the desired date range
start_date = pd.to_datetime("1991-01-01")
end_date = pd.to_datetime("1991-01-10")

dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Generate the filenames in the specified format
filenames = []
for i in range(12):
    for j in range(1, 1001):
        if j < 1000:
            filenames.append(f'{i:04d}.{j:03d}')
        else:
            i += 1
            filenames.append(f'{i:04d}.000')
            

# Combine dates and filenames as per the length of dates
combined_data = list(zip(dates, filenames[:len(dates)]))

# Create a DataFrame from the combined data
df = pd.DataFrame(combined_data, columns=['Dates', 'Filenames'])

# Filter the DataFrame for the desired date range
df_filtered = df[(df['Dates'] >= start_date) & (df['Dates'] <= end_date)]


#%% 
############################################ To change the pcraster file to netcdf ##################################################################

# Mention the parameter that you want to extract from the files
prefixes = ["prec"] #["tmax", "tmin", "tavg"]


# List to store file paths
file_paths = []


for prefix in prefixes:
    for index, row in df_filtered.iterrows():
        # Constructing the filename pattern
        filename_pattern = prefix + row["Filenames"]
        # Check if the file exists in the dir_forcing directory
        source_file = os.path.join(dir_forcing, filename_pattern)
        if os.path.exists(source_file):
            file_paths.append((source_file, row["Dates"]))
        else:
            print(f"File {filename_pattern} not found in {dir_forcing}")   
            
            
# Convert to NetCDF and add attributes 
nc_files = []
for i, (file_path, file_date) in enumerate(file_paths):
    ncd_file = os.path.join(output_dir, f"{prefix}_{i+1:05d}.nc")
    command = f'gdal_translate -of NetCDF "{file_path}" "{ncd_file}"'
    print(command)  # For debugging: print the command to see if it's formatted correctly
    os.system(command)
    ds = xr.open_dataset(ncd_file)
    
    # Rename Band1 to prec
    ds = ds.rename_vars({"Band1": "pr"})   
    print(f'Converted {file_path} to {ncd_file}')
    
    # Add time dimension to the netcdf dataset
    if 'time' not in ds:
        ds = ds.expand_dims('time')
        ds['time'] = pd.to_datetime([file_date])
    
    # Add time_bnds variable to the netcdf dataset
    start_bound = date2num(pd.to_datetime(file_date).to_pydatetime(), units='days since 1991-01-01', calendar='gregorian')
    end_bound = start_bound + 1  # Assuming daily data
    ds['time_bnds'] = (('time', 'bnds'), [[start_bound, end_bound]])
    
    # Create long_bnds and lat_bnds from coordinate bounds
    if 'lon' in ds.coords and 'lat' in ds.coords:
        lon_bnds = np.linspace(ds.lon.min(), ds.lon.max(), len(ds.lon) + 1)
        lat_bnds = np.linspace(ds.lat.min(), ds.lat.max(), len(ds.lat) + 1)
        ds['lon_bnds'] = (('lon', 'bnds'), np.column_stack([lon_bnds[:-1], lon_bnds[1:]]))
        ds['lat_bnds'] = (('lat', 'bnds'), np.column_stack([lat_bnds[:-1], lat_bnds[1:]]))
    
    # Save the dataset
    ds.to_netcdf(ncd_file)
    print(ds)
    ds.close()
    
    nc_files.append(ncd_file)

print('All files have been converted and attributes added.')
print("Done!") 

#%% 
ds = xr.open_dataset('C:/Users/pokhr002/OneDrive - Universiteit Utrecht/06Programming/01Python/07_Lentis/output_data/prec_00006.nc')
print (ds)
  

ds8 = xr.open_dataset('C:/Users/pokhr002/OneDrive - Universiteit Utrecht/06Programming/01Python/07_Lentis/scr/pr_r01_1990-2029_him.nc')
print (ds8)
   

