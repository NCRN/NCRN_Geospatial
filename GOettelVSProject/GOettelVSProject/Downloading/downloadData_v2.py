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
import os
import pandas as pd
import requests
import shutil
import wget
from zipfile import ZipFile


"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
Some of these global variables may not be in use yet.
"""

# Set the directory path to the root directory that will be documented
__WORKSPACE = r'U:\GIS'

# Set the directory path to the root directory that will be documented
__ROOT_DIR = r'C:\_GIS\DOWNLOAD'

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


###Setup progress bar

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
df_NCRN_GIS_Data_Sources = pd.read_excel(__XCEL_LIBRARY, sheet_name='Sources', usecols=['ID', 'Status', 'Is Zip', 'Web File for Download', 'Local Directory'])

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

#print(df_NCRN_GIS_Data_Sources_ready)


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



##########



########## DOWNLOAD ALL URLs SCRIPT ##########

##### NHD Plus HR #####

## Full list of nhd plus urls for download
nhdplus_urls = [r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_0207_HU4_GDB.zip',
                r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_0206_HU4_GDB.zip']

## Out directory for downloads
#nhdplus_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## test get_file_size_requests on list or zip urls
#for url in nhdplus_urls:
#    print('nhdplus', get_file_size_requests(url))

## download_url_wget on nhd plus zip urls
#download_url_wget(nhdplus_out_dir, nhdplus_urls)

##### TIGER Census Boundaries #####

## Full list of tiger urls for download
tiger_urls = [r'https://www2.census.gov/geo/tiger/TGRGDB22/tlgdb_2022_a_us_substategeo.gdb.zip']

## out directory for tiger downloads
#tiger_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## cannot get_file_size_requests on list of tiger downloads.

## download_url_wget on nhd plus zip urls
#download_url_wget(tiger_out_dir, tiger_urls)

##### Open Street Map #####
# Full list of OSM geofabrik urls for download
osm_urls = [r'http://download.geofabrik.de/north-america/us/district-of-columbia-latest-free.shp.zip', #dc
            r'http://download.geofabrik.de/north-america/us/maryland-latest-free.shp.zip', #md
            r'http://download.geofabrik.de/north-america/us/virginia-latest-free.shp.zip', #va
            r'http://download.geofabrik.de/north-america/us/west-virginia-latest-free.shp.zip'] #wv

## Out directory for downloads
#osm_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## Test get_file_size_requests on list or ZIP URLs
#for url in osm_urls:
#    print('osm', get_file_size_requests(url))

## download_url_wget on osm zip urls
#download_url_wget(osm_out_dir, osm_urls)

##### NED #####
# Full list of NED urls for download
ned_urls = [r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w079/USGS_13_n40w079_20220429.tif', 
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w078/USGS_13_n40w078_20220429.tif',
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w077/USGS_13_n40w077_20220524.tif',
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n39w078/USGS_13_n39w078_20220524.tif',
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n39w077/USGS_13_n39w077_20220713.tif']

## Out directory for downloads
#ned_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## Test get_file_size_requests on list or ZIP URLs
#for url in ned_urls:
#    print('ned', get_file_size_requests(url))

## download_url_wget on ned zip urls
#download_url_wget(ned_out_dir, ned_urls)

##### NWI #####
# Full list of NWI urls for download
nwi_urls = [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip', #dc
            r'https://www.fws.gov/wetlands/Data/State-Downloads/MD_shapefile_wetlands.zip', #md
            r'https://www.fws.gov/wetlands/Data/State-Downloads/VA_shapefile_wetlands.zip', #va
            r'https://www.fws.gov/wetlands/Data/State-Downloads/WV_shapefile_wetlands.zip'] #wv

## Out directory for downloads
#nwi_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

# Test get_file_size_requests on list or ZIP URLs
#for url in nwi_urls:
#    print('nwi', get_file_size_requests(url))

## download_url_wget on nwi zip urls
#download_url_wget(nwi_out_dir, nwi_urls)

##### USGS Gauge Locations #####
## Full list of usgs urls for download
usgs_urls = [r'https://water.usgs.gov/GIS/dsdl/gagesII_9322_point_shapefile.zip'] 

## Out directory for downloads
#usgs_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## Test get_file_size_requests on list or ZIP URLs
#for url in usgs_urls:
#    print('usgs', get_file_size_requests(url))

## download_url_wget on usgs zip urls
#download_url_wget(usgs_out_dir, usgs_urls)

##### EPA (303d, NPDES, and WATERS) #####
# Full list of EPA urls for download
epa_urls = [r'https://www.epa.gov/sites/default/files/2015-08/rad_303d_20150501_fgdb.zip', #303d
            r'https://echo.epa.gov/files/echodownloads/npdes_outfalls_layer.zip', #npdes
            r'https://watersgeo.epa.gov/GEOSPATIALDOWNLOADS/ATTAINS_Assessment_20220809_fgdb.zip'] #waters

## Out directory for downloads
#epa_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## Test get_file_size_requests on list or ZIP URLs
#for url in epa_urls:
#    print('epa', get_file_size_requests(url))

## download_url_wget on usgs zip urls
#download_url_wget(epa_out_dir, epa_urls)

##### SSURGO #####
# Full list of SSURGO urls for download
ssurgo_urls = [r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_DC001_soildb_US_2003_[2022-09-14].zip', #dc
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD017_soildb_US_2003_[2022-09-14].zip', #charles
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD033_soildb_US_2003_[2022-09-14].zip', #prince george's
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD003_soildb_US_2003_[2022-09-14].zip', #anne arundel
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD031_soildb_US_2003_[2022-09-14].zip', #montgomery
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD021_soildb_US_2003_[2022-09-14].zip', #frederick
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD043_soildb_US_2003_[2022-09-14].zip', #washington
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_MD001_soildb_US_2003_[2022-09-14].zip', #allegany
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_VA179_soildb_US_2003_[2022-08-22].zip', #stafford
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_VA153_soildb_US_2003_[2022-08-22].zip', #prince william
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_VA059_soildb_US_2003_[2022-08-26].zip', #fairfax
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_VA510_soildb_US_2003_[2022-08-22].zip', #alexandria
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_VA013_soildb_US_2003_[2022-08-23].zip', #arlington
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_VA107_soildb_US_2003_[2022-08-30].zip', #loudoun
               r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/SSA/wss_SSA_WV037_soildb_WV_2003_[2022-09-09].zip'] #jefferson
                
## Out directory for ssurgo downloads
#ssurgo_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## cannot get_file_size_requests on list of ssurgo downloads.

## download_url_wget on ssurgo zip urls
#download_url_wget(ssurgo_out_dir, ssurgo_urls)

##### STATSGO2 #####
# Full list of statsgo2 urls for download
statsgo2_urls = [r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/STATSGO2/wss_gsmsoil_DC_[2016-10-13].zip', #dc
                 r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/STATSGO2/wss_gsmsoil_MD_[2016-10-13].zip', #md
                 r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/STATSGO2/wss_gsmsoil_VA_[2016-10-13].zip', #va
                 r'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/Cache/STATSGO2/wss_gsmsoil_WV_[2016-10-13].zip'] #wv

## Out directory for ssurgo downloads
#statsgo2_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## cannot get_file_size_requests on list of statsgo2 downloads.

## download_url_wget on usgs zip urls
#download_url_wget(statsgo2_out_dir, statsgo2_urls)

##### HIFLD #####
# Full list of hifld urls for download
hifld_urls = [r'https://nps.maps.arcgis.com/sharing/rest/content/items/82ac410d9d9042788e29762f0a57f77b/data']

## Out directory for hifld downloads
#hifld_out_dir = r'C:\Users\goettel\OneDrive - DOI\Documents\GitHub\NCRN_Geospatial\Downloading\Downloads'

## Test get_file_size_requests on list or ZIP URLs
#for url in hifld_urls:
#    print('hifld', get_file_size_requests(url))

## download_url_wget on hifld zip urls
#download_url_wget(hifld_out_dir, hifld_urls)

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