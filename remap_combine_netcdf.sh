#!/bin/bash

# Define directories
initdir=$(pwd) # Get current directory path
inputroot="${initdir}/input_data"
outroot="${initdir}/output_data"
zip_filename="${outroot}/nc_files.zip"
target_grid="${initdir}/input_data/target_grid.txt"

# Python file to convert from PCR to NetCDF
#python3 /scratch/depfg/pokhr002/SPHY3.0/input/netcdf_forcing/pcr-to-netcdf.py  

echo -e "\e[34;43mLET'S GET ALL THE .NC FILES REMAPPED TO TARGET GRID AND ADD THE TIMESTAMPS TO ALL THE .NC FILES\e[0m"

# Create a temporary directory for remapped files
remapped_tmpdir=$(mktemp -d)
tmproot=$(mktemp -d)

# Get the list of files inside the zip archive using unzip
file_list=$(unzip -Z1 "$zip_filename")

# Initialize file index
file_index=0

# Loop through each file in the zip archive
for filename in $file_list; do
    # Extract the current file to the temporary directory
    unzip -j "$zip_filename" "$filename" -d "$tmproot"

    # Define the input file path
    input_file="$tmproot/$filename"

    # Check if the file was extracted successfully
    if [ -f "$input_file" ]; then
        # Define the output file name with '_r' suffix
        output_file="${remapped_tmpdir}/${filename%.*}_r.nc"

        # Perform the remap operation using CDO
        cdo remapmean,"$target_grid" "$input_file" "$output_file"

        # Check if the remap operation was successful
        if [ $? -eq 0 ]; then
            echo "Remap successful for: $input_file"

            echo -e "\033[32mCalling Python script to add timestamps to $output_file with index $file_index\e[0m"
			
            # Call the Python script to add timestamps to the file
            python3 /scratch/depfg/pokhr002/SPHY3.0/input/netcdf_forcing/add_time_nc.py "$output_file" $file_index

            # Increment file index
            file_index=$((file_index + 1))

            # Remove the input file from the temporary directory
            rm "$input_file"
            echo -e "\e[1;35mProcessed, moved, and deleted: $input_file -> $output_file\e[0m"
        else
            echo -e "\e[1;31mFailed to process: $input_file\e[0m"
        fi
    else
        echo -e "\e[1;31mFailed to extract: $filename\e[0m"
    fi
done

echo -e "\e[35mAll files have been processed to netcdf then remapped\e[0m"
echo -e "\e[34;43mNOW COMBINE AND ZIP THE FILES.\e[0m"

# Combine all remapped files into a single NetCDF file
combined_output_file="${outroot}/pr_1991-2022_KB.nc"
cdo mergetime "$remapped_tmpdir"/*.nc "$combined_output_file"

# Create a zip file containing all remapped files
zip_filename_out="${outroot}/remapped_files.zip"
zip -j "$zip_filename_out" "$remapped_tmpdir"/*

# Clean up the temporary directories
rm -r "$tmproot" "$remapped_tmpdir"

# Display the structure of the NetCDF file
ncdump -h "$combined_output_file"



#| grep -q "nan": This pipes the output of the cdo info command to grep, which searches for the string "nan" (indicating a NaN value); 
			# -q: This option tells grep to operate in "quiet" mode, meaning it will not print anything to the console but will set its exit status to 0 if it finds a match, and 1 if it does not.
                