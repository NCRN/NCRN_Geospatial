#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document a GIS directory.
--------------------------------------------------------------------------------
TODO: Add more of a complete description.

References:
https://www.thepythoncode.com/article/get-directory-size-in-bytes-using-python

#__author__ = "David Jones"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.2"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"

"""

# Import statements for utilized libraries / packages
from ftplib import parse150
import arcpy
import glob
import os
import scandir
import pandas as pd
from openpyxl import load_workbook

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used as an 
ArcGIS Toolbox script and/or command line use.
"""
# Currently hardcoded values that may be parameterized if bundling into a tool

_PREFIX = r'C:\Users\goettel' ## Set to the user portion of the root directory. Use to exclude from path that is documented

_WORKSPACE = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\GIS' ## Set the directory path to the root directory that will be documented. Set prefix to the user portion of the root directory

xlsx_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_GIS_Geospatial_Contents.xlsx' ## Create a variable to store the full path to the GIS Library Documenter Excel file

# Create a variable to store the file extension for file geodatabases
_FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
_SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
_EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx', 'png'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (outside FGDBs)
_RAST_EXT = ['.tif', '.tiff', '.jpg', '.jpeg', '.sid', '.bmp'] # Logical variable to parameterize for toolbox and/or command line

# Create dataframes to record information that is documented
fgdbs_master_df = pd.DataFrame(
    columns = ['FGDB Path', 'FGDB Name', 'File Size', 'Feature Class Count', 'Feature Dataset Count', 'Table Count'])
main_master_df = pd.DataFrame(
    columns = ['Full Name', 'Location', 'Container', 'FeatureDataset', 'Extension/Format', 'Name', 'DataType', 'File Type / Compression', 'Geometry Type', 'SRS', 'Band Count', 'Size (MB)'])

# Create some functions to be used in various places
def get_files_glob(base_dir, ext):
    """Gets a glob of file paths
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
    """Returns the folder size in its proper byte format"""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total/1024/1024

def get_srs_name(file):
    """Returns the name of the spatial reference system (srs)"""
    try:
        spatial_ref = arcpy.Describe(file).SpatialReference
        srs_name = spatial_ref.Name
    except:
        srs_name = 'Unknown'
    return srs_name

def get_file_size(file, unit='bytes'):
    """
    Returns the file size in selected byte format
    get_file_size(file, 'bytes')
    Accepts kb, mb, or gb
    """
    try:
        file_size = os.path.getsize(file)
        exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)
    except:
        size = 'Unknown'

def desc_fgdb(fgdb_list):
    """loop over a list of FGDBs to document parameters"""
    print("Looping over FGDBs...")
    for fgdb in fgdb_list:
        arcpy.env.workspace = fgdb
        fgdb_path = fgdb.removeprefix(_PREFIX)
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

def desc_fgdb_file(fgdb_list):
    """loop over a list of geodatabases to document parameters of the feature classes and rasters it contains"""
    print("Looping over feature classes and rasters within FGDBs...")
    for file in fgdb_list:
        arcpy.env.workspace = file
        fgdb = os.path.split(file)
        container = fgdb[1]
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        for ds in datasets:
            # Loop over feature classes
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                full_file = os.path.join(arcpy.env.workspace, ds, fc)
                name = full_file.removeprefix(_PREFIX)
                full_location = os.path.dirname(file)
                location = full_location.removeprefix(_PREFIX)
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
                row_list = [name, location, container, ds, 'NA', desc.baseName, 'Vector', desc.dataType, desc.shapeType, srs_name, 'NA', size_mb]
                main_master_df.loc[len(main_master_df)] = row_list
            # Loop over raster datasets
            for r in arcpy.ListRasters("*", "GRID"):
                full_file = os.path.join(arcpy.env.workspace, ds, r)
                name = full_file.removeprefix(_PREFIX)
                full_location = os.path.dirname(file)
                location = full_location.removeprefix(_PREFIX)
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
                row_list = [name, location, container, ds, 'NA', desc.baseName, desc.dataType, desc.compressionType,'Raster', srs_name, desc.bandCount, size_mb]
                main_master_df.loc[len(main_master_df)] = row_list
        
def desc_shapefile(shp_list):                
    """loop over a list of shapefiles to document parameters"""
    print("Looping over shapefiles...")
    for file in shp_list:
        name = file.removeprefix(_PREFIX)
        full_location = os.path.dirname(file)
        location = full_location.removeprefix(_PREFIX)
        ext = _SHP_EXT.strip('.')
        desc = arcpy.Describe(file)                
        size_mb = get_file_size(file, 'mb')
        row_list = [name, location, '', '', ext, desc.baseName, 'Vector', desc.dataType, desc.shapeType, get_srs_name(file), 'NA', size_mb]
        main_master_df.loc[len(main_master_df)] = row_list
        
def desc_raster(rast_list):
    """loop over a list of rasters to document parameters"""
    print("Looping over rasters...")
    for file in rast_list:
        name = file.removeprefix(_PREFIX)
        full_location = os.path.dirname(file)
        location = full_location.removeprefix(_PREFIX)
        ext = os.path.splitext(file)[1].strip('.')
        desc = arcpy.Describe(file)
        size_mb = get_file_size(file, 'mb')
        row_list = [name, location, '', '', ext, os.path.basename(file), 'Raster', desc.compressionType, 'Raster', get_srs_name(file), desc.bandCount, size_mb]
        main_master_df.loc[len(main_master_df)] = row_list

# Populate list of FGDBs
fgdb_list = []
for root, dirs, files in scandir.walk(_WORKSPACE):
    for dir in dirs:
        if str(dir).endswith(_FGDB_EXT):
            fgdb_list.append(os.path.join(root, dir))

# Document list of FGDBs
desc_fgdb(fgdb_list)

# Populate list of shapefiles
shp_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _SHP_EXT)]

# Populate list of rasters
rast_list = []
glob_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _RAST_EXT)]
for file in glob_list:
    if os.path.splitext(file)[1] in _RAST_EXT:
        rast_list.append(file)

# Document lists of files
desc_fgdb_file(fgdb_list)
desc_shapefile(shp_list)
desc_raster(rast_list)

# Set path to xlsx workbook and worksheet
book = load_workbook(xlsx_path)
writer = pd.ExcelWriter(xlsx_path, engine='openpyxl') 
writer.book = book

# Write output to xlsx and save changes
print("Writing to excel...")
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
fgdbs_master_df.to_excel(writer, "FGDBs", index = False)
main_master_df.to_excel(writer, "Main", index = False)
writer.save()

print("### !!! ALL DONE !!! ###".format())