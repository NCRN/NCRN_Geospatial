import wget

url = r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip'

def bar_custom(current, total, width=80):
  print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total))
  
wget.download(url, bar=bar_custom)