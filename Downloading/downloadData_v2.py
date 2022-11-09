# https://stackoverflow.com/questions/72088811/how-to-download-a-large-zip-file-25-gb-using-python
# https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests

import datetime 
import requests
import wget

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

def download_url_wget(out_dir, url_list):
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





########### TESTING ##########
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


########## DOWNLOAD ALL URLs SCRIPT ##########

##### NHD Plus HR #####

# Full list of nhd plus urls for download
nhdplus_urls = [r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_0207_HU4_GDB.zip', 
                r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/NHDPLUS_H_0206_HU4_GDB.zip']

## Out directory for downloads
#nhdplus_out_dir = r''

# Test get_file_size_requests on list or ZIP URLs
for url in nhdplus_urls:
    print(get_file_size_requests(url))

## download_url_wget on nhd plus zip urls
#download_url_wget(nhdplus_out_dir, nhdplus_urls)

##### TIGER Census Boundaries #####

## Partial list of tiger urls for download
tiger_urls = [r'https://www2.census.gov/geo/tiger/TGRGDB22/tlgdb_2022_a_us_substategeo.gdb.zip']

### out directory for tiger downloads
#tiger_out_dir = r''

## cannot get_file_size_requests on list of nhd plus downloads. error

### download_url_wget on nhd plus zip urls
#download_url_wget(tiger_out_dir, tiger_urls)

##### Open Street Map #####
# Full list of OSM geofabrik urls for download
osm_urls = [r'http://download.geofabrik.de/north-america/us/district-of-columbia-latest-free.shp.zip', 
            r'http://download.geofabrik.de/north-america/us/maryland-latest-free.shp.zip',
            r'http://download.geofabrik.de/north-america/us/virginia-latest-free.shp.zip',
            r'http://download.geofabrik.de/north-america/us/west-virginia-latest-free.shp.zip']

## Out directory for downloads
#osm_out_dir = r''

# Test get_file_size_requests on list or ZIP URLs
for url in osm_urls:
    print(get_file_size_requests(url))

### download_url_wget on osm zip urls
#download_url_wget(osm_out_dir, osm_urls)

##### NED #####
# Full list of NED urls for download
ned_urls = [r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w079/USGS_13_n40w079_20220429.tif', 
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w078/USGS_13_n40w078_20220429.tif',
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n40w077/USGS_13_n40w077_20220524.tif',
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n39w078/USGS_13_n39w078_20220524.tif',
            r'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n39w077/USGS_13_n39w077_20220713.tif']

## Out directory for downloads
#ned_out_dir = r''

# Test get_file_size_requests on list or ZIP URLs
for url in ned_urls:
    print(get_file_size_requests(url))

### download_url_wget on ned zip urls
#download_url_wget(ned_out_dir, ned_urls)

##### NWI #####
# Full list of NWI urls for download
nwi_urls = [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip', 
            r'https://www.fws.gov/wetlands/Data/State-Downloads/MD_shapefile_wetlands.zip',
            r'https://www.fws.gov/wetlands/Data/State-Downloads/VA_shapefile_wetlands.zip',
            r'https://www.fws.gov/wetlands/Data/State-Downloads/WV_shapefile_wetlands.zip']

## Out directory for downloads
#nwi_out_dir = r''

# Test get_file_size_requests on list or ZIP URLs
for url in nwi_urls:
    print(get_file_size_requests(url))

### download_url_wget on nwi zip urls
#download_url_wget(nwi_out_dir, nwi_urls)