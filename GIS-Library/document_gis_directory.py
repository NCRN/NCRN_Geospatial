#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document a GIS directory.
--------------------------------------------------------------------------------

References:
https://www.thepythoncode.com/article/get-directory-size-in-bytes-using-python
"""

What we are trying to do with this script...
OVERARCHING GOAL: Automate the documentation of GIS datasets in a root directory and write key information to an Excel file
We are trying to right to an Excel that is similar to this: https://doimspp.sharepoint.com/sites/NCRNDataManagement/Shared%20Documents/Geospatial/NCRN_GIS_Drive_Contents.xlsx
BACKGROUND:
Looped over the root directory in a few different ways to get unique lists of FGDBs, Shapefiles, and Raster files
Later merged these three lists and looped over the big list passing each item to desc_spatial_data_file
1) Need to loop over the root directory and find all the FGDBs (Phase 2: and we'll eventually need to write some code to find the .mdbs - Personal Geodatabases)
  a) Write those to a tab on the Excel Workbook called 'FGDBs'
  Phase 2: Later we will write some code to count the feature datasets and feature classes and find the file size of the FGDBs
2) Refactor code written below that looks at FGDBs and other GIS datasets to document their properties

References:
https://www.thepythoncode.com/article/get-directory-size-in-bytes-using-python

"""

#__author__ = "David Jones"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.1"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"

# Import statements for utilized libraries / packages
import arcpy
import glob
import os
import scandir
import pandas as pd
from openpyxl import load_workbook
import os
import arcpy
from arcpy import env
import pathlib
import pandas
import time


"""
Set various global variables. Some of these could be parameterized to be used as an 
ArcGIS Toolbox script and/or command line use.
"""
# Set the directory path to the root directory that will be documented
#_WORKSPACE = r'C:\_GIS' # Logical variable to parameterize for toolbox and/or command line
_WORKSPACE = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\GIS\Geodata'
_WORKSPACE_PREFIX = r'C:\Users\goettel\DOI'
#_WORKSPACE = r'C:\Users\dgjones\DOI\NCRN Data Management - Documents\GIS'

# Create a variable to store the file extension for file geodatabases
_FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
_SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
_EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (outside FGDBs)
_RAST_EXT = ['.tif', '.tiff', '.jpg', '.jpeg', '.png', '.sid', '.bmp'] # Logical variable to parameterize for toolbox and/or command line

# Create some lists to be used in various places
dirs = []
fgdb_list = []
shp_list = []
rast_list = []

### NOTE: Not all of the utility functions below ended up being used. There was a lot of trial and error.

def get_files_glob(base_dir, ext):
    """Gets a glob of file paths that .

    Args:
        in_file: A full file path string of file to read.
    Returns:
        A list of full path names of MS Access files in directory.

    Raises:
        TODO: IOError: An error occurred accessing the smalltable.
    """    
    return glob.iglob(rf"{base_dir}\**\*{ext}", recursive=True)


def get_directory_total_size(directory):
    """Returns the `directory` size in bytes."""
    total_size = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # If it's a file, use stat() function
                total_size += entry.stat().st_size
            elif entry.is_dir():
                # If it's a directory, recursively call this function
                try:
                    total_size += get_directory_total_size(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    #return [total_size, count_files, count_dirs]
    return total_size

def get_directory_count(directory):
    """Returns the `directory` size in bytes."""
    total_count = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_dir() and _FGDB_EXT not in str(entry):
                # Increment the directory counter
                total_count = total_count + 1
                # If it's a directory, recursively call this function
                try:
                    total_count += get_directory_count(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    #return [total_size, count_files, count_dirs]
    return total_count

### TODO: Needs tweaking. Still counting FGDB files I think.
def get_file_count(directory):
    """Returns the `directory` size in bytes."""
    total_count = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file() and str(entry).split('.')[-1] not in _EXCLUDE_EXT:
                # Increment the file counter
                total_count = total_count + 1
                # If it's a directory, recursively call this function
                try:
                    total_count += get_file_count(entry.path)
                except FileNotFoundError:
                    pass
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    #return [total_size, count_files, count_dirs]
    return total_count

def get_size_format(bytes, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
    return f"{bytes:.2f}Y{suffix}"

def get_folder_size(path='.'):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total/1024/1024 # MB

# TODO: Needs documentation, needs not to be a print statement but write to Excel
#def get_gdbs_list(in_dir):
#    for f in get_files_glob(in_dir, _FGDB_EXT):
#        print(os.path.join(os.path.dirname(f), os.path.basename(f)))

## OLD FUNCTION TO GET GDBs LIST
#def get_gdbs_list(rootdir):
#    gdbs_list = []
#    for it in os.scandir(rootdir):
#        if it.is_dir() and _FGDB_EXT in str(it.path):
#            gdbs_list.append(it.path)
#            #listdirs(it)
#        elif it.is_dir():
#            get_gdbs_list(it)

# THIS IS KEEP -> USED LIST COMPREHENSION TO GET THE FULL LIST OF SHAPEFILES IN THE ROOT DIRECTORY
shp_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _SHP_EXT)]

#for rast_ext in _RAST_EXT:
#    glob_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, rast_ext)]
#    if len(glob_list):
#        rast_list.append(glob_list)

#file_list = fgdb_list + shp_list + rast_list

#def desc_spatial_data_file(file_list):
#    master_list = []
#    counter = 0
#    for file in file_list:
#        if _FGDB_EXT in file:
#            print('Starting processing for:{0}'.format(file))
#            arcpy.env.workspace = file           
#            datasets = arcpy.ListDatasets(feature_type='feature')
#            print('Finished getting dataset list...')
#            datasets = [''] + datasets if datasets is not None else []
#            for ds in datasets:
#                print('Looping over feature classes...')
#                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
#                    print('Processing a feature class...')
#                    full_file = os.path.join(arcpy.env.workspace, ds, fc)
#                    try:
#                        desc = arcpy.Describe(fc)
#                        try:
#                            spatial_ref = arcpy.Describe(fc).SpatialReference
#                            srs_name = spatial_ref.Name
#                        except:
#                            srs_name = 'Unknown'
#                            pass
#                        print([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
#                    except:
#                        print([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, 'FC does not exist'])
#                        pass
#                    #master_list.append([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
#                    #counter = counter + 1
#                    #print(counter)
#        elif _SHP_EXT in file:
#            ext = _SHP_EXT.strip('.')
#            desc = arcpy.Describe(file)                
#            try:
#                spatial_ref = arcpy.Describe(file).SpatialReference
#                srs_name = spatial_ref.Name
#            except:
#                srs_name = 'Unknown'
#                pass
#            print([file, os.path.dirname(file), 'NA', ext, desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
#        #elif os.path.splitext(file)[1] in _RAST_EXT:
#        elif _RAST_EXT in file:
#            ext = os.path.splitext(file)[1]
#            desc = arcpy.Describe(file)
#            try:
#                spatial_ref = arcpy.Describe(file).SpatialReference
#                srs_name = spatial_ref.Name
#            except:
#                srs_name = 'Unknown'
#                pass  
#            print([file, os.path.dirname(file), 'NA', 'NA', ext, os.path.basename(file), 'Raster', desc.compressionType, 'Raster', srs_name, desc.bandCount])
#            #master_list.append([file, os.path.dirname(file), 'NA', 'NA', ext, file_name, 'Raster', desc.compressionType, 'Raster', srs_name, desc.bandCount])
#    return master_list

# IGNORE THIS -> NOT WHAT WAS USED TO GET THE LIST OF GDBs
#for root, dirs, files in scandir.walk(_WORKSPACE):
#    for dir in dirs:
#        if str(dir).endswith(_FGDB_EXT):
#            fgdb_list.append(os.path.join(root, dir))
#    for file in files:
#        #print(file)
#    #append the file name to the list
#        if file.endswith(_SHP_EXT):
#            shp_list.append(os.path.join(root, file))
#        elif file.split('.')[-1] in _RAST_EXT:
#            rast_list.append(os.path.join(root, file))

#for gdb in fgdb_list:
#    print(gdb)
=======
#def get_folder_size(path='.'):
    #total = 0
    #for entry in os.scandir(path):
        #if entry.is_file():
            #total += entry.stat().st_size
        #elif entry.is_dir():
            #total += get_folder_size(entry.path)
    #return total/1024/1024 # MB

def get_gdbs_list(rootdir):
    gdbs_list = []
    for it in os.scandir(rootdir):
        if it.is_dir() and _FGDB_EXT in str(it.path):
            gdbs_list.append(it.path)
            #listdirs(it)
        elif it.is_dir():
            get_gdbs_list(it)

def desc_spatial_data_file(file_list):
    master_list = []
    counter = 0
    for file in file_list:
        if _FGDB_EXT in file:
            #print('Starting processing for:{0}'.format(file))
            arcpy.env.workspace = file           
            datasets = arcpy.ListDatasets(feature_type='feature')
            #print('Finished getting dataset list...')
            datasets = [''] + datasets if datasets is not None else []
            
            for ds in datasets:
                #print('Looping over feature classes...')
                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                    #print('Processing a feature class...')
                    full_file = os.path.join(arcpy.env.workspace, ds, fc)
                    try:
                        desc = arcpy.Describe(fc)
                        try:
                            spatial_ref = arcpy.Describe(fc).SpatialReference
                            srs_name = spatial_ref.Name
                        except:
                            srs_name = 'Unknown'
                            pass
                        print([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
                    except:
                        print([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, 'FC does not exist'])
                        pass
                    #master_list.append([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
                    #counter = counter + 1
                    #print(counter)
        elif _SHP_EXT in file:
            ext = _SHP_EXT.strip('.')
            desc = arcpy.Describe(file)                
            try:
                spatial_ref = arcpy.Describe(file).SpatialReference
                srs_name = spatial_ref.Name
            except:
                srs_name = 'Unknown'
                pass
            print([file, os.path.dirname(file), 'NA', ext, desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
        elif os.path.splitext(file)[1] in _RAST_EXT:
            ext = os.path.splitext(file)[1]
            desc = arcpy.Describe(file)
            try:
                spatial_ref = arcpy.Describe(file).SpatialReference
                srs_name = spatial_ref.Name
            except:
                srs_name = 'Unknown'
                pass  
            print([file, os.path.dirname(file), 'NA', 'NA', ext, os.path.basename(file), 'Raster', desc.compressionType, 'Raster', srs_name, desc.bandCount])
            #master_list.append([file, os.path.dirname(file), 'NA', 'NA', ext, file_name, 'Raster', desc.compressionType, 'Raster', srs_name, desc.bandCount])

    return master_list

for root, dirs, files in scandir.walk(_WORKSPACE):
    for dir in dirs:
        if str(dir).endswith(_FGDB_EXT):
            fgdb_list.append(os.path.join(root, dir))
    #for file in files:
    #    #print(file)
    ##append the file name to the list
    #    if file.endswith(_SHP_EXT):
    #        shp_list.append(os.path.join(root, file))
    #    elif file.split('.')[-1] in _RAST_EXT:
    #        rast_list.append(os.path.join(root, file))

for gdb in fgdb_list:
    print(gdb)
#file_list = fgdb_list + shp_list + rast_list

#for files in scandir.walk(workspace):
    #if files.path.endswith(limited_exts):
        #print(files)
    
#spatial_file_info = desc_spatial_data_file(file_list)

#for item in spatial_file_info:
    #print('{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}'.format(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]))
    
#print(get_folder_size(_WORKSPACE))

#dir_stats = get_directory_stats(_WORKSPACE)

#print('Total # Files: {0}\nTotal # Folders: {1}\nTotal Size: {2}'.format(dir_stats[1], dir_stats[2], get_size_format(dir_stats[0])))


#fgdbs_giant_list = [original big ass list of fgdb files]

##fgdbs_smaller_list = [r'U:\GIS\WOTR\WOTR_NRCA_Basedata.gdb', r'U:\GIS\WOTR\WOTR_ParkAtlas.gdb']

#fgdbs_giant_list = []

##fgdbs_smaller_list = [r'U:\GIS\WOTR\WOTR_NRCA_Basedata.gdb',
##r'U:\GIS\WOTR\WOTR_ParkAtlas.gdb']

##shp_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _SHP_EXT)]

##for rast_ext in _RAST_EXT:
#    #glob_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, rast_ext)]
#    #if len(glob_list):
#        #rast_list.append(glob_list)

##import numpy as np

##def numpy_flat(arr):
#    #return list(np.array(arr).flat)

##rast_list = numpy_flat(rast_list)

##print(shp_list)
##print(rast_list)

##file_list = fgdbs_smaller_list #+ shp_list #+ rast_list

##file_list = [r'U:\GIS\ANTI\ANTI_ParkAtlas.gdb']

##print('Processing...')

#file_list = []

#exclude_fgdbs = set([big ass list of gdbs with full file path])

#exclude_folders = []

#exclude = fgdbs_giant_list + exclude_folders

#for root, dirs, files in os.walk(top=_WORKSPACE, topdown=True):
    #dirs[:] = [d for d in dirs if d not in exclude_fgdbs]
    #files[:] = [f for f in files if os.path.splitext(f)[1] in _RAST_EXT]
    #for f in files:
        ##print(os.path.dirname(f))
        ##print(os.path.join(root, f))
        #file_list.append(os.path.join(root, f))
        
#print('Finished getting list of files...')
#print(file_list)

#test_list = [r'U:\GIS\CATO\Elevation\Hypsography\CATO_Hypso_USGS.shp']

#spatial_file_info = desc_spatial_data_file(file_list)

#for gdb in fgdbs_giant_list:
    #arcpy.env.workspace = gdb
    #rasters = arcpy.ListRasters("*")
    #for raster in rasters:
        #try: 
            #desc = arcpy.Describe(raster)
            #try:
                #spatial_ref = arcpy.Describe(raster).SpatialReference
                #srs_name = spatial_ref.Name
            #except:
                #srs_name = 'Unknown'
                #pass  
            #print([os.path.join(gdb,raster),gdb,'NA','NA','NA',raster,'Raster',desc.compressionType,'Raster',srs_name,desc.bandCount])
        #except:
            #print([os.path.join(gdb,raster),gdb,'NA','NA','NA',raster,'Raster','FC does not exist'])
            #pass            

        #master_list.append([full_file, os.path.dirname(file), ds, 'NA', desc.baseName, desc.dataType, desc.shapeType, srs_name, ''])
        #counter = counter + 1
        #print(counter)    

#spatial_file_info = desc_spatial_data_file(giant_shp_list)

#print('Finished analyzing FGDB...')

#for item in spatial_file_info:
    #print('{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}'.format(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]))

#print(get_size_format(get_directory_total_size(_WORKSPACE)))

#print(get_directory_count(_WORKSPACE))

#print(get_file_count(_WORKSPACE))

#for gdb in fgdbs_giant_list:
    #print(gdb, "|", gdb.split('\\')[-1])

#for root, dirs, files in os.walk(top=_WORKSPACE, topdown=True):
#    dirs[:] = [d for d in dirs if d not in exclude]
#    for d in dirs:
#        arcpy.env.workspace = os.path.join(root,d)
#        rasters = arcpy.ListRasters("*", "GRID")
#        if len(rasters) != 0:
#            for raster in rasters:
#                try: 
#                    desc = arcpy.Describe(raster)
#                    try:
#                        spatial_ref = arcpy.Describe(raster).SpatialReference
#                        srs_name = spatial_ref.Name
#                    except:
#                        srs_name = 'Unknown'
#                        pass  
#                    print([os.path.join(root,d,raster),os.path.join(root,d),'NA','NA','NA',raster,'Grid',desc.compressionType,'Raster',srs_name,desc.bandCount])
#                except:
#                    print([os.path.join(root,d,raster),os.path.join(root,d),'NA','NA','NA',raster,'Grid','FC does not exist'])
#                    pass
#        else:
#            print("|Directory has no rasters: {0}".format(arcpy.env.workspace))
        #except:
            #print("|Directory has no rasters: {0}".format(arcpy.env.workspace))
            #pass

#############################ACTIVE CODE#############################

fgdb_path_list = []
fgdb_name_list = []
fgdb_filesize_list = []
fgdb_featuredatasetcount_list = []
fgdb_featureclasscount_list = []
fgdb_tablecount_list = []
fgdb_featureclassname_list = []
full_name_list = []
location_list = []
container_list = []
featuredataset_list = []
ext_list = []
name_list = []
datatype_list = []
filetype_list = []
geometrytype_list = []
srs_list = []
bandcount_list = []
sizekb_list = []
sizemb_list = []
createddate_list = []
modifieddate_list = []

#Create list of FGDB paths
print("Finding FGDB Path")
for root, dirs, files in scandir.walk(_WORKSPACE):
    for dir in dirs:
        if str(dir).endswith(_FGDB_EXT):
            fgdb_list.append(os.path.join(root, dir))
for gdb in fgdb_list:
    path = gdb.removeprefix(r"C:\Users\goettel\DOI")
    fgdb_path_list.append(path)

##Create list of FGDB names
print("Finding FGDB Name")
for gdb in fgdb_list:
    fgdb_name = os.path.basename(gdb).split('/')[-1]
    fgdb_name_list.append(fgdb_name)    

#Create list of FGDB file sizes
print("Finding File Size")
for gdb in fgdb_list:
    filesize = get_size_format(get_folder_size(gdb))
    fgdb_filesize_list.append(filesize)

#Create list of FGDB feature dataset count
print("Finding Feature Dataset Count")
for gdb in fgdb_list:
    arcpy.env.workspace = gdb
    fds = arcpy.ListDatasets("","")
    fgdb_featuredatasetcount_list.append(len(fds))

#Create list of FGDB feature class count
print("Finding Feature Class Count")
for gdb in fgdb_list:
    workspace = gdb
    feature_classes = []
    for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,
                                                  datatype="FeatureClass",
                                                  type="Any"):
        for filename in filenames:
            feature_classes.append(os.path.join(dirpath, filename))
    featureclasscount = len(feature_classes)
    fgdb_featureclasscount_list.append(featureclasscount)

#Create list of FGDB table count
print("Finding Table Count")
for gdb in fgdb_list:
    workspace = gdb
    tables = []
    for dirpath, dirnames, filenames in arcpy.da.Walk(workspace,
                                                  datatype="Table",
                                                  type="Any"):
        for filename in filenames:
            tables.append(os.path.join(dirpath, filename))
    tablecount = len(tables)
    fgdb_tablecount_list.append(tablecount)

#Create list of FGDB feature class names
for gdb in fgdb_list:
    arcpy.env.workspace = gdb
    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []
    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            path = os.path.join(arcpy.env.workspace, ds, fc)
            fgdb_featureclassname_list.append(path)

#Add FGDB rasters to list of FGDB feature class names
for gdb in fgdb_list:
    arcpy.env.workspace = gdb
    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []
    for ds in datasets:
        for r in arcpy.ListRasters("*", "GRID"):
            path = os.path.join(arcpy.env.workspace, ds, r)
            fgdb_featureclassname_list.append(path)

#Create list of raster names
glob_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _RAST_EXT)]
for file in glob_list:
    if os.path.splitext(file)[1] in _RAST_EXT:
        rast_list.append(file)

#Create list of Full Names
print("Finding Full Name")
file_list = fgdb_featureclassname_list + shp_list + rast_list
for file in file_list:
    path = file.removeprefix(_WORKSPACE_PREFIX)
    full_name_list.append(path)

###Create list of Full Name Locations
#Function to remove fgdb and feature dataset from Location
def get_geodatabase_path(file):
    workspace = os.path.dirname(file)
    if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace)]:
        return workspace
    else:
        return os.path.dirname(workspace)
gdb = "gdb"

print("Finding Location")
for file in file_list:    
    if _FGDB_EXT in file:
        gdb_path_full = get_geodatabase_path(file)
        gdb_path = gdb_path_full.removeprefix(_WORKSPACE_PREFIX)
        location = os.path.dirname(gdb_path)
        location_list.append(location)
    else:
        location_full = os.path.dirname(file)
        location = location_full.removeprefix(_WORKSPACE_PREFIX)
        location_list.append(location)

#Create list of Containers
print("Finding Container")
for file in file_list:
    if _FGDB_EXT in file:
        gdb_path = get_geodatabase_path(file)
        container = os.path.basename(gdb_path).split('/')[-1]
        container_list.append(container)
    else: 
        container = "NA"
        container_list.append(container)

#Create list of feature datasets
print("Finding FeatureDataset")
for file in file_list:
    if _FGDB_EXT in file:
        try:
            desc = arcpy.Describe(file)
            if hasattr(desc, 'path'):
                descPth = arcpy.Describe(desc.path)
                if hasattr(descPth, 'dataType'):
                    if descPth.dataType == 'FeatureDataset':
                        featuredataset_list.append(descPth.name)
                    else:
                        featuredataset_list.append("NA")
        except:
            featuredataset_list.append("Unknown")
    else:
        featuredataset_list.append("NA")
    
#Create list of extension formats
print("Finding Extension/Format")
for file in file_list:
    ext = pathlib.Path(file).suffix
    ext_list.append(ext)
    for ext in range(len(ext_list)):
        if ext_list[ext] == '':
            ext_list[ext] = "NA"

#Create list of names
print("Finding Name")
for file in file_list:
    filename = os.path.basename(file).split('/')[-1]
    name_list.append(filename)

#Create list of data types
print("Finding Data Type")
for file in file_list:
    if _FGDB_EXT in file:
        try:
            desc = arcpy.Describe(file)
            geometrytype = desc.shapeType
            if (geometrytype == "Polygon") or (geometrytype == "Polyline") or (geometrytype == "Point") or (geometrytype == "Multipoint"):
                datatype = "Vector"
                datatype_list.append(datatype)
            else: 
                datatype_list.append("FGDB Raster")
        except:
            datatype_list.append("Unknown")
    elif _SHP_EXT in file:
        datatype_list.append("Vector")
    elif os.path.splitext(file)[1] in _RAST_EXT:
        datatype_list.append("Raster")

#Create list of file types
print("Finding File Type / Compression")
for file in file_list:  
    if _FGDB_EXT in file:
        try:
            desc = arcpy.Describe(file)
            filetype = desc.dataType
            filetype_list.append(filetype)
        except:
            filetype_list.append("Unknown")
    elif _SHP_EXT in file:
        desc = arcpy.Describe(file)
        filetype = desc.dataType
        filetype_list.append(filetype)   
    elif os.path.splitext(file)[1] in _RAST_EXT:
        ext = os.path.splitext(file)[1]
        desc = arcpy.Describe(file)
        filetype = desc.compressionType
        filetype_list.append(filetype)
    
#Create list of geometry types
print("Finding Geometry Type")
for file in file_list:
    if _FGDB_EXT in file:
        try:
            desc = arcpy.Describe(file)
            geometrytype = desc.shapeType
            geometrytype_list.append(geometrytype)
        except:
            geometrytype_list.append("Unknown")
    elif _SHP_EXT in file:
        desc = arcpy.Describe(file)
        geometrytype = desc.shapeType
        geometrytype_list.append(geometrytype)   
    elif os.path.splitext(file)[1] in _RAST_EXT:
        geometrytype = "Raster"
        geometrytype_list.append(geometrytype)

#Create list of srs
print("Finding SRS")
for file in file_list:
    try:
        spatial_ref = arcpy.Describe(file).SpatialReference
        srs = spatial_ref.Name
    except:
        srs = 'Unknown'
    srs_list.append(srs)

#Create list of band count
print("Finding Band Count")
for file in file_list:
    try:
        desc = arcpy.Describe(file)
        bandcount = desc.bandCount
    except:
        bandcount = "NA/Unknown"
    bandcount_list.append(bandcount)

#Create list of file sizes in kb and mb
def get_size(file, unit='bytes'):
    try:
        file_size = os.path.getsize(file)
        exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)
    except:
        size = None
print("Finding Size")
for file in file_list:
    if get_size(file, 'kb') == None:
        sizekb_list.append('Unknown')
    else:
        sizekb_list.append(get_size(file, 'kb'))
for file in file_list:
    if get_size(file, 'mb') == None:
        sizemb_list.append('Unknown')
    else:
        sizemb_list.append(get_size(file, 'mb'))

#Create list of create and modify date
for file in file_list:
    if _FGDB_EXT in file:
        pass
        createddate_list.append("Unknown")
        modifieddate_list.append("Unknown")
    else:
        ti_c = os.path.getctime(file)
        ti_m = os.path.getmtime(file)
        c_ti = time.ctime(ti_c)
        m_ti = time.ctime(ti_m)
        c_t_obj = time.strptime(c_ti)
        m_t_obj = time.strptime(m_ti)
        c_T_stamp = time.strftime("%Y-%m-%d", c_t_obj)
        createddate_list.append(c_T_stamp)
        m_T_stamp = time.strftime("%Y-%m-%d", m_t_obj)
        modifieddate_list.append(m_T_stamp)

#Set path to xlsx workbook and worksheet
wb = load_workbook(r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_GIS_Geospatial_Contents.xlsx')
ws1 = wb['FGDBs']
ws2 = wb['Main']

##Write FGDB Path to xlsx
fgdb_df = pd.DataFrame({'FGDB Path': fgdb_path_list})
for index, row in fgdb_df.iterrows():
    cell = 'A%d'  % (index + 2)
    ws1[cell] = row[0]
##Write FGDB Name to xlsx
fgdb_name_df = pd.DataFrame({'FGDB Name': fgdb_name_list})
for index, row in fgdb_name_df.iterrows():
    cell = 'B%d'  % (index + 2)
    ws1[cell] = row[0]
##Write File Size to xlsx
fgdb_filesize_df = pd.DataFrame({'File Size': fgdb_filesize_list})
for index, row in fgdb_filesize_df.iterrows():
    cell = 'C%d'  % (index + 2)
    ws1[cell] = row[0]
##Write Feature Dataset Count to xlsx
fgdb_featuredatasetcount_df = pd.DataFrame({'Feature Dataset Count': fgdb_featuredatasetcount_list})
for index, row in fgdb_featuredatasetcount_df.iterrows():
    cell = 'D%d'  % (index + 2)
    ws1[cell] = row[0]    
##Write Feature Class Count to xlsx
fgdb_featureclasscount_df = pd.DataFrame({'Feature Class Count': fgdb_featureclasscount_list})
for index, row in fgdb_featureclasscount_df.iterrows():
    cell = 'E%d'  % (index + 2)
    ws1[cell] = row[0]
##Write Table Count to xlsx
fgdb_tablecount_df = pd.DataFrame({'Table Count': fgdb_tablecount_list})
for index, row in fgdb_tablecount_df.iterrows():
    cell = 'F%d'  % (index + 2)
    ws1[cell] = row[0]
##Write Full Name to xlsx
fullname_df = pd.DataFrame({'Full Name': full_name_list})
for index, row in fullname_df.iterrows():
    cell = 'A%d'  % (index + 2)
    ws2[cell] = row[0]
##Write Full Name Location to xlsx
location_df = pd.DataFrame({'Location': location_list})
for index, row in location_df.iterrows():
    cell = 'B%d'  % (index + 2)
    ws2[cell] = row[0]
#Write Container to xlsx
container_df = pd.DataFrame({'Container': container_list})
for index, row in container_df.iterrows():
    cell = 'C%d'  % (index + 2)
    ws2[cell] = row[0]
#Write Feature Dataset to xlsx
featuredataset_df = pd.DataFrame({'FeatureDataset': featuredataset_list})
for index, row in featuredataset_df.iterrows():
    cell = 'D%d'  % (index + 2)
    ws2[cell] = row[0]
##Write Extension to xlsx
ext_df = pd.DataFrame({'Extension/Format': ext_list})
for index, row in ext_df.iterrows():
    cell = 'E%d'  % (index + 2)
    ws2[cell] = row[0]
##Write Name to xlsx
name_df = pd.DataFrame({'Name': name_list})
for index, row in name_df.iterrows():
    cell = 'F%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Data Type to xlsx
datatype_df = pd.DataFrame({'Data Type': datatype_list})
for index, row in datatype_df.iterrows():
    cell = 'G%d'  % (index + 2)
    ws2[cell] = row[0]
###Write File Type to xlsx
filetype_df = pd.DataFrame({'Data Type': filetype_list})
for index, row in filetype_df.iterrows():
    cell = 'H%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Geometry Type to xlsx
geometrytype_df = pd.DataFrame({'File Type / Compression': geometrytype_list})
for index, row in geometrytype_df.iterrows():
    cell = 'I%d'  % (index + 2)
    ws2[cell] = row[0]
###Write SRS to xlsx
srs_df = pd.DataFrame({'SRS': srs_list})
for index, row in srs_df.iterrows():
    cell = 'J%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Band Count to xlsx
bandcount_df = pd.DataFrame({'Band Count': bandcount_list})
for index, row in bandcount_df.iterrows():
    cell = 'K%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Size (KB) to xlsx
sizekb_df = pd.DataFrame({'Size (KB)': sizekb_list})
for index, row in sizekb_df.iterrows():
    cell = 'L%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Size (MB) to xlsx
sizemb_df = pd.DataFrame({'Size (KB)': sizemb_list})
for index, row in sizemb_df.iterrows():
    cell = 'M%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Created Date to xlsx
createddate_df = pd.DataFrame({'Created Date': createddate_list})
for index, row in createddate_df.iterrows():
    cell = 'N%d'  % (index + 2)
    ws2[cell] = row[0]
###Write Modified Date to xlsx
modifieddate_df = pd.DataFrame({'Last Modified Date': modifieddate_list})
for index, row in modifieddate_df.iterrows():
    cell = 'O%d'  % (index + 2)
    ws2[cell] = row[0]

#save xlsx changes
wb.save(r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_GIS_Geospatial_Contents.xlsx')
print("write successful!")
