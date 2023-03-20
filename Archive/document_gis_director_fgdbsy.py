import arcpy
import os
import scandir

workspace = r'C:\_GIS'
#workspace = r'U:\GIS

fgdb_ext = '.gdb'

#def listdirs(rootdir):
    #for it in os.scandir(rootdir):
        #if it.is_dir() and fgdb_ext in str(it.path):
            #print(it.path)
            ##listdirs(it)
        #elif it.is_dir():
            #listdirs(it)

##for stuff in os.scandir(workspace):
    ##if stuff.is_dir() and fgdb_ext in str(stuff):
        ##print(stuff.path)

#listdirs(workspace)

#from pathlib import Path

#def get_gdb_files(base_dir):
    #return Path(base_dir).glob("*/*.gdb")

#print(os.path.basename(get_gdb_files(workspace)))

import glob

def get_files_glob(base_dir, ext):
    return glob.iglob(rf"{base_dir}\**\*{ext}", recursive=True)

shp_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(workspace, shp_ext)]
for f in get_files_glob(workspace, fgdb_ext):
    print(os.path.join(os.path.dirname(f), os.path.basename(f)))