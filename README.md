# pcr-to-netcdf

## Objective

* Convert PCR files to NetCDF format.
* Ensure compatibility with ERA5 data (same coordinate system).
* Compare converted KNMI-LENTIS NetCDF files with ERA5 NetCDF.

### Steps

#### 1. Data Preparation
* Identify coordinate systems: Determine the coordinate system of PCR files (likely not WGS84) and the desired target system which is WGS84.
* Handle projection differences: Reproject PCR files to the target coordinate system using tools like GDAL.
* Address grid extent issues: Ensure the reprojected data has the same spatial extent as the ERA5 data. Considered providing the extent and number of cells along x and y directions.

#### 2. Conversion to NetCDF
* Choose a conversion tool: Select a suitable tool like `cdo` or Python libraries (e.g., `xarray`, `netCDF4`) based on your preferences. We chose `cdo`.
* Define metadata: Provide essential metadata for the NetCDF file, including variable names, units, and time information.
* Create NetCDF file: Generate the NetCDF file using the chosen tool, incorporating the reprojected data and metadata.

#### 3. Data Comparison
* Align datasets: Ensure both NetCDF files (ERA5 and converted PCR) share the same spatial and temporal dimensions by providing the grid information using griddles.
* Calculate metrics: Use appropriate statistical methods (e.g., correlation, difference, anomaly analysis) to compare the datasets.
* Visualize results: Create maps or plots to visualize the comparison and identify potential discrepancies.

### Challenges
* Coordinate system mismatches: Addressing differences in projection and grid extent is crucial for accurate comparison.
* Data quality: Ensure both datasets have consistent data quality and coverage for reliable comparison.
* Computational efficiency: Handling large datasets might require optimized algorithms and tools for efficient processing for example using the zip folders to store the files.

### Additional Considerations
* Data preprocessing: Consider applying necessary corrections or adjustments to the data before comparison (e.g., filling missing values, removing outliers).
* Visualization tools: Utilize tools like QGIS, Python libraries (e.g., matplotlib, cartopy), or specialized climate analysis software for effective data visualization.


By following these steps and addressing potential challenges, you can effectively convert PCR data to NetCDF format and compare it with ERA5 data for meaningful analysis.

In simple language: 
 This file converts PCR files for the ERA5 data and then converts them to NetCDF. 
 Steps:
* Define the filetype
* Select the data
* Since pcr file is in a different projection system, change it to match the NetCDF projection system that you want to compare with
* Change the reprojected PCR to the NetCDF file
* Save in a zip file to reduce the file size
* Add timestamps to the converted NetCDF file
* Combine them
