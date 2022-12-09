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
import datetime
import os
import pandas as pd
import requests
import shutil
import wget
import arcgis
from arcgis.gis import GIS
from pathlib import Path, PurePath
from zipfile import ZipFile


"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
Some of these global variables may not be in use yet.
"""

# Set the directory path to the root directory that will be documented
__WORKSPACE = r'U:\GIS'

# Set the directory path to the root directory that will be documented
__ROOT_DIR = r'C:\Users\goettel\OneDrive - DOI\Documents'

# Create a variable to store the file extension for file geodatabases
__FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
__SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
__EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (that are outside of FGDBs)
__RAST_EXT = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.sid', '.bmp'] # Logical variable to parameterize for toolbox and/or command line

# Create a variable to store the full path to the GIS Library sources Excel file
__XCEL_LIBRARY = r'C:\Users\goettel\DOI\NCRN Data Management - GIS\NCRN-GIS-Data-Sources.xlsx'

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

########### TESTING ##########

###Read excel into dataframe using Pandas
df_NCRN_GIS_Data_Sources = pd.read_excel(__XCEL_LIBRARY, sheet_name='Sources', usecols=['ID', 'Status', 'Web File for Download', 'Local Directory'])

#print(df_NCRN_GIS_Data_Sources)

##Select sources where Status = Ready
df_NCRN_GIS_Data_Sources_ready = df_NCRN_GIS_Data_Sources[df_NCRN_GIS_Data_Sources["Status"]=='Ready']

for index, row in df_NCRN_GIS_Data_Sources_ready.iterrows():
    dest_dir = os.path.join(__ROOT_DIR, row['Local Directory'])
    #print('Download Destination: ', dest_dir)
    url = row['Web File for Download']
    filename = url.split('/')[-1]
    #print('Filename: ', filename)
    ext_dir_name = os.path.join(dest_dir, os.path.splitext(filename)[0])
    #print('Extract to Dir: ', ext_dir_name)
    fullpath_filename = os.path.join(dest_dir, filename)
    #print('Full File Path: ', fullpath_filename)
    download_url_wget(dest_dir, url)
    if filename.endswith('.zip'):
        print("'{0}' is unzipping...Please be patient!\n".format(filename))
        shutil.unpack_archive(fullpath_filename, os.path.join(dest_dir, ext_dir_name))
        print("Unzipped: {0}.\n".format(fullpath_filename))
        os.remove(fullpath_filename)

#print(df_NCRN_GIS_Data_Sources_ready)

#Download feature service items from ArcGIS Online
#Specify the ArcGIS Online credentials to use.
#gis = GIS("https://arcgis.com", "Username", "Password")
#print("Connected.")

# Download all data from a user
#def downloadUserItems(owner, downloadFormat):
#    try:
#        group = gis.groups.search(query = 'title: "NCR Regional Datasets INTERNAL Download"')
#        for group_item in group.content():
#            print(group_item)
#        # Search items by username
#        #items = gis.content.search(query='owner:ncrgis', item_type='File Geodatabase')
#        #print(items)
#        ## Loop through each item and if equal to Feature Service then download it
#        #for item in items:
#        #    print(item)
#        #    result = item.export(item.title, downloadFormat)
#        #    data_path = Path(r'C:\Users\goettel\OneDrive - DOI\Documents\GIS\Geodata\NPS_Regional_Data')
#        #    result.download(save_path=data_path)

## Function takes in two parameters. Username, and the type of download format.
#downloadUserItems('ncrgis', downloadFormat='File Geodatabase')
#print("All items downloaded")

#def download_ncr_gdb(download_path, file_type):
#    groups = gis.groups.search(query = 'title: "NCR Regional Datasets INTERNAL Download"')
#    for group in groups:
#        for group_item in group.content():
#            #print(group_item)
#            if group_item.title == 'NCR Regional Geodatabase INTERNAL':
#                result = group_item.export(group_item.title, file_type)
#                result.download(save_path = download_path)
#                print('Successfully downloaded file! (in theory)')

download_path = r'C:\Users\goettel\OneDrive - DOI\Documents\GIS\Geodata\NPS_Regional_Data'
#file_type = 'File Geodatabase'

#download_ncr_gdb(download_path, file_type)

# 'NCR Regional Geodatabase INTERNAL' = 'NCR_Regional_Datasets_INTERNAL.gdb.zip
#gdb_item = gis.content.get('b3c18dafc7de437bb1621b77f6669c8a')
##gdb_item.get_data()
#path = gdb_item.download(download_path)


## Full list of NWI URLs for testing
#wetland_urls = [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip', 
#                r'https://www.fws.gov/wetlands/Data/State-Downloads/MD_shapefile_wetlands.zip',
#                r'https://www.fws.gov/wetlands/Data/State-Downloads/VA_shapefile_wetlands.zip',
#                r'https://www.fws.gov/wetlands/Data/State-Downloads/WV_shapefile_wetlands.zip']

## Partial list of NWI URLs for testing
#wetland_urls = [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip']

## Out directory for testing downloads
#out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## Test get_file_size_requests on list or ZIP URLs
#for url in wetland_urls:
#    print(get_file_size_requests(url))

## Test download_url_wget on NWI Wetlands ZIP URLs
#download_url_wget(out_dir, wetland_urls)
