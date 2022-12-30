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

###Read excel into dataframe using Pandas
df_NCRN_GIS_Data_Sources = pd.read_excel(__XCEL_LIBRARY, sheet_name='Sources', usecols=['ID', 'Status', 'Activated', 'Source Data Type', 'Web File for Download', 'Data Item ID', 'Source', 'Local Directory', 'File Rename', 'Local File Path', 'Old Layer Name', 'New Layer Name'])

#print(df_NCRN_GIS_Data_Sources)

##Select sources where Status is URL
df_NCRN_GIS_Data_Sources_URL = df_NCRN_GIS_Data_Sources[(df_NCRN_GIS_Data_Sources["Status"] == 'URL') & (df_NCRN_GIS_Data_Sources["Activated"]=='Yes')]

#Iterate over dataframe to download urls
#for index, row in df_NCRN_GIS_Data_Sources_URL.iterrows():
#    #Folder where the download will go
#    dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
#    #print('Download Destination: ', dest_dir)
#    #File path for the download
#    dest_file = os.path.join(__ROOT_DIR, row['Local File Path'])
#    #print('File Path: ', dest_file)
#    #Define download link
#    url = row['Web File for Download']
#    #Old file name of the url
#    filename = url.split('/')[-1]
#    #print('Filename: ', filename)
#    ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
#    #print('Extract to Dir: ', ext_dir_name)
#    fullpath_filename = os.path.join(dest_dir, filename)
#    #print('Full File Path: ', fullpath_filename)
#    download_url_wget(dest_dir, url)
#    if filename.endswith('.zip'):
#        #print("'{0}' is unzipping...Please be patient!\n".format(filename))
#        shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
#        #print("Unzipped: {0}.\n".format(fullpath_filename))
#        #delete zip file after extract
#        os.remove(fullpath_filename)
#        #rename file
#        os.rename(ext_dir_name, dest_file)
#    else:     
#        os.rename(fullpath_filename, dest_file)
#print(df_NCRN_GIS_Data_Sources_URL)

###Download feature service items from ArcGIS Online
#Specify the ArcGIS Online credentials to use.
#gis = GIS("https://arcgis.com", "Username", "Password")
#print("Connected.")



#gis = GIS("pro")

##Select sources where Status is AGOL
df_NCRN_GIS_Data_Sources_AGOL = df_NCRN_GIS_Data_Sources[(df_NCRN_GIS_Data_Sources["Status"] == 'AGOL') & (df_NCRN_GIS_Data_Sources["Activated"]=='Yes')]

##Iterate over dataframe to download AGOL content
#for index, row in df_NCRN_GIS_Data_Sources_AGOL.iterrows():
#    dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
#    data_item_id = row['Data Item ID']
#    data_item = gis.content.get(data_item_id)
#    if row['Source Data Type']=='File Geodatabase':       
#        data_item.get_data()
#        filename = data_item.download(dest_dir)
#        ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
#        fullpath_filename = os.path.join(dest_dir, filename)
#        if filename.endswith('.zip'):
#            #print("'{0}' is unzipping...please be patient!\n".format(filename))
#            shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
#            #print("unzipped: {0}.\n".format(fullpath_filename))
#            os.remove(fullpath_filename)
#    elif row['Source Data Type']=='Multiple (File Geodatabase)':
#        data_item = data_item.export(title = row['File Rename'], export_format = "File Geodatabase", wait = True)
#        data_item.get_data()
#        filename = data_item.download(dest_dir)
#        ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
#        fullpath_filename = os.path.join(dest_dir, filename)
#        if filename.endswith('.zip'):
#            #print("'{0}' is unzipping...please be patient!\n".format(filename))
#            shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
#            #print("unzipped: {0}.\n".format(fullpath_filename))
#            os.remove(fullpath_filename)
#print(df_NCRN_GIS_Data_Sources_AGOL)

##Select sources where Source Data Type is Shapefile and Status is URL
df_NCRN_GIS_Data_Sources_Shapefile = df_NCRN_GIS_Data_Sources[(df_NCRN_GIS_Data_Sources["Source Data Type"] == 'Shapefile') & (df_NCRN_GIS_Data_Sources["Status"] == 'URL')]

#Delete unwanted shapefiles
for index, row in df_NCRN_GIS_Data_Sources_Shapefile.iterrows():
    dest_dir = os.path.join(__ROOT_DIR, row['Local File Path'])
    if row['Source']=='Open Street Map':
        landuse = os.path.join(dest_dir, 'gis_osm_landuse*')
        natural = os.path.join(dest_dir, 'gis_osm_natural*')
        places = os.path.join(dest_dir, 'gis_osm_places*')
        pofw = os.path.join(dest_dir, 'gis_osm_pofw*')
        pois = os.path.join(dest_dir, 'gis_osm_pois*')
        traffic = os.path.join(dest_dir, 'gis_osm_traffic*')
        water = os.path.join(dest_dir, 'gis_osm_water*')
        transport = os.path.join(dest_dir, 'gis_osm_transport*')
        try:
            for item in glob.iglob(landuse, recursive=True):
                os.remove(item)
            for item in glob.iglob(natural, recursive=True):
                os.remove(item)
            for item in glob.iglob(places, recursive=True):
                os.remove(item)
            for item in glob.iglob(pofw, recursive=True):
                os.remove(item)
            for item in glob.iglob(pois, recursive=True):
                os.remove(item)
            for item in glob.iglob(traffic, recursive=True):
                os.remove(item)
            for item in glob.iglob(water, recursive=True):
                os.remove(item)
            for item in glob.iglob(transport, recursive=True):
                os.remove(item)
        except Exception:
            pass

#Rename shapefiles
for index, row in df_NCRN_GIS_Data_Sources_Shapefile.iterrows():
    dest_dir = os.path.join(__ROOT_DIR, row['Local File Path'])
    old_filename = row['Old Layer Name']
    new_filename = row['New Layer Name']
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.cpg'),os.path.join(dest_dir,new_filename+'.cpg')) # Rename cpg file
    except Exception:
        pass
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.dbf'),os.path.join(dest_dir,new_filename+'.dbf')) # Rename dbf file
    except Exception:
        pass
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.prj'),os.path.join(dest_dir,new_filename+'.prj')) # Rename prj file
    except Exception:
        pass
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.shp'),os.path.join(dest_dir,new_filename+'.shp')) # Rename shp file
    except Exception:
        pass
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.shx'),os.path.join(dest_dir,new_filename+'.shx')) # Rename shx file
    except Exception:
        pass
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.sbn'),os.path.join(dest_dir,new_filename+'.sbn')) # Rename sbn file
    except Exception:
        pass
    try:
        os.rename(os.path.join(dest_dir,old_filename+'.sbx'),os.path.join(dest_dir,new_filename+'.sbx')) # Rename sbn file
    except Exception:
        pass

#Rename layers in file geodatabase