#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial working script for downloading GIS data and formatting the NCRN GIS Library.
--------------------------------------------------------------------------------
TODO: Add more of a complete description (once the MVP is working and refactored.)

References:
# https://stackoverflow.com/questions/72088811/how-to-download-a-large-zip-file-25-gb-using-python
# https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
TEST CHANGE
"""

#__author__ = "NCRN GIS Unit"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.4"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"

# Import statements for utilized libraries / packages
from ast import If
import datetime
import os
import sys
import pandas as pd
import requests
import shutil
import wget
import arcgis
from arcgis.gis import GIS
import pathlib
from pathlib import Path, PurePath
import zipfile
from zipfile import ZipFile
import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy import env
from arcpy.sa import *
import glob

print('### GETTING STARTED ###'.format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool
__ROOT_DIR = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial' ## Set the directory path to the root directory that will be the destination for downloads. Example: _WORKSPACE = r'C:\_GIS'

__XCEL_LIBRARY = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_GIS_Data_Sources.xlsx' ## Create a variable to store the full path to the GIS Library Sources Excel file

# Specify the ArcGIS Online credentials to use.
# DELETE BEFORE COMMITING TO GITHUB
print('Connecting to ArcGIS Online...')
try:
    gis = GIS("https://arcgis.com", "Username", "Password")
    print('Connected')
except:
    print('Not connected')

# Connect to ArcGIS Pro
print('Connecting to ArcGIS Pro...')
try:
    gis = GIS("pro")
    print('Connected')
except:
    print('Not connected')

# Create some functions to be used in various places

# Setup progress box
def get_file_size_requests(url):
    """
    Utility function to get the size of a file at a URL using requests library.
        NOTE: May not work on all file types and all endpoints.

    Keyword arguments:
    url -- The full URL of a file on the internet as a string.
        Example: r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip'

    Return:
    size -- File size in bytes as integer
    """
    # Create a request for URL head content and store in variable
    response = requests.head(url)
    # Parse the header of the request response and get the Content Length (i.e., file size in bytes)
    size = int(response.headers['Content-Length'])
    # Return the file size in bytes
    return size

def download_progress_bar_custom(current, total, width=80):
    """
    Utility function to create a custom progress bar

    Keyword arguments:
    current -- The full URL of a file on the internet as a string.
        Example: r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip'

    Return:
    size -- File size in bytes as integer
    """
    #print(int(int(current) / int(total) * 100) % 10)
    if int(int(current) / int(total) * 100) % 10 == 0:
        print("Downloading: {0}% [{1} / {2}] bytes".format(current / total * 100, current, total))

def download_url_wget(out_dir, url):
    """
    Utility function to download a file via URL using wget library.
        NOTE: May not work on all URLs. Tends to work best on files with explicit endpoint on the web.

    Keyword arguments:
    out_dir -- The full filepath to destination directory to download things to in string format.
        Example: r'C:\GIS'
    url -- A single URLs
        Example:    r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip'
    """

    # Create a datetime object for current date/time before download
    start_dtm = datetime.datetime.now()
    # Print status to Python console with start time
    print("'{0}' is downloading...Please be patient!\nStart time: {1}\n".format(url.split('/')[-1], str(datetime.datetime.time(start_dtm))))
    # Call the wget.download function with the url and output directory as variables
    wget.download(url=url, out=out_dir, bar=download_progress_bar_custom)
    # Create a datetime object for current date/time after download
    end_dtm = datetime.datetime.now()
    # Create a variable to store the time elapsed during download
    diff_dtm = end_dtm - start_dtm
    # Print status to Python console with where the file was downloaded and how long it took
    print("The file downloaded to: {0}.\nDownload time: {1}".format(os.path.join(out_dir, url.split('/')[-1]), str(diff_dtm)))

def download_url_list_wget(out_dir, url_list):
    """
    Utility function to download a list of files via URL using wget library.
        NOTE: May not work on all URLs. Tends to work best on files with explicit endpoint on the web.

    Keyword arguments:
    out_dir -- The full filepath to destination directory to download things to in string format.
        Example: r'C:\GIS'
    url_list -- List of URLs. List could be just one item.
        Example:    [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip',
                    r'https://www.fws.gov/wetlands/Data/State-Downloads/MD_shapefile_wetlands.zip']
    """

    # Loop over the list of urls
    for url in url_list:
        download_url_wget(out_dir, url)

# Read excel into dataframe using Pandas
print('Importing Data Sources excel...')
df_NCRN_GIS_Data_Sources = pd.read_excel(__XCEL_LIBRARY, sheet_name='Sources', usecols = ['ID', 'Status', 'Source Type', 'Activated', 'Source Data Type', 'Web File for Download', 'Items', 'Data Item ID', 'Local Directory', 'Original GDB Name', 'New GDB Directory', 'New GDB Name', 'File Names', 'New File Names'])

# Delete existing copy of activated downloads
print('Deleting existing copies before downloading...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if row["Activated"]=='Yes':
        # Delete files within FGDB downloads (Original GDB Name)
        try:
            path = os.path.join(__ROOT_DIR, row['Local Directory'], row['Original GDB Name'])
            for file_name in os.listdir(path):
                file = os.path.join(path, file_name)
                if os.path.isfile(file):
                    os.remove(file)
        except Exception:
            pass
        # Delete files within FGDB downloads (New GDB Name)
        try:
            path = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
            for file_name in os.listdir(path):
                file = os.path.join(path, file_name)
                if os.path.isfile(file):
                    os.remove(file)
        except Exception:
            pass
        # Delete files within downloads containing subfolders (e.g. SSURGO & STATSGO2)
        try:
            def Convert(string):
                li = list(string.split(", "))
                return li
            items_str = row['Original GDB Name']
            items_list = Convert(items_str)
            dir = os.path.join(__ROOT_DIR, row['Local Directory'])
            path1 = os.path.join(dir, items_list[0])
            path2 = os.path.join(path1, items_list[1])
            path3 = os.path.join(path1, items_list[2])
            #Delete files within the first subfolder (e.g. spatial) of the primary subfolder (e.g. DC001)
            for file_name in os.listdir(path2):
                file = os.path.join(path2, file_name)
                if os.path.isfile(file):
                    os.remove(file)
            #Delete files within the second subfolder (e.g. tabular) of the primary subfolder
            try:
                for file_name in os.listdir(path3):
                    file = os.path.join(path3, file_name)
                    if os.path.isfile(file):
                        os.remove(file)
            except:
                pass
            #Delete files within the primary subfolder
            for file_name in os.listdir(path1):
                file = os.path.join(path1, file_name)
                if os.path.isfile(file):
                    os.remove(file)
            #Delete the primary subfolder
            os.rmdir(path1)
        except Exception:
                pass
        #Delete files within multi-item FGDB downloads (e.g. 3DEP Contours)
        try:
            def Convert(string):
                li = list(string.split(", "))
                return li
            items_str = row['Items']
            items_list = Convert(items_str)
            dir_path = os.path.join(__ROOT_DIR, row['Local Directory'])
            for item in items_list:
                path = os.path.join(dir_path, item)
                for file_name in os.listdir(path):
                    file = os.path.join(path, file_name)
                    if os.path.isfile(file):
                        os.remove(file)
                os.rmdir(path)
        except Exception:
            pass
        #Delete files
        try:
            dir_path = os.path.join(__ROOT_DIR, row['Local Directory'])
            for file_name in os.listdir(dir_path):
                file = os.path.join(dir_path, file_name)
                if os.path.isfile(file):
                    os.remove(file)
        except Exception:
            pass
        #Delete empty folders
        try:
            dir_path = os.path.join(__ROOT_DIR, row['Local Directory'])
            for file_name in os.listdir(dir_path):
                file = os.path.join(dir_path, file_name)
                if os.path.isdir(file):
                    os.rmdir(file)
        except Exception:
            pass
        
# Download activated URLs
print('Downloading URLs...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if ((row['Status']=='URL') & (row["Activated"]=='Yes')):
        dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        #print('Download Destination: ', dest_dir)
        if row['Source Type']=='Dataset':
            url = row['Web File for Download']
            filename = url.split('/')[-1]
            #print('Filename: ', filename)
            fullpath_filename = os.path.join(dest_dir, filename)
            #print('Full File Path: ', fullpath_filename)
            download_url_wget(dest_dir, url)
            if filename.endswith('.zip'):
                #print("'{0}' is unzipping...Please be patient!\n".format(filename))
                shutil.unpack_archive(fullpath_filename, dest_dir)
                print("Unzipped: {0}.\n".format(fullpath_filename))
                # delete zip file after extract
                os.remove(fullpath_filename)
        # Download multi-item URLs (e.g. 3DEP Contours)
        elif row['Source Type']=='Datasets':
                def Convert(string):
                    li = list(string.split(", "))
                    return li
                items_str = row['Items']
                items_list = Convert(items_str)
                for item in items_list:
                    url = os.path.join(row['Web File for Download'], item)
                    filename = url.split('/')[-1]
                    #print('Filename: ', filename)
                    fullpath_filename = os.path.join(dest_dir, filename)
                    #print('Full File Path: ', fullpath_filename)
                    download_url_wget(dest_dir, url)
                    if filename.endswith('.zip'):
                        #print("'{0}' is unzipping...Please be patient!\n".format(filename))
                        shutil.unpack_archive(fullpath_filename, dest_dir)
                        print("Unzipped: {0}.\n".format(fullpath_filename))
                        # delete zip file after extract
                        os.remove(fullpath_filename)

# Download feature service items from ArcGIS Online
print('Downloading feature service items from ArcGIS Online...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if ((row["Status"] == 'AGOL') & (row["Activated"] == 'Yes')):
        dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        data_item_id = row['Data Item ID']
        data_item = gis.content.get(data_item_id)
        if row['Source Data Type']=='File Geodatabase':       
            data_item.get_data()
            filename = data_item.download(dest_dir)
            ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
            fullpath_filename = os.path.join(dest_dir, filename)
            if filename.endswith('.zip'):
                #print("'{0}' is unzipping...please be patient!\n".format(filename))
                shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
                print("unzipped: {0}.\n".format(fullpath_filename))
                # delete zip file after extract
                os.remove(fullpath_filename)
        elif row['Source Data Type']=='Multiple (File Geodatabase)':
            data_item = data_item.export(title = data_item_id, export_format = "File Geodatabase", wait = True)
            data_item.get_data()
            filename = data_item.download(dest_dir)
            fullpath_filename = os.path.join(dest_dir, filename)
            if filename.endswith('.zip'):
                #print("'{0}' is unzipping...please be patient!\n".format(filename))
                shutil.unpack_archive(fullpath_filename, dest_dir)
                print("unzipped: {0}.\n".format(fullpath_filename))
                # delete zip file after extract
                os.remove(fullpath_filename)

# Rename FGDBs as needed
print('Checking for FGDBs to rename...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if ((row['ID'] == 3) or (row['ID'] == 68) or (row['ID'] == 69)): ## Select FGDBs to rename using row ID
        gdb_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['Original GDB Name'])
        new_gdb_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        in_data = row['Original GDB Name']
        out_data = row['New GDB Name']
        data_type = "FileGeodatabase"
        if os.path.exists(gdb_path):
            arcpy.management.Rename(in_data, out_data, data_type)
            print('FGDB renamed as: ', row['New GDB Name'])

# Create new FGDBs as needed
print('Checking for new FGDBs to create...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    # Create FGDB in parent folder (e.g. Open Street Map) 
    if row['ID'] == 23: ## Select FGDBs to rename using row ID
        gdb_dir = os.path.join(__ROOT_DIR, row['New GDB Directory'])
        gdb_path = os.path.join(gdb_dir, row['New GDB Name'])
        if os.path.exists(gdb_path):
            pass
        else: 
            arcpy.CreateFileGDB_management(gdb_dir, row['New GDB Name'])
            print('Created FGDB: ', row['New GDB Name'])
    # Create FGDB in same folder (e.g. NWI) 
    elif ((row['ID'] == 40) or (row['ID'] == 47) or (row['ID'] == 63) or (row['ID'] == 67)): ## Select FGDBs to create using row ID
        gdb_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        gdb_path = os.path.join(gdb_dir, row['New GDB Name'])
        if os.path.exists(gdb_path):
            pass
        else: 
            arcpy.CreateFileGDB_management(gdb_dir, row['New GDB Name'])
            print('Created FGDB: ', row['New GDB Name'])

# Merge feature classes as needed
print('Checking for feature classes to merge...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    # 4 feature classes to FGDB in parent folder (e.g. Open Street Map)
    if ((row['ID'] == 23) or (row['ID'] == 26) or (row['ID'] == 29) or (row['ID'] == 32)): ## Select using row ID
        def Convert(string):
            li = list(string.split(", "))
            return li
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        gdb_path = os.path.join(__ROOT_DIR, row['New GDB Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR,  row['New GDB Directory'])
        in_data1 = os.path.join(arcpy.env.workspace, in_data_list[0])
        in_data2 = os.path.join(arcpy.env.workspace, in_data_list[1])
        in_data3 = os.path.join(arcpy.env.workspace, in_data_list[2])
        in_data4 = os.path.join(arcpy.env.workspace, in_data_list[3])
        out_data = os.path.join(gdb_path, row['New File Names'])
        # Delete existing feature classes
        if arcpy.Exists(out_data):
            arcpy.env.workspace = gdb_path
            arcpy.management.Delete(out_data)
        arcpy.management.Merge([in_data1, in_data2, in_data3, in_data4], out_data)
        print('Merged feature class: ', row['New File Names'])
    # 4 feature classes to FGDB in same folder (e.g. NWI)
    if ((row['ID'] == 40) or (row['ID'] == 63)): ## Select using row ID
        def Convert(string):
            li = list(string.split(", "))
            return li
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        gdb_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        in_data1 = os.path.join(arcpy.env.workspace, in_data_list[0])
        in_data2 = os.path.join(arcpy.env.workspace, in_data_list[1])
        in_data3 = os.path.join(arcpy.env.workspace, in_data_list[2])
        in_data4 = os.path.join(arcpy.env.workspace, in_data_list[3])
        out_data = os.path.join(gdb_path, row['New File Names'])
        # Delete existing feature classes
        if arcpy.Exists(out_data):
            arcpy.env.workspace = gdb_path
            arcpy.management.Delete(out_data)
        arcpy.management.Merge([in_data1, in_data2, in_data3, in_data4], out_data)
        print('Merged feature class: ', row['New File Names'])
    # 6 feature classes to FGDB in same folder (e.g. contours)
    if row['ID'] == 67: ## Select using row ID
        def Convert(string):
            li = list(string.split(", "))
            return li
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        gdb_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        in_data1 = os.path.join(arcpy.env.workspace, in_data_list[0])
        in_data2 = os.path.join(arcpy.env.workspace, in_data_list[1])
        in_data3 = os.path.join(arcpy.env.workspace, in_data_list[2])
        in_data4 = os.path.join(arcpy.env.workspace, in_data_list[3])
        in_data5 = os.path.join(arcpy.env.workspace, in_data_list[4])
        in_data6 = os.path.join(arcpy.env.workspace, in_data_list[5])
        out_data = os.path.join(gdb_path, row['New File Names'])
        # Delete existing feature classes
        if arcpy.Exists(out_data):
            arcpy.env.workspace = gdb_path
            arcpy.management.Delete(out_data)
        arcpy.management.Merge([in_data1, in_data2, in_data3, in_data4, in_data5, in_data6], out_data)
        print('Merged feature class: ', row['New File Names'])
    # 5 raster datasets to GeoTIFF in same folder (e.g. 3DEP DEM)
    if row['ID'] == 35: ## Select using row ID
        def Convert(string):
            li = list(string.split(", "))
            return li
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        in_data = (in_data_list[0], in_data_list[1], in_data_list[2], in_data_list[3], in_data_list[4])
        out_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        out_data = row['New File Names']
        env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        arcpy.management.MosaicToNewRaster(in_data, out_dir, out_data,
                                            'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
                                            "32_BIT_FLOAT", None, 1, "LAST", "FIRST")
        print('Merged raster: ', out_data)

# Convert csv download to point feature class (e.g. NPDES Discharge Points)
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if row['Source Data Type'] == 'CSV':
        print('Running xy table to point...')
        def Convert(string):
            li = list(string.split(", "))
            return li
        out_data_str = row['New File Names']
        out_data_list = Convert(out_data_str)
        dir_path = os.path.join(__ROOT_DIR, row['Local Directory'])
        path1 = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        # Read csv into dataframe
        in_csv = os.path.join(dir_path, row['File Names'])
        df = pd.read_csv(in_csv, low_memory=False)
        df["latitude"] = df["LATITUDE83"].astype(float)
        df["longitude"] = df["LONGITUDE83"].astype(float)
        out_csv = os.path.join(dir_path, out_data_list[0])
        if os.path.exists(out_csv):
            os.remove(out_csv)
        # Export dataframe to CSV
        df.to_csv(out_csv)
        in_table = out_csv
        out_data = out_data_list[1]
        path2 = os.path.join(path1, out_data)
        x_coords = "longitude"
        y_coords = "latitude"
        # Delete existing copy of feature class
        if arcpy.Exists(path2):
            arcpy.env.workspace = path1
            arcpy.management.Delete(out_data)
        # Run XY Table to Point tool
        arcpy.env.workspace = path1
        arcpy.management.XYTableToPoint(in_table, 
                                        out_data, 
                                        x_coords, y_coords, None, 
                                        'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1920000002.98022;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')        
        print('xy table to point was successful')