#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial working script for downloading GIS data and formatting the NCRN GIS Library.
--------------------------------------------------------------------------------
TODO: Add more of a complete description (once the MVP is working and refactored.)

References:
# https://stackoverflow.com/questions/72088811/how-to-download-a-large-zip-file-25-gb-using-python
# https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
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
import geopandas as gpd
import os
import pandas as pd
import rasterstats
import requests
import streamstats
import wget

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
Some of these global variables may not be in use yet.
"""

# Set the directory path to the root directory that will be documented
__WORKSPACE = r'U:\GIS'

# Set the directory path to the root directory that will be documented
__ROOT_DIR = r'C:\_GIS\WATER'

# Create a variable to store the file extension for file geodatabases
__FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
__SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
__EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (that are outside of FGDBs)
__RAST_EXT = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.sid', '.bmp'] # Logical variable to parameterize for toolbox and/or command line

# Create a variable to store the full path to the GIS Library sources Excel file
__XCEL_LIBRARY = r'C:\Users\dgjones\DOI\NCRN Data Management - GIS\NCRN-GIS-Data-Sources.xlsx'

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
    print("The file is downloading.....Please be patient!\nStart time: {0}\n".format(str(datetime.datetime.time(start_dtm))))        
    # Call the wget.download function with the url and output directory as variables
    wget.download(url=url, out=out_dir, bar=download_progress_bar_custom)
    # Create a datetime object for current date/time after download
    end_dtm = datetime.datetime.now()
    # Create a variable to store the time elapsed during download
    diff_dtm = end_dtm - start_dtm
    # Print status to Python console with where the file was downloaded and how long it took
    print("The file downloaded to: {0}.\nDownload time: {1}".format(out_dir,str(diff_dtm)))

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

## Full list of nhd plus urls for download
#nhdplus_urls = [r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_0207_HU4_GDB.zip',
#                r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_0206_HU4_GDB.zip']

#nhd_download_dir = r'C:\_GIS\WATER\Vector\Hydrology\NHDPLUS'

#download_url_list_wget(nhd_download_dir, nhdplus_urls)

wq_sites_dict = {0:[39.449701,-77.730321], 
                1:[39.45493,-77.737773], 
                2:[39.626153,-77.440433], 
                3:[39.660679,-77.481992], 
                4:[39.633338,-77.450409], 
                5:[38.976696,-77.244384], 
                6:[38.919468,-77.108308], 
                7:[38.924962,-77.114078], 
                8:[38.968183,-77.138701], 
                9:[38.999944,-77.256167], 
                10:[38.93049,-77.11899], 
                11:[38.963209,-77.157671], 
                12:[39.295894,-77.792258], 
                13:[38.81773,-77.528128], 
                14:[38.814173,-77.543967], 
                15:[38.815771,-77.507193], 
                16:[38.817783,-77.510283], 
                17:[39.369119,-77.385475], 
                18:[39.368497,-77.388681], 
                19:[39.359295,-77.400905], 
                20:[38.690659,-77.054486], 
                21:[38.88132,-76.957333], 
                22:[38.834611,-76.900599], 
                23:[38.81229,-77.007302], 
                24:[38.972989,-76.914109], 
                25:[38.566609,-77.3641], 
                26:[38.566576,-77.364618], 
                27:[38.577732,-77.417682], 
                28:[38.568083,-77.360755], 
                29:[38.557815,-77.423806], 
                30:[38.572725,-77.347316], 
                31:[38.565084,-77.425761], 
                32:[38.544425,-77.40029], 
                33:[38.562378,-77.357539], 
                34:[38.57194,-77.347137], 
                35:[38.572653,-77.347376], 
                36:[38.566573,-77.352963], 
                37:[38.57647,-77.381416], 
                38:[38.575788,-77.375135], 
                39:[38.920314,-77.099383], 
                40:[38.944988,-77.050354], 
                41:[38.915841,-77.059136], 
                42:[38.920857,-77.050336], 
                43:[38.984798,-77.042041], 
                44:[38.938327,-77.051926], 
                45:[38.933285,-77.051822], 
                46:[38.961686,-77.041589], 
                47:[38.919225,-77.05591], 
                48:[38.972064,-77.043732], 
                49:[38.93552,-77.046785], 
                50:[38.915659,-77.058711], 
                51:[38.98404,-77.042985], 
                52:[38.945265,-77.051771], 
                53:[38.939716,-77.262698], 
                54:[38.941112,-77.26802]}

for k, v in wq_sites_dict.items():
    ws = streamstats.Watershed(v[0], v[1])
    ws.boundary
    poly = gpd.GeoDataFrame.from_features(ws.boundary["features"], crs="EPSG:4326")
    ax = poly.plot(figsize=(20, 10), edgecolor='k')
    ax.set_title("Single Watershed", fontsize=30, fontweight = 'bold')
    ax.set_axis_off()