# pcr-to-netcdf
 This file converts pcr files for the ERA5 data and then converts them to NetCDF. I will then compare two NetCDF (ERA5 and KNMI-LENTIS)








### Errors encountered:
* First, the coordinate system between the LENTIS and ERA5 data is not the same. The ERA5 data is in WGS 84 / UTM zone 44N EPSG:32644 and LENTIS in EPSG:4326
* Second, when translating the grid extension of the file in WGS84 is changed to a larger extent thus NAN values are introduced in the cells. I tried copying the extent and defining the grids across the x and y axis but it didn't work. 
