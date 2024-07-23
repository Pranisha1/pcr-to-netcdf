# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 15:13:12 2024

@author: Pokhr002
"""

import xarray as xr
import matplotlib.pyplot as plt


# Define the date range
start_date = '1991-01-01'
end_date = '1991-01-05'

# Open the NetCDF files
file1 = 'pr_r01_1990-2029_him.nc'
file2 = 'pr_1991-2022_KB.nc'

# Load the datasets
ds1 = xr.open_dataset(file1)
ds2 = xr.open_dataset(file2)
print (ds2)
ds_val = ds2['pr'].values
print(ds_val)

# Define the grid cell location (latitude and longitude)
lat = 29
lon = 82

# Select the nearest grid cell to the specified latitude and longitude
da1_point = ds1['pr'].sel(lat=lat, lon=lon, method='nearest')
da2_point = ds2['pr'].sel(lat=lat, lon=lon, method='nearest')

# Select the data for the specified date range
da1_selected = da1_point.sel(time=slice(start_date, end_date))
da2_selected = da2_point.sel(time=slice(start_date, end_date))

# Calculate the mean precipitation over the selected dates
mean_precip_ds1 = da1_selected.mean(dim='time').values
mean_precip_ds2 = da2_selected.mean(dim='time').values

# Convert to pandas dataframe for easier plotting
df1 = da1_selected.to_dataframe().reset_index()
df2 = da2_selected.to_dataframe().reset_index()

# Plotting
plt.figure(figsize=(10, 6))

plt.plot(df1['time'], df1['pr'], label='Dataset 1', marker='o')
plt.plot(df2['time'], df2['pr'], label='Dataset 2', marker='s')

# Adding the average lines
plt.axhline(mean_precip_ds1, color='blue', linestyle='--', label=f'Dataset 1 Mean: {mean_precip_ds1:.2f}')
plt.axhline(mean_precip_ds2, color='orange', linestyle='--', label=f'Dataset 2 Mean: {mean_precip_ds2:.2f}')

# Customize the plot
plt.title('Precipitation from 1991-01-01 to 1991-01-05')
plt.xlabel('Date')
plt.ylabel('Precipitation (mm)')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
