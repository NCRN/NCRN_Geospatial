#Download file from link
import wget

url = r'https://www.fws.gov/wetlands/Data/State-Downloads/DC_shapefile_wetlands.zip'
wget.download(url)

#def bar_custom(current, total, width=80):
#    print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total))
  
#wget.download(url, bar=bar_custom)


#Download ZIP file from BOX
#import boxsdk
#file_id = '875227512344'
#file_content = client.file(file_id).content()