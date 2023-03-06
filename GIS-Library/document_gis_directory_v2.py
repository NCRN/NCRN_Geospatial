#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document a GIS directory.
--------------------------------------------------------------------------------

References:
https://www.thepythoncode.com/article/get-directory-size-in-bytes-using-python

#__author__ = "David Jones"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.1"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"

"""

# Import statements for utilized libraries / packages
import arcpy
import glob
import os
import scandir
import pandas as pd
from openpyxl import load_workbook

#Set various global variables. Some of these could be parameterized to be used as an 
#ArcGIS Toolbox script and/or command line use.

# Set the directory path to the root directory that will be documented
#_WORKSPACE = r'C:\_GIS' # Logical variable to parameterize for toolbox and/or command line
_WORKSPACE = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\GIS'
#_WORKSPACE = r'C:\Users\dgjones\DOI\NCRN Data Management - Documents\GIS'
_WORKSPACE_PREFIX = r'C:\Users\goettel\DOI'
#_WORKSPACE_PREFIX = r'C:\Users\dgjones\DOI'
xlsx_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial'
#xlsx_path = r'C:\Users\dgjones\DOI\NCRN Data Management - Geospatial'  

# Create a variable to store the file extension for file geodatabases
_FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
_SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
_EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx', 'png'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (outside FGDBs)
_RAST_EXT = ['.tif', '.tiff', '.jpg', '.jpeg', '.sid', '.bmp'] # Logical variable to parameterize for toolbox and/or command line

# Create some lists to be used in various places
dirs = []
fgdb_list = []
shp_list = []
rast_list = []
fgdbs_master_df = pd.DataFrame(
    columns = ['FGDB Path', 'FGDB Name', 'File Size', 'Feature Class Count', 'Feature Dataset Count', 'Table Count'])
main_master_df = pd.DataFrame(
    columns = ['Full Name', 'Location', 'Container', 'FeatureDataset', 'Extension/Format', 'Name', 'DataType', 'File Type / Compression', 'Geometry Type', 'SRS', 'Band Count', 'Size (MB)'])

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

def get_file_size(file, unit='bytes'):
    try:
        file_size = os.path.getsize(file)
        exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)
    except:
        size = None

#Create list of file geodatabases
for root, dirs, files in scandir.walk(_WORKSPACE):
    for dir in dirs:
        if str(dir).endswith(_FGDB_EXT):
            fgdb_list.append(os.path.join(root, dir))

def desc_fgdb(fgdb_list):
    for fgdb in fgdb_list:
        arcpy.env.workspace = fgdb
        fgdb_path = fgdb.removeprefix(_WORKSPACE_PREFIX)
        fgdb_name = os.path.basename(fgdb).split('/')[-1]
        file_size = get_size_format(get_folder_size(fgdb))
        fcs = arcpy.ListFeatureClasses()
        fc_count = len(fcs)
        fds = arcpy.ListDatasets("","")
        fd_count = len(fds)
        tables = arcpy.ListTables()
        table_count = len(tables)
        row_list = [fgdb_path, fgdb_name, file_size, fc_count, fd_count, table_count]
        fgdbs_master_df.loc[len(fgdbs_master_df)] = row_list
desc_fgdb(fgdb_list)

#Create list of shapefiles
shp_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _SHP_EXT)]

#Create list of rasters
glob_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _RAST_EXT)]
for file in glob_list:
    if os.path.splitext(file)[1] in _RAST_EXT:
        rast_list.append(file)

#Create list of all files
file_list = fgdb_list + shp_list + rast_list    

def desc_spatial_data_file(file_list):
    for file in file_list:
        if _FGDB_EXT in file:
            #print('Starting processing for:{0}'.format(file))
            arcpy.env.workspace = file
            fgdb = os.path.split(file)
            container = fgdb[1]
            datasets = arcpy.ListDatasets(feature_type='feature')
            #print('Finished getting dataset list...')
            datasets = [''] + datasets if datasets is not None else []
            for ds in datasets:
                #print('Looping over feature classes...')
                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                    #print('Processing a feature class...')
                    full_file = os.path.join(arcpy.env.workspace, ds, fc)
                    name = full_file.removeprefix(_WORKSPACE_PREFIX)
                    desc = arcpy.Describe(fc)
                    try:
                        spatial_ref = arcpy.Describe(fc).SpatialReference
                        srs_name = spatial_ref.Name
                    except:
                        srs_name = 'Unknown'
                        pass
                    if get_file_size(full_file, 'mb') == None:
                        size_mb = 'Unknown'
                    else:
                        size_mb = get_file_size(full_file, 'mb')
                    row_list = [name, os.path.dirname(file), container, ds, '', desc.baseName, desc.dataType, '', desc.shapeType, srs_name, '', size_mb]
                    main_master_df.loc[len(main_master_df)] = row_list
            rasters = arcpy.ListRasters("*", "GRID")
            if len(rasters) != 0:
                for r in rasters:
                    full_file = os.path.join(arcpy.env.workspace, r)
                    name = full_file.removeprefix(_WORKSPACE_PREFIX)
                    desc = arcpy.Describe(r)
                    try: 
                        spatial_ref = arcpy.Describe(r).SpatialReference
                        srs_name = spatial_ref.Name
                    except:
                        srs_name = 'Unknown'
                        pass
                    if get_file_size(full_file, 'mb') == None:
                        size_mb = 'Unknown'
                    else:
                        size_mb = get_file_size(full_file, 'mb')
                    row_list = [name, os.path.dirname(file), container, ds, 'Grid', desc.baseName, 'FGDB Raster', desc.compressionType,'Raster', srs_name, desc.bandCount, size_mb]
                    main_master_df.loc[len(main_master_df)] = row_list
        elif _SHP_EXT in file:
            name = file.removeprefix(_WORKSPACE_PREFIX)
            ext = _SHP_EXT.strip('.')
            desc = arcpy.Describe(file)                
            try:
                spatial_ref = arcpy.Describe(file).SpatialReference
                srs_name = spatial_ref.Name
            except:
                srs_name = 'Unknown'
                pass
            if get_file_size(file, 'mb') == None:
                size_mb = 'Unknown'
            else:
                size_mb = get_file_size(file, 'mb')
            row_list = [file, os.path.dirname(file), '', '', ext, desc.baseName, desc.dataType, '', desc.shapeType, srs_name, '', size_mb]
            main_master_df.loc[len(main_master_df)] = row_list
        elif os.path.splitext(file)[1] in _RAST_EXT:
            name = os.path.splitext(file)[1].removeprefix(_WORKSPACE_PREFIX)
            ext = os.path.splitext(file)[1].strip('.')
            desc = arcpy.Describe(file)
            try:
                spatial_ref = arcpy.Describe(file).SpatialReference
                srs_name = spatial_ref.Name
            except:
                srs_name = 'Unknown'
                pass
            if get_file_size(file, 'mb') == None:
                size_mb = 'Unknown'
            else:
                size_mb = get_file_size(file, 'mb')
            row_list = [file, os.path.dirname(file), '', '', ext, os.path.basename(file), 'Raster', desc.compressionType, 'Raster', srs_name, desc.bandCount, size_mb]
            main_master_df.loc[len(main_master_df)] = row_list
desc_spatial_data_file(file_list)
#print(main_master_df)

#Set path to xlsx workbook and worksheet
xlsx_name = os.path.join(xlsx_path, 'NCRN_GIS_Geospatial_Contents.xlsx')

#with pd.ExcelWriter(xlsx_name) as writer:  
#    fgdbs_master_df.to_excel(writer, sheet_name='FGDBs', index = False)
#    main_master_df.to_excel(writer, sheet_name='Main', index = False)

book = load_workbook(xlsx_name)
writer = pd.ExcelWriter(xlsx_name, engine='openpyxl') 
writer.book = book

writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
fgdbs_master_df.to_excel(writer, "FGDBs", index = False)
main_master_df.to_excel(writer, "Main", index = False)

writer.save()