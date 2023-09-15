#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Abstract: Initial working script for downloading GIS data and formatting the NCRN GIS Library.

Description: 
The purpose of this script is to download internal and authoritative external data sources to the NCRN GIS Library.
An excel spreadsheet will define the parameters for the location of each download in the directory.
The two items that the script accepts at the moment are URLs and ArcGIS Online Data Item IDs.
The script will unzip the downloads and finally preform geoproccessing on select downloads.

TODO: Additional refactoring
--------------------------------------------------------------------------------
References:
# https://stackoverflow.com/questions/72088811/how-to-download-a-large-zip-file-25-gb-using-python
# https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
TEST CHANGE

#__author__ = "NCRN GIS Unit"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.4"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"
"""

# Import statements for utilized libraries / packages
from ast import If
from datetime import date
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

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool
__ROOT_DIR = r'C:\Users\goettel\Downloads\Geospatial_Copy' ## Set the directory path to the root directory that will be the destination for downloads. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT
__XCEL_LIBRARY = r'C:\Users\goettel\OneDrive - DOI\Geospatial\NCRN_GIS_Data_Sources.xlsx' ## Create a variable to store the full path to the Excel file. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT

# Specify the ArcGIS Online credentials to use.
# DELETE BEFORE COMMITING TO GITHUB
print("Connecting to ArcGIS Online...")
try:
    #gis = GIS("https://arcgis.com", "Username", "Password")
    print("Connected.")
except:
    print("Not connected")

# Connect to ArcGIS Pro
print("Connecting to ArcGIS Pro...")
try:
    gis = GIS("pro")
    print("Connected")
except:
    print("Not connected")

# Create some functions to be used in various places
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
    try:
        wget.download(url=url, out=out_dir, bar=download_progress_bar_custom)
    except Exception as e:
            print("Could not download {}".format(url.split('/')[-1], str(datetime.datetime.time(start_dtm))))
            print(e)
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

def Convert(string):
    """
    convert string to list
    string.split("delimiter")
    Example:
    Input : "Geeks for Geeks"
    Output : ['Geeks', 'for', 'Geeks']
    """
    li = list(string.split(", "))
    return li

def Clear_Folder(folder_path):
    """
    Takes the path of a folder or geodatabase and deletes the files within it
    """
    for filename in os.listdir(folder_path):
        fullpath_filename = os.path.join(folder_path, filename)
        if os.path.isfile(fullpath_filename):
            os.remove(fullpath_filename)
            print("Deleted download: {0}".format(filename))

def Write_Date_to_Text_File(filename, dest_dir):
    """
    Writes date of a download to a text file in the same folder
    """
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    textfilename = filename + '.txt'
    fullpath_textfilename = os.path.join(dest_dir, textfilename)
    with open(fullpath_textfilename, 'w') as f:
        f.write(d1)

# Read excel into dataframe using Pandas
df_NCRN_GIS_Data_Sources = pd.read_excel(__XCEL_LIBRARY, sheet_name='Sources')

# Delete existing copies of activated downloads
print("Deleting existing copies before downloading...")
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if row['Activated'] == 'Yes':
        # Delete files within geodatabase downloads (gdb wasn't renamed)
        try:
            fullpath_fgdbname = os.path.join(__ROOT_DIR, row['Local Directory'], row['Original GDB Name']) ## Full path of the geodatabase
            Clear_Folder(fullpath_fgdbname)
        except Exception:
            pass
        # Delete files within geodatabase downloads (gdb was renamed)
        try:
            fullpath_fgdbrename = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name']) ## Full path of the renamed geodatabase
            Clear_Folder(fullpath_fgdbrename)
        except Exception:
            pass
        # Delete files within downloads containing subfolders (e.g. SSURGO & STATSGO2)
        try:
            items_str = row['File Names']
            items_list = Convert(items_str)
            folder_path = os.path.join(__ROOT_DIR, row['Local Directory']) ## Path to where the folder is located
            fullpath_subfoldername = os.path.join(folder_path, items_list[0]) ## Path and name of the parent subfolder
            # Delete files within the first subfolder
            fullpath_subfoldername1 = os.path.join(fullpath_subfoldername, items_list[1]) ## Path to the first subfolder (e.g. spatial) in the parent subfolder (e.g. DC001)
            Clear_Folder(fullpath_subfoldername1)
            # Delete files within the second subfolder
            try:
                fullpath_subfoldername2 = os.path.join(fullpath_subfoldername, items_list[2]) ## Path to a second subfolder (e.g. tabular) in the parent subfolder
                Clear_Folder(fullpath_subfoldername2)
            except:
                pass
            # Delete files within the parent subfolder
            Clear_Folder(fullpath_subfoldername)
            # Delete the parent subfolder
            os.rmdir(fullpath_subfoldername)
        except Exception:
                pass
        # Delete files within multi-item downloads (e.g. 3DEP Contours)
        try:
            items_str = row['Items']
            items_list = Convert(items_str)
            folder_path = os.path.join(__ROOT_DIR, row['Local Directory']) ## Path to where the folder is located 
            for item in items_list:
                fullpath_foldername = os.path.join(folder_path, item) ## Path and name of the folder
                Clear_Folder(fullpath_foldername)
                os.rmdir(fullpath_foldername)
        except Exception:
            pass
        # Delete files within download folders
        try:
            folder_path = os.path.join(__ROOT_DIR, row['Local Directory'])
            Clear_Folder(folder_path)
        except Exception:
            pass
        # Delete empty download folders
        try:
            folder_path = os.path.join(__ROOT_DIR, row['Local Directory'])
            for foldername in os.listdir(folder_path):
                fullpath_foldername = os.path.join(folder_path, foldername)
                if os.path.isdir(fullpath_foldername):
                    os.rmdir(fullpath_foldername)
                    print("Deleted download: {0}".format(fullpath_foldername))
        except Exception:
            pass

# Create an empty list to append content that couldn't be downloaded        
Issue_List = []

# Download URLs
print("Downloading activated URLs...")
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    # Download activated URLs
    if ((row['Avaliability'] == 'URL') & (row['Activated'] == 'Yes')):
        dest_dir = os.path.join(__ROOT_DIR, row['Local Directory']) ## Destination in the directory where the download will be sent
        if row['Source Type'] == 'Dataset':
            url = row['Web File for Download']
            filename = url.split('/')[-1] ## Name of the download
            fullpath_filename = os.path.join(dest_dir, filename) ## Folder path and name of the download
            download_url_wget(dest_dir, url)
            if filename.endswith('.zip'):
                try:
                        shutil.unpack_archive(fullpath_filename, dest_dir)
                        print("Unzipped: {0}.\n".format(fullpath_filename))
                        ## delete zip file after extract
                        os.remove(fullpath_filename)
                        Write_Date_to_Text_File(filename, dest_dir)
                except Exception as e:
                    print("Could not unzip {}".format(fullpath_filename))
                    print(e)
                    Issue_List.append(fullpath_filename)
        # Download multi-item URLs (e.g. 3DEP Contours)
        elif row['Source Type'] == 'Datasets':
            # Convert string of items to parsable list
            items_str = row['Items']
            items_list = Convert(items_str)
            for item in items_list:
                url = os.path.join(row['Web File for Download'], item)
                filename = url.split('/')[-1]
                fullpath_filename = os.path.join(dest_dir, filename)
                download_url_wget(dest_dir, url)
                if filename.endswith('.zip'):
                    try:
                        shutil.unpack_archive(fullpath_filename, dest_dir)
                        print("Unzipped: {0}.\n".format(fullpath_filename))
                        ## delete zip file after extract
                        os.remove(fullpath_filename)
                        Write_Date_to_Text_File(filename, dest_dir)
                    except Exception as e:
                        print("Could not unzip {}".format(fullpath_filename))
                        print(e)
                        Issue_List.append(fullpath_filename)

# Download AGOL content
print("Downloading feature service items from ArcGIS Online...")
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if ((row['Avaliability'] == 'AGOL') & (row['Activated'] == 'Yes')):
        dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        data_item_id = row['Data Item ID']
        # Feature service items with geodatabase as the only format option
        if row['File Type'] == 'FileGeodatabase':
            try:
                data_item = gis.content.get(data_item_id)
                data_item.get_data()
                filename = data_item.download(dest_dir)
                ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
                fullpath_filename = os.path.join(dest_dir, filename)
                if filename.endswith('.zip'):
                    shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
                    print("unzipped: {0}.\n".format(fullpath_filename))
                    ## delete zip file after extract
                    os.remove(fullpath_filename)
                    Write_Date_to_Text_File(filename, dest_dir)
            except Exception as e:
                print("Could not get gis content for {}".format(data_item_id))
                print(e)
                Issue_List.append(data_item_id)
        # Feature service items with multiple download format options
        elif row['File Type'] == 'Multiple (FileGeodatabase)':
            try:
                data_item = data_item.export(title = data_item_id, export_format = 'FGDB', wait = True)
                data_item.get_data()
                filename = data_item.download(dest_dir)
                fullpath_filename = os.path.join(dest_dir, filename)
                if filename.endswith('.zip'):
                    shutil.unpack_archive(fullpath_filename, dest_dir)
                    print("unzipped: {0}.\n".format(fullpath_filename))  
                    ## delete zip file after extract
                    os.remove(fullpath_filename) 
                    Write_Date_to_Text_File(filename, dest_dir)
            except Exception as e:
                print("Could not get gis content for {}".format(data_item_id))
                print(e)
                Issue_List.append(data_item_id)

print("Downloads that raised issues: {0}", format(Issue_List))

# Rename the specififed geodatabases
print("Checking for geodatabases to rename...")
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    #if ((row['ID'] == 3) or (row['ID'] == 68) or (row['ID'] == 69)): ## Select geodatabases to rename using row ID
    if ((row['ID'] == 3) or (row['ID'] == 68)): ## Select geodatabases to rename using row ID
        fullpath_fgdbname = os.path.join(__ROOT_DIR, row['Local Directory'], row['Original GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        in_data = row['Original GDB Name']
        out_data = row['New GDB Name']
        data_type = 'FileGeodatabase'
        if os.path.exists(fullpath_fgdbname):
            arcpy.management.Rename(in_data, out_data, data_type)
            print("geodatabase renamed as: {0}".format(row['New GDB Name']))

# Create the specified geodatabases
print("Checking for new geodatabases to create...")
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    # Create geodatabase in parent folder (e.g. Open Street Map) 
    if row['ID'] == 23: ## Select geodatabases to rename using row ID
        folder_path = os.path.join(__ROOT_DIR, row['New GDB Directory']) ## Folder path where the new geodatabase will be located 
        fullpath_fgdbrename = os.path.join(folder_path, row['New GDB Name'])
        if os.path.exists(fullpath_fgdbrename):
            pass
        else: 
            arcpy.CreateFileGDB_management(folder_path, row['New GDB Name'])
            print("Created geodatabase: {0}".format(row['New GDB Name']))
    # Create geodatabase in same folder (e.g. NWI) 
    elif ((row['ID'] == 40) or (row['ID'] == 47) or (row['ID'] == 63) or (row['ID'] == 67)): ## Select geodatabases to create using row ID
        folder_path = os.path.join(__ROOT_DIR, row['Local Directory']) ## Same folder path as the download
        fullpath_fgdbrename = os.path.join(folder_path, row['New GDB Name'])
        if os.path.exists(fullpath_fgdbrename):
            pass
        else: 
            arcpy.CreateFileGDB_management(folder_path, row['New GDB Name'])
            print("Created geodatabase: {0}".format(row['New GDB Name']))

# Merge the specified feature classes
print("Checking for feature classes to merge...")
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    # 4 feature classes to geodatabase in parent folder (e.g. Open Street Map)
    if ((row['ID'] == 23) or (row['ID'] == 26) or (row['ID'] == 29) or (row['ID'] == 32)): ## Select using row ID
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        fullpath_fgdbrename = os.path.join(__ROOT_DIR, row['New GDB Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR,  row['New GDB Directory'])
        in_data1 = os.path.join(arcpy.env.workspace, in_data_list[0])
        in_data2 = os.path.join(arcpy.env.workspace, in_data_list[1])
        in_data3 = os.path.join(arcpy.env.workspace, in_data_list[2])
        in_data4 = os.path.join(arcpy.env.workspace, in_data_list[3])
        out_data = os.path.join(fullpath_fgdbrename, row['New File Names'])
        if arcpy.Exists(out_data):
            arcpy.env.workspace = fullpath_fgdbrename
            ## Delete existing feature classes
            arcpy.management.Delete(out_data)
        arcpy.management.Merge([in_data1, in_data2, in_data3, in_data4], out_data)
        print("Merged feature class: {0}".format(row['New File Names']))
    # 4 feature classes to geodatabase in same folder (e.g. NWI)
    if ((row['ID'] == 40) or (row['ID'] == 63)): ## Select using row ID
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        fullpath_fgdbrename = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        in_data1 = os.path.join(arcpy.env.workspace, in_data_list[0])
        in_data2 = os.path.join(arcpy.env.workspace, in_data_list[1])
        in_data3 = os.path.join(arcpy.env.workspace, in_data_list[2])
        in_data4 = os.path.join(arcpy.env.workspace, in_data_list[3])
        out_data = os.path.join(fullpath_fgdbrename, row['New File Names'])
        if arcpy.Exists(out_data):
            arcpy.env.workspace = fullpath_fgdbrename
            ## Delete existing feature classes
            arcpy.management.Delete(out_data)
        arcpy.management.Merge([in_data1, in_data2, in_data3, in_data4], out_data)
        print("Merged feature class: {0}".format(row['New File Names']))
    # 6 feature classes to geodatabase in same folder (e.g. contours)
    if row['ID'] == 67: ## Select using row ID
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        fullpath_fgdbrename = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        in_data1 = os.path.join(arcpy.env.workspace, in_data_list[0])
        in_data2 = os.path.join(arcpy.env.workspace, in_data_list[1])
        in_data3 = os.path.join(arcpy.env.workspace, in_data_list[2])
        in_data4 = os.path.join(arcpy.env.workspace, in_data_list[3])
        in_data5 = os.path.join(arcpy.env.workspace, in_data_list[4])
        in_data6 = os.path.join(arcpy.env.workspace, in_data_list[5])
        out_data = os.path.join(fullpath_fgdbrename, row['New File Names'])
        if arcpy.Exists(out_data):
            arcpy.env.workspace = fullpath_fgdbrename
            ## Delete existing feature classes
            arcpy.management.Delete(out_data)
        arcpy.management.Merge([in_data1, in_data2, in_data3, in_data4, in_data5, in_data6], out_data)
        print("Merged feature class: {0}".format(row['New File Names']))
    # 5 raster datasets to GeoTIFF in same folder (e.g. 3DEP DEM)
    if row['ID'] == 35: ## Select using row ID
        in_data_str = row['File Names']
        in_data_list = Convert(in_data_str)
        in_data = (in_data_list[0], in_data_list[1], in_data_list[2], in_data_list[3], in_data_list[4])
        dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        out_data = row['New File Names']
        env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        arcpy.management.MosaicToNewRaster(in_data, dest_dir, out_data,
                                            'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
                                            "32_BIT_FLOAT", None, 1, "LAST", "FIRST")
        print("Merged raster: {0}".format(out_data))

# Convert csv downloads to point feature class (e.g. NPDES Discharge Points)
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if row['File Type'] == 'CSV':
        print("Running xy table to point...")
        out_data_str = row['New File Names']
        out_data_list = Convert(out_data_str)
        folder_path = os.path.join(__ROOT_DIR, row['Local Directory'])
        fullpath_fgdbrename = os.path.join(__ROOT_DIR, row['Local Directory'], row['New GDB Name'])
        # Read csv into dataframe
        in_csv = os.path.join(folder_path, row['File Names'])
        df = pd.read_csv(in_csv, low_memory=False)
        df["latitude"] = df["LATITUDE83"].astype(float)
        df["longitude"] = df["LONGITUDE83"].astype(float)
        out_csv = os.path.join(folder_path, out_data_list[0])
        # Remove existing copy of the csv
        if os.path.exists(out_csv):
            os.remove(out_csv)
        # Export dataframe to csv
        df.to_csv(out_csv)
        in_table = out_csv
        out_data = out_data_list[1]
        fullpath_filename = os.path.join(fullpath_fgdbrename, out_data)
        x_coords = "longitude"
        y_coords = "latitude"
        # Delete existing copy of feature class
        if arcpy.Exists(fullpath_filename):
            arcpy.env.workspace = fullpath_fgdbrename
            arcpy.management.Delete(out_data)
        # Run XY Table to Point tool
        arcpy.env.workspace = fullpath_fgdbrename
        arcpy.management.XYTableToPoint(in_table, 
                                        out_data, 
                                        x_coords, y_coords, None, 
                                        'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1920000002.98022;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')        
        print("xy table to point was successful")

print("### !!! ALL DONE !!! ###".format())