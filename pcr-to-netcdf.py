# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 12:44:01 2024

@author: Pokhr002


THIS CODE IS TO READ THE FORCING FILES IN PCRASTER FORMAT CHANGE THEM TO NETCDF WHILE
ADDING THE TIME ATTRIBUTE AND THEN COMBINE THEM TO ONE NETCDF FILE

"""


import os
import zipfile
import numpy as np
import pandas as pd
import xarray as xr
import rasterio
import fiona
from shapely.geometry import shape, box


base_dir = os.getcwd()
dir_forcing = os.path.join(base_dir, 'input_data', 'forcing')
input_dir = os.path.join(base_dir, 'input_data')
output_dir = os.path.join(base_dir,  'output_data')
vector_file = os.path.join(input_dir, 'Extent_WGS84.shp')  # to provide the boundary of the map
zip_filename = os.path.join(output_dir, "nc_files.zip")

#%% 

# Define the desired date range
start_date = pd.to_datetime("1991-01-01")
end_date = pd.to_datetime("1991-01-5")

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

# create the zip file as sepecified name
zip_file = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) 

# Function to get the corner coordinates from a vector file
def get_vector_corners(vector_file):
    with fiona.open(vector_file, 'r') as src:
        bounds = src.bounds
        top_left = (bounds[0], bounds[3])
        top_right = (bounds[2], bounds[3])
        bottom_left = (bounds[0], bounds[1])
        bottom_right = (bounds[2], bounds[1])
    return top_left, top_right, bottom_left, bottom_right


# Get the extent from the vector file
top_left, top_right, bottom_left, bottom_right = get_vector_corners(vector_file)
# Set extent using the corner coordinates
extent = [bottom_left[0], bottom_left[1], top_right[0], top_right[1]]

# Desired number of cells in x and y directions for the projected raster file
num_x_cells = 625
num_y_cells = 555


# List to store file paths
file_paths = []


#Check if the raster file exists
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
            
            
# Convert the pcr file to NetCDF 
nc_files = []
for i, (file_path, file_date) in enumerate(file_paths):
    
    # Check for NaN values in the .tif file
    with rasterio.open(file_path) as src:
        data = src.read(1)
        if np.isnan(data).any():
            print(f"NaN values found in {file_path}")
        else:
            print(f"No NaN values in {file_path}")
        
        # Display the values (optional, can be large for big files)
        print("Data values:", data)
    
    
    # As pcr file is in projected system use GDAL command to reproject the data
    reprojected_file = os.path.join(output_dir, f"{prefix}_{i+1:05d}_r.tif" )    
    reproject_command = (
       f'gdalwarp -s_srs EPSG:32644 -t_srs EPSG:4326 -te {extent[0]} {extent[1]} {extent[2]} {extent[3]} -ts {num_x_cells} {num_y_cells} -of GTiff -dstnodata -999999 "{file_path}" "{reprojected_file}"'
               )    
    print("\n\033[1m\033[34m" + "---"+ reproject_command + "\033[0m\n\n")   # For debugging
    os.system(reproject_command) 
    
    
    # Check for NaN values in the .tif file
    with rasterio.open(reprojected_file) as src:
        data = src.read(1)
        no_data_value = -999999
        
        if np.isnan(data).any():
            print(f"\n\033[1m\033[31mNaN values found in {reprojected_file}\033[0m\n\n")
        else:
            print(f"\n\033[1m\033[31mNo NaN values in {reprojected_file}\033[0m\n\n")
        
        # Count the number of no data cells
        no_data_count = np.sum(data == no_data_value)
        print(f"Number of cells with no data value ({no_data_value}): {no_data_count}")
        
        # Display the values (optional, can be large for big files)
        print("Data values:", data)
    
       
    # Then convert the reprojected file to NetCDF format
    ncd_file = os.path.join(output_dir, f"{prefix}_{i+1:05d}.nc")
    command = f'gdal_translate -of NetCDF "{reprojected_file}" "{ncd_file}"'
    print("\n\033[1m\033[34m" + "---" + command + "\033[0m\n")  # For debugging: print the command to see if it's formatted correctly
    os.system(command)    
    
    
    # Open the NetCDF file and check for NaN values
    ds = xr.open_dataset(ncd_file)
    if np.isnan(ds['Band1'].values).any():
        print(f"\n\033[1m\033[31mNaN values found in NetCDF file before remapping: {ncd_file}\033[0m")
    else:
        print("\n\033[1m\033[31mNaN value not found\033[0m") # printing in bold red  
    
    # Get the values and print them to check 
    ds_val = ds['Band1'].values    
    print(ds)
    print("Printing values of the Band1")
    print(ds_val)  
    
    # Close the dataset       
    ds.close()
    
    nc_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.nc')]
    
    # Add the NetCDF file to the zip archive
    zip_file.write(ncd_file, os.path.basename(ncd_file))
        
    # Delete the reprojected file
    os.remove(reprojected_file)
    os.remove(ncd_file)
        
zip_file.close()   
 
#..............................................................................   
print(f"\n\033[1m\033[32mConverted {file_path} to {ncd_file}\033[0m") # printing in bold green 
    
     

#%% 
ds_1 = xr.open_dataset('C:/Users/pokhr002/OneDrive - Universiteit Utrecht/06Programming/01Python/07_Lentis/output_data/prec_00001_r.nc')
print (ds_1)
ds_val_1 = ds_1['Band1'].values    
print(ds_val_1)
  

ds8 = xr.open_dataset('C:/Users/pokhr002/OneDrive - Universiteit Utrecht/06Programming/01Python/07_Lentis/scr/pr_r01_1990-2029_him.nc')
print (ds8)

# Close the dataset
ds8.close()
   

