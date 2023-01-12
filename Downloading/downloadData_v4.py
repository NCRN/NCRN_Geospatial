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
#__version__ = "1.0.1"
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
from arcpy import env
import glob


###Setup progress box

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

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
Some of these global variables may not be in use yet.
"""

# Set the directory path to the root directory that will be documented
__WORKSPACE = r'U:\GIS'

# Set the directory path to the root directory that will be documented
__ROOT_DIR = r'C:\Users\goettel\OneDrive - DOI\Documents\Test_Downloads'

# Create a variable to store the file extension for file geodatabases
__FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
__SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
__EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (that are outside of FGDBs)
__RAST_EXT = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.sid', '.bmp'] # Logical variable to parameterize for toolbox and/or command line

# Create a variable to store the full path to the GIS Library sources Excel file
__XCEL_LIBRARY = r'C:\Users\goettel\OneDrive - DOI\Geospatial\NCRN-GIS-Data-Sources.xlsx'


###Download feature service items from ArcGIS Online

#Specify the ArcGIS Online credentials to use.
#gis = GIS("https://arcgis.com", "Username", "Password")
#print("Connected.")

gis = GIS("pro")

###Read excel into dataframe using Pandas
df_NCRN_GIS_Data_Sources = pd.read_excel(__XCEL_LIBRARY, sheet_name='Sources', usecols = ['ID', 'Status', 'Activated', 'Source Data Type', 'Web File for Download', 'Data Item ID', 'Local Directory', 'Folder Rename', 'Geodatabase Name', 'New Geodatabase Name', 'File Name 1', 'Feature Class Rename 1', 'File Name 2', 'Feature Class Rename 2', 'File Name 3', 'Feature Class Rename 3', 'File Name 4', 'File Name 5', 'File Name 6'])
#print(df_NCRN_GIS_Data_Sources)

##Select sources where Status is URL
df_NCRN_GIS_Data_Sources_URL = df_NCRN_GIS_Data_Sources[(df_NCRN_GIS_Data_Sources["Status"] == 'URL') & (df_NCRN_GIS_Data_Sources["Activated"]=='Yes')]

#download urls
for index, row in df_NCRN_GIS_Data_Sources_URL.iterrows():
    #Folder where the download will go
    dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
    #print('Download Destination: ', dest_dir)
    #File path for the download
    try:
        dest_path = os.path.join(dest_dir, row['Folder Rename'])
    except Exception:
        pass
    #print('Download File: ', dest_path)
    #Define download link
    url = row['Web File for Download']
    #Old file name of the url
    filename = url.split('/')[-1]
    #print('Filename: ', filename)
    ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
    #print('Extract to Dir: ', ext_dir_name)
    fullpath_filename = os.path.join(dest_dir, filename)
    #print('Full File Path: ', fullpath_filename)
    download_url_wget(dest_dir, url)
    if filename.endswith('.zip'):
        #print("'{0}' is unzipping...Please be patient!\n".format(filename))
        shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
        print("Unzipped: {0}.\n".format(fullpath_filename))
        #delete zip file after extract
        os.remove(fullpath_filename)
        #rename file
        try:
            os.rename(ext_dir_name, dest_path)
            print("Rename complete")
        except Exception:
            pass
    else:     
        try:
            os.rename(fullpath_filename, dest_path)
            print("Rename complete")
        except Exception:
            pass
print(df_NCRN_GIS_Data_Sources_URL)

###Select sources where Status is AGOL
df_NCRN_GIS_Data_Sources_AGOL = df_NCRN_GIS_Data_Sources[(df_NCRN_GIS_Data_Sources["Status"] == 'AGOL') & (df_NCRN_GIS_Data_Sources["Activated"] == 'Yes')]

##download AGOL content
for index, row in df_NCRN_GIS_Data_Sources_AGOL.iterrows():
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
            os.remove(fullpath_filename)
    elif row['Source Data Type']=='Multiple (File Geodatabase)':
        data_item = data_item.export(title = row['Folder Rename'], export_format = "File Geodatabase", wait = True)
        data_item.get_data()
        filename = data_item.download(dest_dir)
        ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
        fullpath_filename = os.path.join(dest_dir, filename)
        if filename.endswith('.zip'):
            #print("'{0}' is unzipping...please be patient!\n".format(filename))
            shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
            print("unzipped: {0}.\n".format(fullpath_filename))
            os.remove(fullpath_filename)
print(df_NCRN_GIS_Data_Sources_AGOL)

##Rename geodatabases
print('Checking for Geodatabases to rename...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    #NHDPlus, TIGER
    if ((row['ID'] == 20) or (row['ID'] == 21) or (row['ID'] == 22)):
        try:
            arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'])
            in_data = row['Geodatabase Name']
            out_data = row['New Geodatabase Name']
            data_type = "FileGeodatabase"
            arcpy.management.Rename(in_data, out_data, data_type)
            print('Geodatabase renamed as: ', row['New Geodatabase Name'])
        except Exception:
            pass

## Create geodatabases
print('Checking for new Geodatabases to create...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    #HIFLD/OSM, NWI, USGS, EPA  
    if  ((row['ID'] == 3) or (row['ID'] == 40) or (row['ID'] == 44) or (row['ID'] == 45)):
        dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
        dest_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['New Geodatabase Name'])
        if os.path.exists(dest_path):
            pass
        else: 
            arcpy.CreateFileGDB_management(dest_dir, row['New Geodatabase Name'])
            print('Created Geodatabase: ', row['New Geodatabase Name'])

#Merge feature classes
print('Checking for feature classes to merge...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    #TIGER
    if row['ID'] == 22:
        try:
            dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['New Geodatabase Name'])
            fc1 = os.path.join(dest_dir, row['File Name 3'])
            fc2 = os.path.join(dest_dir, row['File Name 4'])
            output = os.path.join(dest_dir, row['Feature Class Rename 3'])
            arcpy.env.workspace = dest_dir
            arcpy.management.Merge([fc1, fc2], output)
            print('Merged feature class: ', row['Feature Class Rename 3'])
        except Exception:
            pass
    #OSM
    elif ((row['ID'] == 23) or (row['ID'] == 26) or (row['ID'] == 29) or (row['ID'] == 32)):
        try:
            input_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
            gdb_path = os.path.join(__ROOT_DIR, row['New Geodatabase Name'])
            fc1 = os.path.join(dest_dir, row['File Name 1'])
            fc2 = os.path.join(dest_dir, row['File Name 2'])
            fc3 = os.path.join(dest_dir, row['File Name 3'])
            fc4 = os.path.join(dest_dir, row['File Name 4'])
            output = os.path.join(gdb_path, row['Feature Class Rename 1'])
            arcpy.env.workspace = dest_dir
            arcpy.management.Merge([fc1, fc2, fc3, fc4], output)
            print('Merged feature class: ', row['Feature Class Rename 1'])
        except Exception:
            pass
    #NWI
    elif row['ID'] == 40:
        try:
            dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
            fc1 = os.path.join(dest_dir, row['File Name 1'])
            fc2 = os.path.join(dest_dir, row['File Name 2'])
            fc3 = os.path.join(dest_dir, row['File Name 3'])
            fc4 = os.path.join(dest_dir, row['File Name 4'])
            output = os.path.join(dest_dir, row['New Geodatabase Name'], row['Feature Class Rename 1'])
            arcpy.env.workspace = dest_dir
            arcpy.management.Merge([fc1, fc2, fc3, fc4], output)
            print('Merged feature class: ', row['Feature Class Rename 1'])
        except Exception:
            pass
                
#Merge rasters
print('Checking for rasters to merge...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    #NED
    if row['ID'] == 35:
        env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'])
        try:
            input_rasters = (row['File Name 1'], row['File Name 2'], row['File Name 3'], row['File Name 4'], row['File Name 5'])
            output_location = os.path.join(__ROOT_DIR, row['New Geodatabase Name'])
            raster_dataset_name_with_extension = row['Feature Class Rename 1']
            arcpy.management.MosaicToNewRaster(input_rasters, 
                                                output_location,
                                                raster_dataset_name_with_extension,
                                                'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', 
                                                "32_BIT_FLOAT", None, 1, "LAST", "FIRST")
            #Rename output
            arcpy.env.workspace = os.path.join(__ROOT_DIR, row['New Geodatabase Name'])
            in_data = row['File Name 6']
            out_data = row['Feature Class Rename 1']
            data_type = "FeatureClass"
            arcpy.management.Rename(in_data, out_data, data_type)
            print('Merged raster: ', out_data)
        except Exception:
            pass

#Create feature classes for geodatabases
print('Checking for new Feature Classes to create...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    try:
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['Geodatabase Name'])
        inFeatures = row['File Name 1']
        outLocation = os.path.join(__ROOT_DIR, row['Local Directory'], row['New Geodatabase Name'])
        outFeatureClass = row['Feature Class Rename 1']
        arcpy.FeatureClassToFeatureClass_conversion(inFeatures, outLocation, outFeatureClass)
        print('Created feature class: ', outFeatureClass)
    except Exception:
        pass
    try:
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'])
        inFeatures = row['File Name 1']
        outLocation = os.path.join(__ROOT_DIR, row['Local Directory'], row['New Geodatabase Name'])
        outFeatureClass = row['Feature Class Rename 1']
        arcpy.FeatureClassToFeatureClass_conversion(inFeatures, outLocation, outFeatureClass)
        print('Created feature class: ', outFeatureClass)
    except Exception:
        pass
    try:
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['Geodatabase Name'])
        inFeatures = row['File Name 2']
        outLocation = os.path.join(__ROOT_DIR, row['Local Directory'], row['New Geodatabase Name'])
        outFeatureClass = row['Feature Class Rename 2']
        arcpy.FeatureClassToFeatureClass_conversion(inFeatures, outLocation, outFeatureClass)
        print('Created feature class: ', outFeatureClass)
    except Exception:
        pass
    try:
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['Geodatabase Name'])
        inFeatures = row['File Name 3']
        outLocation = os.path.join(__ROOT_DIR, row['Local Directory'], row['New Geodatabase Name'])
        outFeatureClass = row['Feature Class Rename 3']
        arcpy.FeatureClassToFeatureClass_conversion(inFeatures, outLocation, outFeatureClass)
        print('Created feature class: ', outFeatureClass)
    except Exception:
        pass
 
##Rename feature classes in geodatabases
print('Checking for Feature Classes to rename...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    try:
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['New Geodatabase Name'])
        in_data = row['File Name 1']
        out_data = row['Feature Class Rename 1']
        data_type = "FeatureClass"
        arcpy.management.Rename(in_data, out_data, data_type)
        print('Feature class renamed as: ', out_data)
    except Exception:
        pass
    try:
        arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['New Geodatabase Name'])
        in_data = row['File Name 2']
        out_data = row['Feature Class Rename 2']
        data_type = "FeatureClass"
        arcpy.management.Rename(in_data, out_data, data_type)
        print('Feature class renamed as: ', out_data)
    except Exception:
        pass

##Remove feature classes
print('Checking for Feature Classes to remove...')
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    #TIGER
    if row['ID'] == 22:
        try:
            arcpy.env.workspace = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'], row['New Geodatabase Name'])
            fc1 = 'Block_Group'
            fc2 = 'Census_Tract'
            fc3 = 'Consolidated_City'
            fc4 = 'County_Subdivision'
            fc5 = 'Census_Designated_Place'
            fc6 = 'Incorporated_Place'
            arcpy.management.Delete(fc1, fc2, fc3, fc4, fc5, fc6)
            print('Removed: ', fc1, fc2, fc3, fc4, fc5, fc6)
        except Exception:
            pass

## NPDES Discharge Points xy table to point
for index, row in df_NCRN_GIS_Data_Sources.iterrows():
    if row['Source Data Type'] == 'CSV':
        if os.path.exists(os.path.join(dest_path, row['Feature Class Rename 1'])):
            pass
        else:
            try:
                print('Running xy table to point...')
                dest_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['Folder Rename'])
                gdb_path = os.path.join(__ROOT_DIR, row['Local Directory'], row['New File Name'])
                input_csv = os.path.join(dest_path, row['File Name 1'])
                df = pd.read_csv(input_csv, low_memory=False)
                df["latitude"] = df["LATITUDE83"].astype(float)
                df["longitude"] = df["LONGITUDE83"].astype(float)
                output_csv = os.path.join(dest_path, row['Feature Class Rename 1'])
                df.to_csv(output_csv)
                print('Exported CSV')
                arcpy.management.XYTableToPoint(output_csv, 
                                                os.path.join(gdb_path, row["Feature Class Rename 1"]), 
                                                "longitude", "latitude", None, 
                                                'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1920000002.98022;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')        
                print('xy table to point was successful')
            except Exception:
                pass

#Create hillshading layer