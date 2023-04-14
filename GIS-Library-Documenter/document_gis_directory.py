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

_PREFIX = r'C:\Users\goettel' ## Set to the user portion of the root directory. Script will exclude from path that is documented

_WORKSPACE = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\GIS' ## Set the directory path to the root directory that will be documented. Set prefix to the user portion of the root directory

__XCEL_LIBRARY = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_GIS_Geospatial_Contents.xlsx' ## Create a variable to store the full path to the Excel file

# Create a variable to store the file extension for file geodatabases
_FGDB_EXT = '.gdb'

# Create a variable to store the file extension for shapefiles
_SHP_EXT = '.shp'

# Create a list variable to store file extensions to be ignored
_EXCLUDE_EXT = ['lock', 'gdbindexes', 'gdbtable', 'gdbtablx', 'horizon', 'spx', 'freelist', 'atx', 'png'] # Logical variable to parameterize for toolbox and/or command line (maybe)

# Create a list variable to store the file extensions for rasters (outside geodatabases)
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
        return 'Unknown'

def desc_fgdb(fgdb_list):
    """loop over a list of geodatabases to document parameters"""
    print("Looping over geodatabases...")
    for fgdb in fgdb_list:
        arcpy.env.workspace = fgdb
        fgdb_path = fgdb.removeprefix(_PREFIX) ## Full path of the geodatabase
        fgdb_name = os.path.basename(fgdb).split('/')[-1] ## Name of the geodatabase
        file_size = get_size_format(get_folder_size(fgdb)) ## File size of the geodatabase
        fcs = arcpy.ListFeatureClasses()
        fc_count = len(fcs) ## Number of feature classes in the geodatabase
        fds = arcpy.ListDatasets("","")
        fd_count = len(fds) ## Number of feature datasets in the geodatabase
        tables = arcpy.ListTables()
        table_count = len(tables) ## Number of tables in the geodatabase
        row_list = [fgdb_path, fgdb_name, file_size, fc_count, fd_count, table_count]
        fgdbs_master_df.loc[len(fgdbs_master_df)] = row_list

def desc_fgdb_file(fgdb_list):
    """loop over a list of geodatabases to document parameters of the feature classes and rasters it contains"""
    print("Looping over feature classes and rasters within geodatabases...")
    for fgdb in fgdb_list:
        arcpy.env.workspace = fgdb
        fgdb_name = os.path.split(fgdb) 
        container = fgdb_name[1] ## Geodatabase that contains the file
        ext = 'NA' ## Extension/format of the file
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        for ds in datasets:
            # Loop over feature classes
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                fullpath_filename = os.path.join(arcpy.env.workspace, ds, fc)
                full_name = fullpath_filename.removeprefix(_PREFIX) ## Folder path and name of the feature class
                folder_path = os.path.dirname(fgdb)
                location = folder_path.removeprefix(_PREFIX) ## Directory location of the fc
                if ds == '': ## Name of the feature dataset that contains the fc
                    featuredataset = 'NA'
                else:
                    featuredataset = ds
                desc = arcpy.Describe(fc)
                name = desc.baseName ## Name of the fc
                data_type = 'Vector' ## Data type of the fc
                file_type = desc.dataType ## File type/compression of the fc
                geometry_type = desc.shapeType ## Geometry type of the fc
                srs = get_srs_name(fc)
                band_count = 'NA'
                size_mb = get_file_size(fullpath_filename, 'mb')
                row_list = [full_name, location, container, featuredataset, ext, name, data_type, file_type, geometry_type, srs, band_count, size_mb]
                main_master_df.loc[len(main_master_df)] = row_list
            # Loop over raster datasets
            for r in arcpy.ListRasters('*', 'GRID'):
                fullpath_filename = os.path.join(arcpy.env.workspace, ds, r)
                full_name = fullpath_filename.removeprefix(_PREFIX)
                folder_path = os.path.dirname(fgdb)
                location = folder_path.removeprefix(_PREFIX)
                if ds == '':
                    featuredataset = 'NA'
                else:
                    featuredataset = ds
                desc = arcpy.Describe(r)
                name = desc.baseName
                data_type = 'FGDB Raster'
                file_type = desc.compressionType
                geometry_type = 'Raster'
                srs = get_srs_name(r)
                band_count = desc.bandCount ## Band count of the raster
                size_mb = get_file_size(fullpath_filename, 'mb')
                row_list = [full_name, location, container, featuredataset, ext, name, data_type, file_type, geometry_type, srs, band_count, size_mb]
                main_master_df.loc[len(main_master_df)] = row_list
        
def desc_shapefile(shp_list):                
    """loop over a list of shapefiles to document parameters"""
    print("Looping over shapefiles...")
    for shp in shp_list:
        full_name = shp.removeprefix(_PREFIX)
        folder_path = os.path.dirname(shp)
        location = folder_path.removeprefix(_PREFIX)
        container = 'NA'
        featuredataset = 'NA'
        ext = _SHP_EXT.strip('.')
        desc = arcpy.Describe(shp)
        name = desc.baseName
        data_type = 'Vector'
        file_type = desc.dataType
        geometry_type = desc.shapeType
        srs = get_srs_name(shp)
        band_count = 'NA'
        size_mb = get_file_size(shp, 'mb')
        row_list = [full_name, location, container, featuredataset, ext, name, data_type, file_type, geometry_type, srs, band_count, size_mb]
        main_master_df.loc[len(main_master_df)] = row_list
        
def desc_raster(rast_list):
    """loop over a list of rasters to document parameters"""
    print("Looping over rasters...")
    for rast in rast_list:
        full_name = rast.removeprefix(_PREFIX)
        folder_path = os.path.dirname(rast)
        location = folder_path.removeprefix(_PREFIX)
        container = 'NA'
        featuredataset = 'NA'
        ext = os.path.splitext(rast)[1].strip('.')
        desc = arcpy.Describe(rast)
        name = os.path.basename(rast)
        data_type = 'Raster'
        file_type = desc.compressionType
        geometry_type = 'Raster'
        srs = get_srs_name(rast)
        band_count = desc.bandCount
        size_mb = get_file_size(rast, 'mb')
        row_list = [full_name, location, container, featuredataset, ext, name, data_type, file_type, geometry_type, srs, band_count, size_mb]
        main_master_df.loc[len(main_master_df)] = row_list

# Populate list of geodatabases
fgdb_list = []
for root, dirs, files in scandir.walk(_WORKSPACE):
    for folder in dirs:
        if str(folder).endswith(_FGDB_EXT):
            fgdb_list.append(os.path.join(root, folder))

# Document list of geodatabases
desc_fgdb(fgdb_list)

# Populate list of shapefiles
shp_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _SHP_EXT)]

# Populate list of rasters
rast_list = []
glob_list = [os.path.join(os.path.dirname(f), os.path.basename(f)) for f in get_files_glob(_WORKSPACE, _RAST_EXT)]
for rast in glob_list:
    if os.path.splitext(rast)[1] in _RAST_EXT:
        rast_list.append(rast)

# Document lists of files
desc_fgdb_file(fgdb_list)
desc_shapefile(shp_list)
desc_raster(rast_list)

# Set path to xlsx workbook and worksheet
book = load_workbook(__XCEL_LIBRARY)
writer = pd.ExcelWriter(__XCEL_LIBRARY, engine='openpyxl') 
writer.book = book

# Write output to xlsx and save changes
print("Writing to excel...")
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
fgdbs_master_df.to_excel(writer, "FGDBs", index = False)
main_master_df.to_excel(writer, "Main", index = False)
writer.save()

print("### !!! ALL DONE !!! ###".format())