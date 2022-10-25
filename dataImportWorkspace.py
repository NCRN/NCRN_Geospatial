#Download standard ZIP file
import wget

url = r'https://water.usgs.gov/GIS/dsdl/gagesII_9322_point_shapefile.zip'

def bar_custom(current, total, width=80):
    print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total))
  
wget.download(url, bar=bar_custom)

