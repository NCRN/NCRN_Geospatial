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





########## TESTING ##########
# Full list of NWI URLs for testing
#wetland_urls = [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip', 
#                r'https://www.fws.gov/wetlands/Data/State-Downloads/MD_shapefile_wetlands.zip',
#                r'https://www.fws.gov/wetlands/Data/State-Downloads/VA_shapefile_wetlands.zip',
#                r'https://www.fws.gov/wetlands/Data/State-Downloads/WV_shapefile_wetlands.zip']

# Partial list of NWI URLs for testing
wetland_urls = [r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip']

# Out directory for testing downloads
out_dir = r'C:\_GIS\TEST2'


# Test get_file_size_requests on list or ZIP URLs
#for url in wetland_urls:
#    print(get_file_size_requests(url))

# Test download_url_wget on NWI Wetlands ZIP URLs
download_url_wget(out_dir, wetland_urls)