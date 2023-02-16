#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document a GIS directory.
--------------------------------------------------------------------------------


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

"""
Set various global variables. Some of these could be parameterized to be used as an 
ArcGIS Toolbox script and/or command line use.
"""
# Set the directory path to the root directory that will be documented
#_WORKSPACE = r'C:\_GIS' # Logical variable to parameterize for toolbox and/or command line
_WORKSPACE = r'C:\Users\dgjones\DOI\NCRN Data Management - Documents\GIS'

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

#fgdbs_giant_list = [r'U:\GIS\ANTI\ANTI_ParkAtlas.gdb', r'U:\GIS\ANTI\Soil\ANTI.gdb', r'U:\GIS\CATO\CATO_ParkAtlas_Final.gdb', r'U:\GIS\CHOH\CHOH_ParkAtlas.gdb', r'U:\GIS\GWMP\GWMP_Atlas.gdb', r'U:\GIS\MANA\Soil\MANA.gdb', 
#                    r'U:\GIS\MONO\Soil\MONO.gdb', r'U:\GIS\NACE\NACE_ParkAtlas.gdb', r'U:\GIS\NATIONAL\Hydro\WBD_National.gdb', r'U:\GIS\NATIONAL\Landcover\PADUS1_2_Geodatabase\PADUS1_2.gdb', r'U:\GIS\NCRN\Bird.gdb', 
#                    r'U:\GIS\NCRN\LANDS_Boundaries.gdb', r'U:\GIS\NCRN\NCRN_AOAs.gdb', r'U:\GIS\NCRN\NCRN_Basedata_ESRI.gdb', r'U:\GIS\NCRN\NCRN_Basedata_Other.gdb', r'U:\GIS\NCRN\NCRN_Boundaries.gdb', r'U:\GIS\NCRN\NCRN_Geology.gdb', 
#                    r'U:\GIS\NCRN\NCRN_Hydrology.gdb', r'U:\GIS\NCRN\NCRN_Monitoring.gdb', r'U:\GIS\NCRN\NCRN_Points_of_Interest.gdb', r'U:\GIS\NCRN\NCRN_Soil.gdb', r'U:\GIS\NCRN\NCR_Basedata.gdb', r'U:\GIS\NCRN\NCR_Basedata_WGS84.gdb', 
#                    r'U:\GIS\NCRN\HERP Monitoring\NCRN_Amphib_Habitat_Mapping.gdb', r'U:\GIS\NCRN\Landcover\Historic_Vegetation.gdb', r'U:\GIS\NCRN\Landcover\NCRN_Vegetation.gdb', r'U:\GIS\NCRN\Landcover\Forest_Lidar\Forest_Lidar_Derivatives_Old.gdb', 
#                    r'U:\GIS\NCRN\Landcover\Forest_Lidar\HAFE_Lidar_Derivatives.gdb', r'U:\GIS\NCRN\Retired\NCRN_Boundaries_Draft_20110913.gdb', r'U:\GIS\NCRN\Retired\NCRN_Boundaries_Draft_20110913_Final.gdb', r'U:\GIS\NCRN\Retired\NCRN_Boundaries_Draft_pre2014.gdb', 
#                    r'U:\GIS\NCRN\Retired\NCRN_Boundary_Issues.gdb', r'U:\GIS\NCRN\Retired\NCRN_Draft_Data.gdb', r'U:\GIS\NCRN\Retired\NCRN_Hydrology.gdb', r'U:\GIS\NCRN\Retired\NCRN_Hydrology_20140204.gdb', r'U:\GIS\NCRN\Retired\NCRN_Hydrology_20140305.gdb', 
#                    r'U:\GIS\NCRN\Retired\NCRN_Hydrology_20140804.gdb', r'U:\GIS\NCRN\Retired\NCRN_Hydrology_Legacy.gdb', r'U:\GIS\NCRN\Retired\NCRN_Monitoring_20120810.gdb', r'U:\GIS\NCRN\Retired\NCRN_Monitoring_20140204.gdb', 
#                    r'U:\GIS\NCRN\Retired\NCRN_Monitoring_20140804.gdb', r'U:\GIS\NCRN\Retired\NCRN_Monitoring_20170613.gdb', r'U:\GIS\NCRN\Retired\NCRN_Monitoring_20180502.gdb', r'U:\GIS\NCRN\Retired\NCRN_Retired_Layers.gdb', 
#                    r'U:\GIS\NCRN\Retired\NCRN_Vegetation_DRAFT_temp.gdb', r'U:\GIS\NCRN\Retired\NCR_Basedata_pre2014.gdb', r'U:\GIS\NCRN\Retired\NCR_Basedata_WGS_pre2014.gdb', r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\NCRN_Monitoring.gdb', 
#                    r'U:\GIS\NCRN\Soil\SSURGO\Soil_Derivatives.gdb', r'U:\GIS\NCRN\Transportation\NCR_Trails_v1.gdb', r'U:\GIS\NCRN\Water\NHD\NHDH0206.gdb', r'U:\GIS\NCRN\Water\NHD\NHDH0207.gdb', r'U:\GIS\NCRN\Water\NHD\NHDStreamGageEvents.gdb', 
#                    r'U:\GIS\NCRN\Water\NHD\NHDStreamGageEvents_1.gdb', r'U:\GIS\NCRN\Water\NHD\PointEventFC_dams.gdb', r'U:\GIS\NCRN\Water\NHD\Retired\NHDH0206.gdb', r'U:\GIS\NCRN\Water\NHD\Retired\NHDH0207.gdb', 
#                    r'U:\GIS\NCRN\Water\NHD\Retired\v2_0\NHDDamEvents.gdb', r'U:\GIS\NCRN\Water\NHD\Retired\v2_0\NHDH0206.gdb', r'U:\GIS\NCRN\Water\NHD\Retired\v2_0\NHDH0207.gdb', r'U:\GIS\NCRN\Water\NHD\Retired\v2_0\NHDStreamGageEvents.gdb', 
#                    r'U:\GIS\NCRN\Water\NHD\Retired\v2_0\NHDStreamGageEvents_1.gdb', r'U:\GIS\NCRN\_ARCHIVE\2017\NCRN_Monitoring.gdb', r'U:\GIS\Other\LEGACY\MANA\Soil\MANA.gdb', r'U:\GIS\Other\LEGACY\NCRN\NCRN_Boundaries_20110510.gdb', 
#                    r'U:\GIS\Other\LEGACY\PRWI\Revised\County\PWCData_FileDB.gdb', r'U:\GIS\Other\New_Downloads\CEC Ecoregions\CEC_Terrestrial_Ecosystems_L3.gdb', r'U:\GIS\Other\New_Downloads\GWMP\Boundary.gdb', 
#                    r'U:\GIS\Other\New_Downloads\GWMP\Lands.gdb', r'U:\GIS\Other\New_Downloads\Lands\MonumentationFileGeodatabase\MonumentationFileGeodatabase\NPS_Survey_Monumentation.gdb', r'U:\GIS\Other\New_Downloads\MD\kx-maryland-watersheds-FGDB\maryland-watersheds.gdb', 
#                    r'U:\GIS\Other\New_Downloads\NHD\NHDH0206.gdb', r'U:\GIS\Other\New_Downloads\NHD\NHDH0207.gdb', r'U:\GIS\Other\New_Downloads\NPScape\NPScape_AOA_CEC.gdb', r'U:\GIS\Other\New_Downloads\NPScape\NPScape_AOA_LCC.gdb', 
#                    r'U:\GIS\Other\New_Downloads\NPScape\NPScape_ScriptTools_PatternMetrics\Pattern_Tools\ToolData\MSPA_Reclassifications.gdb', r'U:\GIS\Other\New_Downloads\NPScape\NPScape_ScriptTools_PatternMetrics\Pattern_Tools\ToolData\Pattern_Reclassifications.gdb', 
#                    r'U:\GIS\Other\New_Downloads\NWI\2014-01-28\MD_wetlands.gdb', r'U:\GIS\Other\New_Downloads\NWI\2014-01-28\PA_wetlands.gdb', r'U:\GIS\Other\New_Downloads\NWI\2014-01-28\VA_wetlands.gdb', r'U:\GIS\Other\New_Downloads\NWI\2014-01-28\WV_wetlands.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\DCGIS_CENTRAL_062011.gdb', r'U:\GIS\Other\New_Downloads\Region\Test.gdb', r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_Basedata.gdb', r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_Buildings.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_GIS_Basedata.gdb', r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_GIS_Basedata_Bldgs_Rds_and Trails.gdb', r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_GIS_Basedata_Bldgs_Rds_and TrailsTEST.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_GIS_Basedata_Bldgs_Rds_and_Trails_9_2.gdb', r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_GIS_Basedata_Bldgs_Rds_and TrailsTEST.gdb\NCR_GIS_Basedata_Bldgs_Rds_and Trails.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20120611\NCR_GIS_Basedata_Bldgs_Rds_and_Trails_9_2.gdb\NCR_GIS_Basedata_Bldgs_Rds_and_Trails_9_2.gdb', r'U:\GIS\Other\New_Downloads\Region\20120611\vegetation\NCR_Vegetation_2011.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20120928\NCR_Buildings.gdb', r'U:\GIS\Other\New_Downloads\Region\20120928\NCR_Fire.gdb', r'U:\GIS\Other\New_Downloads\Region\20120928\NCR_GIS_Basedata.gdb', r'U:\GIS\Other\New_Downloads\Region\20130228\NCR_GIS_Basedata.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20130405\NCR_Fire.gdb', r'U:\GIS\Other\New_Downloads\Region\20130405\NCR_WUI_2010.gdb', r'U:\GIS\Other\New_Downloads\Region\20130520\NCR_GIS_Basedata.gdb', r'U:\GIS\Other\New_Downloads\Region\20131125\NCR_GIS_Basedata.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20140128\NCR_Buildings.gdb', r'U:\GIS\Other\New_Downloads\Region\20140128\NCR_Fire.gdb', r'U:\GIS\Other\New_Downloads\Region\20140128\NCR_Fuels.gdb', r'U:\GIS\Other\New_Downloads\Region\20140128\NCR_GIS_Basedata.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20140128\NCR_Vegetation_2011.gdb', r'U:\GIS\Other\New_Downloads\Region\20140128\NWI_Wetlands.gdb', r'U:\GIS\Other\New_Downloads\Region\20140428_Regional_Basedata\NCR_GIS_Basedata.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20140710\NCR_Basedata.gdb', r'U:\GIS\Other\New_Downloads\Region\20140710\NCR_Basedata_OLD.gdb', r'U:\GIS\Other\New_Downloads\Region\20140710\NCR_Buildings.gdb', 
#                    r'U:\GIS\Other\New_Downloads\Region\20140710\NCR_Vegetation_2011.gdb', r'U:\GIS\Other\New_Downloads\Region\20140710\NPS_Cell_Towers.gdb', r'U:\GIS\Other\New_Downloads\USFWS\fwsWetlandsExtract_20121001\fwsWetlandsExtract.gdb', 
#                    r'U:\GIS\Other\New_Downloads\USFWS\LCC\DOI_LCC_All\FWS_Climate_Change.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_2013_Revisions.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_Empty_9_3_Template.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_FDEN_2001.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_FDEN_2006.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_NLCD_LAC1.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_NLCD_LAC2.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_NLCD_LPI.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_PADUS.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_PFM1_2006_30m.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_PFM4_2006_150m.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_PFM_2006_90m_8_3_0_1.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_PFM_old.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_RDD.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_RDDWT.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_RDDWT_20130206.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_RDD_250m.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_RDD_v2.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\COHFECAT\COHFECAT_RDF.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Old\ProcessedData\Housing_Density_SERGoM.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Old\ProcessedData\gn5X\Housing_Density_SERGoM.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Old\ToolData\HousingDensity_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Old\ToolData\Test_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Older\ProcessedData\NAGWWOPR_Housing_Density_SERGoM_20140123.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Older\ProcessedData\20140325\Housing_Density_SERGoM.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Older\ProcessedData\NAGWWOPR_20140325\Housing_Density_SERGoM.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Older\ToolData\HousingDensity_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Housing_Tools_Older\ToolData\Test_AOA.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ProcessedData\Land_Cover_LAC.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ProcessedData\Land_Cover_LPI.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ProcessedData\Land_Cover_LPI5X.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ProcessedData\MONO_Land_Cover_LAC.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ToolData\CCAP_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ToolData\Landfire_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ToolData\NALC_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ToolData\NLCD_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\Landscape Tools\Landcover_Tools\ToolData\NPScape_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Hostetler_Birds_v2.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\NCRN_PRWI_Morphology_Test.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\PRWI_Morphology.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\PRWI_Morphology2.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\ConservationStatus_Tools\ProcessedData\mpaToolOut.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\ConservationStatus_Tools\ProcessedData\PADToolOut.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\ConservationStatus_Tools\ProcessedData\WDPAToolOut.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Housing_Tools\ToolData\HousingDensity_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Housing_Tools\ToolData\Test_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ProcessedData\LCCngToolOut.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ProcessedData\LCImperToolOut.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ProcessedData\lcToolout.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ToolData\CCAP_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ToolData\Landfire_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ToolData\NALC_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ToolData\NLCD_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Landcover_Tools\ToolData\NPScape_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools\ProcessedData\NLCDMorph.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools\ProcessedData\NLCD_Density.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools\ToolData\MSPA_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools\ToolData\Pattern_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools\ToolData\Test_AOA.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools_20130206\Pattern_Tools\ToolData\MSPA_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Pattern_Tools_20130206\Pattern_Tools\ToolData\Pattern_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Population_Tools\ToolData\Test_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Areas_Without_Roads.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_5x_Road_Density.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Park_Road_Density.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_2.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_v18.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_v20_5x.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_v3.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_v5.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_v6.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\CATO_Road_Density_v7.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\rdDens.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\RdDens4.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\RdDist3.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\RdDist4.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_CATO_30Only.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_v10.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_v11.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_v15.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_v6.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_v8.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Density_v9.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\Road_Distance.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\THRONoRds.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ProcessedData\THRONoRds4.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_20130204\Roads_Tools\ToolData\Test_AOA.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_1980_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_1980_20130603.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_1990_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_2010_20130602.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_2030_20130602.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_HD_SERGoM_Nxt_20130603.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_LAC2_20130601.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_LCI_2001_2006_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_LNC_20130602.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_LPI_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PDT1990_20130603c.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PDT2000_20130603.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PDT2010_20130601.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PFD27_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PFD27_20130604.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PFD7_20130601.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PFD81_20130603.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PFM1_20130601.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_PFM5_20130602.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRNa_RDDw_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRN_AOA_20130529b.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRN_PADUS_1_2.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\NPScape_201306b_Talk\Data\NCRN_PFM81_20130603.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Housing_Tools\ProcessedData\MONO5x_Housing_Density_SERGoM.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Housing_Tools\ProcessedData\NCRNa_HD_SERGoM_20130603.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Housing_Tools\ToolData\HousingDensity_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Landcover_Tools\ProcessedData\NCRNa_LAC1_20130603.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Landcover_Tools\ProcessedData\NCRNa_LPI_20130602.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Landcover_Tools\ToolData\CCAP_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Landcover_Tools\ToolData\Landfire_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Landcover_Tools\ToolData\NALC_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Landcover_Tools\ToolData\NLCD_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Pattern_Tools\ToolData\MSPA_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\ARCHIVE\v20130619\Pattern_Tools\ToolData\Pattern_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\Housing_Tools\ToolData\HousingDensity_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Housing_Tools\ToolData\Test_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\Land_Cover_LPI.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\Land_Cover_LPI5X.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ProcessedData\Land_Cover_LAC.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ProcessedData\Land_Cover_LAC_2001.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ProcessedData\Land_Cover_LPI.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ProcessedData\Park_Land_Cover_LAC.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ProcessedData\Park_Percent_Land_Cover_Level_1.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ToolData\CCAP_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ToolData\Landfire_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ToolData\NALC_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ToolData\NLCD_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\Landcover_Tools\ToolData\NPScape_AOA.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Pattern_Morphology\ProcessedData\NLCD_Morphology.gdb', r'U:\GIS\Projects\Air\NPScape\Pattern_Morphology\ToolData\MSPA_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Pattern_Morphology\ToolData\Pattern_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\Pattern_Tools\ToolData\MSPA_Reclassifications.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Pattern_Tools\ToolData\Pattern_Reclassifications.gdb', r'U:\GIS\Projects\Air\NPScape\Population_Tools\ToolData\Test_AOA.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\GWMP30k_PADUS_1_3.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\RESULTS\NACE30k_PADUS_1_3.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Land_Cover_LAC_01.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Land_Cover_LAC_06.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Land_Cover_LAC_11.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Land_Cover_LPI_01.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Land_Cover_LPI_06.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Land_Cover_LPI_11.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\NLCD_Morphology_FWW_8301_2011.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\PRWI30k_PADUS_1_3.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\RESULTS\WOTR30k_PADUS_1_3.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\CHOH_2014\CHOH_All_2001_Land_Cover_LAC.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\CHOH_2014\CHOH_All_2001_Land_Cover_LPI.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\RESULTS\CHOH_2014\CHOH_All_2006_Land_Cover_LAC.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\CHOH_2014\CHOH_All_2006_Land_Cover_LPI.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\CHOH_2014\CHOH_All_2011_Land_Cover_LAC.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\RESULTS\CHOH_2014\CHOH_All_2011_Land_Cover_LPI.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\NAGWWOPR_Housing\NAGWWOPR_Housing_Density_SERGoM.gdb', r'U:\GIS\Projects\Air\NPScape\RESULTS\Regional\NCRN_Road_Distance_20140205.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Roads_Tools\ProcessedData\Road_Density.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_CHOH_2014.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_COHFECAT.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_NAGWWOPR.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_NCRN_20130529.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_NCRN_20130529b.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_NCRN_Boundaries.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\AOA_NCRN_Test.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_NCRN\NCRN_Roads.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\PADUS1_3.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\Population_Census1990.gdb', r'U:\GIS\Projects\Air\NPScape\Source_NCRN\Population_Census2000.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_NCRN\Population_Census2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\COHFECAT_AOAs.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\ConservationStatus_ProtectedAreas_Governance_WDPA2011.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\ConservationStatus_ProtectedAreas_MPA2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Housing_Density_SERGoM.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NAGWWOPR_AOAs.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NAGWWOPR_AOAs_LT.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NCRN_20130529.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NCRN_AOA_20130529b.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NCRN_Boundaries_AOI.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NCRN_Roads.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\NCRN_Roads_Old.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\PADUS1_2.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_Census1990.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_Census2000.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_Census2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_DensityTotal_Census1990.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_DensityTotal_Census2000.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_DensityTotal_Census2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_HistoricDensityTotal_County.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Population_ProjectedDensityTotal_County.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Roads_AreasWithoutAll_ESRI2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Pre_2014\Roads_AreasWithoutMajor_ESRI2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\ConservationStatus_ProtectedAreas_Governance_WDPA2011.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\ConservationStatus_ProtectedAreas_MPA2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Housing_Density_SERGoM.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Landcover_CCAP_1996_2006.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Landcover_Change_CCAP.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Landcover_NALC2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Landcover_NaturalConverted_NLCD2006.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\PADUS1_3.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Pattern_ForestDensity_NALC2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Pattern_ForestMorphology_EdgeWidth1_NALC2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Pattern_ForestMorphology_EdgeWidth4_NALC2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Pattern_GrasslandDensity_NALC2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Pattern_GrasslandMorphology_EdgeWidth1_NALC2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Pattern_GrasslandMorphology_EdgeWidth4_NALC2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_Census1990.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_Census2000.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_Census2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_Census2010_CNMI.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_DensityTotal_Census1990.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_DensityTotal_Census2000.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_DensityTotal_Census2010.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_DensityTotal_CNMICensus2010.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_HistoricDensityTotal_County.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Population_ProjectedDensityTotal_County.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Roads_AreasWithoutAll_2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Roads_AreasWithoutAll_ESRI2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Roads_AreasWithoutMajor_ESRI2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Road_Density_AllRoads_ESRI2005.gdb', 
#                    r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Road_Density_MajorRoads_ESRI2005.gdb', r'U:\GIS\Projects\Air\NPScape\Source_Seamless\Road_Density_WeightedRoads_ESRI2005.gdb', 
#                    r'U:\GIS\Projects\CATO\CATO_Products.gdb', r'U:\GIS\Projects\CATO\Elevation\CATO_Elevation.gdb', r'U:\GIS\Projects\CHOH\MerryGoRound_Farms.gdb', r'U:\GIS\Projects\CHOH\scratch.gdb', 
#                    r'U:\GIS\Projects\CHOH\CHOH Watershed\CHOH_Watershed_Analysis.gdb', r'U:\GIS\Projects\CHOH\CHOH Watershed\CHOH_WS_Analysis.gdb', r'U:\GIS\Projects\CHOH\CHOH Watershed\NCRN_Hydrology.gdb', 
#                    r'U:\GIS\Projects\CHOH\CHOH_ParkVisit_2018\Buffer.gdb', r'U:\GIS\Projects\CUE\Emergency Plan\Parking_Lot.gdb', r'U:\GIS\Projects\EAB\NCRN_Fraxinus_Data.gdb', r'U:\GIS\Projects\Eastern Forest\Eastern_Forests.gdb', 
#                    r'U:\GIS\Projects\Eastern Forest\Eastern_Forests_Population.gdb', r'U:\GIS\Projects\Eastern Forest\Archive\Eastern_Forests_0_1.gdb', r'U:\GIS\Projects\Eva\Forest Cover\Historic Forest Cover.gdb', 
#                    r'U:\GIS\Projects\Eva\Plot Properties\NCRN_Plot_Properties.gdb', r'U:\GIS\Projects\Eva\Wetlands\Wetlands.gdb', r'U:\GIS\Projects\Forest_Vegetation\Camp\Camp_Monitoring.gdb', 
#                    r'U:\GIS\Projects\Geodetic\NCRN_Points_of_Interest.gdb', r'U:\GIS\Projects\GWMP\Dyke Marsh\Retired Data\2011 RTK Survey November\Export_To_GIS\RTK_DykeMarsh_20111117_AdjustedToRapid\RTK_Survey.gdb', 
#                    r'U:\GIS\Projects\HAFE\Deer Sampling\HAFE_Deer.gdb', r'U:\GIS\Projects\HAFE\Deer Sampling\New File Geodatabase.gdb', r'U:\GIS\Projects\HAFE\NPScape\HAFETest.gdb', r'U:\GIS\Projects\Hostetler\ANTIPat.gdb', 
#                    r'U:\GIS\Projects\Hostetler\BirdBuffers.gdb', r'U:\GIS\Projects\Hostetler\CATOPat.gdb', r'U:\GIS\Projects\Hostetler\CHOHCPatO.gdb', r'U:\GIS\Projects\Hostetler\CHOHEPatO.gdb', r'U:\GIS\Projects\Hostetler\CHOHWPatO.gdb', 
#                    r'U:\GIS\Projects\Hostetler\HAFEPat.gdb', r'U:\GIS\Projects\Hostetler\Hostetler_Landcover.gdb', r'U:\GIS\Projects\Hostetler\MANAPat.gdb', r'U:\GIS\Projects\Hostetler\MONOPat.gdb', r'U:\GIS\Projects\Hostetler\NACEPat.gdb', 
#                    r'U:\GIS\Projects\Hostetler\PRWIEPatO.gdb', r'U:\GIS\Projects\Hostetler\PRWIWPatO.gdb', r'U:\GIS\Projects\Hostetler\ROCRPat.gdb', r'U:\GIS\Projects\Hostetler\ROCTPatO.gdb', r'U:\GIS\Projects\Hostetler\WOTRPat.gdb', 
#                    r'U:\GIS\Projects\Hostetler\Delivered Products\Birds_30m_NLCD_Morphology.gdb', r'U:\GIS\Projects\Hostetler\Delivered Products\Hostetler_Birds_Landcover_Morphology.gdb', r'U:\GIS\Projects\LandscapeDynamics BND 2017\NCRN_LandscapeDynamics_CustomAOAs.gdb', 
#                    r'U:\GIS\Projects\Lidar\PRWI Lidar\Single Area Detail\PRWI_107.gdb', r'U:\GIS\Projects\MONO\Mono-Grasslands\2015_Intern_Study\MONO_Grasslands_Intern.gdb', r'U:\GIS\Projects\NACE\Seeps Transects 20111026\NACE_Seeps_Transects_2011.gdb', 
#                    r'U:\GIS\Projects\National Landscape Program\NCRN_Bounds.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_1980_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_1980_20130603.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_1990_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_2010_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_20130602.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_2030_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_HD_SERGoM_Nxt_20130603.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_LAC2_20130601.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_LCI_2001_2006_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_LNC_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_LPI_20130602.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PDT1990_20130603c.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PDT2000_20130603.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PDT2010_20130601.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PFD27_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PFD27_20130604.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PFD7_20130601.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PFD81_20130603.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PFM1_20130601.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_PFM5_20130602.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRNa_RDDw_20130602.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRN_AOA_20130529b.gdb', r'U:\GIS\Projects\NPScape_201306\Data\NCRN_PADUS_1_2.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\Data\NCRN_PFM81_20130603.gdb', r'U:\GIS\Projects\NPScape_201306\LCC Data\LCC_Road_Stats.gdb', r'U:\GIS\Projects\NPScape_201306\LCC Data\Appalachian_Pattern_Data\NALC_Forest_Density.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\LCC Data\Appalachian_Pattern_Data\NALC_Forest_Morphology.gdb', r'U:\GIS\Projects\NPScape_201306\LCC Data\Appalachian_Pattern_Data\NALC_Grassland_Density.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\LCC Data\Appalachian_Pattern_Data\NALC_Grassland_Morphology.gdb', r'U:\GIS\Projects\NPScape_201306\LCC Data\North_Atlantic_Landcover_Data\NALC_LAC.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\LCC Data\North_Atlantic_Landcover_Data\NALC_LNC.gdb', r'U:\GIS\Projects\NPScape_201306\LCC Data\North_Atlantic_Pattern_Data\NALC_Forest_Density.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\LCC Data\North_Atlantic_Pattern_Data\NALC_Forest_Morphology.gdb', r'U:\GIS\Projects\NPScape_201306\LCC Data\North_Atlantic_Pattern_Data\NALC_Grassland_Density.gdb', 
#                    r'U:\GIS\Projects\NPScape_201306\LCC Data\North_Atlantic_Pattern_Data\NALC_Grassland_Morphology.gdb', r'U:\GIS\Projects\ROCR\Elevation\ROCR_Watersheds.gdb', r'U:\GIS\Projects\ROCR\Sewer\Sewer_System.gdb', 
#                    r'U:\GIS\Projects\Watersheds\Training\Data\PRWI_Watersheds.gdb', r'U:\GIS\Projects\Watersheds\Training\Data\Training_Data.gdb', r'U:\GIS\Projects\Watersheds\Watershed In and Out of Parks\Park Watershed Area.gdb', 
#                    r'U:\GIS\Projects\Watersheds\Website - Big\Standard Annotation.gdb', r'U:\GIS\Projects\WOTR\DataTransfer\WOTR_NRCA_Basedata.gdb', r'U:\GIS\PRWI\PRWI_NRCA_Basedata.gdb', r'U:\GIS\PRWI\PRWI_Park_Atlas_20130110_1324.gdb', 
#                    r'U:\GIS\PRWI\For_DivisionChief_Ekk\PRWI_Birds.gdb', r'U:\GIS\PRWI\Soil\PRWI.gdb', r'U:\GIS\REGIONAL\Water\NHD_Plus\NHDPlus02\NHDPlusFGDB.gdb', r'U:\GIS\WOTR\WOTR_NRCA_Basedata.gdb', r'U:\GIS\WOTR\WOTR_ParkAtlas.gdb', 
#                    r'U:\GIS\WOTR\Soil\WOTR.gdb', r'U:\GIS\~Documentation\Core_Spatial_Data_Standard_Plan_DRAFT\DRAFT_NPS_CORE.gdb', r'U:\GIS\~~GIS_Database_Lite~~\Projects\Region\NCRN_Amph_LandUse_Buffer\NCRN Land Use and Percent Forest Cover\Park_Land_Cover.gdb', 
#                    r'U:\GIS\~~GIS_Database_Lite~~\Water\Regional\NCRN_NHD.gdb', r'U:\GIS\~~GIS_Database_Lite~~\Water\Regional\NCRN_NHD\v105\ncrn_nhd.gdb']

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

#exclude_fgdbs = set(['Park_Land_Cover.gdb', 
#'NCRN_NHD.gdb', 
#'DRAFT_NPS_CORE.gdb', 
#'ANTI_ParkAtlas.gdb', 
#'ANTI.gdb', 
#'CATO_ParkAtlas_Final.gdb', 
#'CHOH_ParkAtlas.gdb', 
#'GWMP_Atlas.gdb', 
#'MANA.gdb', 
#'MONO.gdb', 
#'NACE_ParkAtlas.gdb', 
#'WBD_National.gdb', 
#'PADUS1_2.gdb', 
#'NCRN_Monitoring.gdb', 
#'Bird.gdb', 
#'NCRN_Amphib_Habitat_Mapping.gdb', 
#'Forest_Lidar_Derivatives_Old.gdb', 
#'HAFE_Lidar_Derivatives.gdb', 
#'Historic_Vegetation.gdb', 
#'NCRN_Vegetation.gdb', 
#'LANDS_Boundaries.gdb', 
#'NCR_Basedata.gdb', 
#'NCR_Basedata_WGS84.gdb', 
#'NCRN_AOAs.gdb', 
#'NCRN_Basedata_ESRI.gdb', 
#'NCRN_Basedata_Other.gdb', 
#'NCRN_Boundaries.gdb', 
#'NCRN_Geology.gdb', 
#'NCRN_Hydrology.gdb', 
#'NCRN_Points_of_Interest.gdb', 
#'NCRN_Soil.gdb', 
#'NCR_Basedata_pre2014.gdb', 
#'NCR_Basedata_WGS_pre2014.gdb', 
#'NCRN_Boundaries_Draft_20110913.gdb', 
#'NCRN_Boundaries_Draft_20110913_Final.gdb', 
#'NCRN_Boundaries_Draft_pre2014.gdb', 
#'NCRN_Boundary_Issues.gdb', 
#'NCRN_Draft_Data.gdb', 
#'NCRN_Hydrology_20140204.gdb', 
#'NCRN_Hydrology_20140305.gdb', 
#'NCRN_Hydrology_20140804.gdb', 
#'NCRN_Hydrology_Legacy.gdb', 
#'NCRN_Monitoring_20120810.gdb', 
#'NCRN_Monitoring_20140204.gdb', 
#'NCRN_Monitoring_20140804.gdb', 
#'NCRN_Monitoring_20170613.gdb', 
#'NCRN_Monitoring_20180502.gdb', 
#'NCRN_Retired_Layers.gdb', 
#'NCRN_Vegetation_DRAFT_temp.gdb', 
#'Soil_Derivatives.gdb', 
#'NCR_Trails_v1.gdb', 
#'NHDH0206.gdb', 
#'NHDH0207.gdb', 
#'NHDStreamGageEvents.gdb', 
#'NHDStreamGageEvents_1.gdb', 
#'PointEventFC_dams.gdb', 
#'NHDDamEvents.gdb', 
#'NCRN_Boundaries_20110510.gdb', 
#'PWCData_FileDB.gdb', 
#'CEC_Terrestrial_Ecosystems_L3.gdb', 
#'Boundary.gdb', 
#'Lands.gdb', 
#'NPS_Survey_Monumentation.gdb', 
#'maryland-watersheds.gdb', 
#'NPScape_AOA_CEC.gdb', 
#'NPScape_AOA_LCC.gdb', 
#'MSPA_Reclassifications.gdb', 
#'Pattern_Reclassifications.gdb', 
#'MD_wetlands.gdb', 
#'PA_wetlands.gdb', 
#'VA_wetlands.gdb', 
#'WV_wetlands.gdb', 
#'NCR_Buildings.gdb', 
#'NCR_GIS_Basedata.gdb', 
#'NCR_GIS_Basedata_Bldgs_Rds_and Trails.gdb', 
#'NCR_GIS_Basedata_Bldgs_Rds_and TrailsTEST.gdb', 
#'NCR_GIS_Basedata_Bldgs_Rds_and_Trails_9_2.gdb', 
#'NCR_Vegetation_2011.gdb', 
#'NCR_Fire.gdb', 
#'NCR_WUI_2010.gdb', 
#'NCR_Fuels.gdb', 
#'NWI_Wetlands.gdb', 
#'NCR_Basedata_OLD.gdb', 
#'NPS_Cell_Towers.gdb', 
#'DCGIS_CENTRAL_062011.gdb', 
#'Test.gdb', 
#'fwsWetlandsExtract.gdb', 
#'FWS_Climate_Change.gdb', 
#'COHFECAT_2013_Revisions.gdb', 
#'COHFECAT_Empty_9_3_Template.gdb', 
#'COHFECAT_FDEN_2001.gdb', 
#'COHFECAT_FDEN_2006.gdb', 
#'COHFECAT_NLCD_LAC1.gdb', 
#'COHFECAT_NLCD_LAC2.gdb', 
#'COHFECAT_NLCD_LPI.gdb', 
#'COHFECAT_PADUS.gdb', 
#'COHFECAT_PFM_2006_90m_8_3_0_1.gdb', 
#'COHFECAT_PFM_old.gdb', 
#'COHFECAT_PFM1_2006_30m.gdb', 
#'COHFECAT_PFM4_2006_150m.gdb', 
#'COHFECAT_RDD.gdb', 
#'COHFECAT_RDD_250m.gdb', 
#'COHFECAT_RDD_v2.gdb', 
#'COHFECAT_RDDWT.gdb', 
#'COHFECAT_RDDWT_20130206.gdb', 
#'COHFECAT_RDF.gdb', 
#'Housing_Density_SERGoM.gdb', 
#'HousingDensity_Reclassifications.gdb', 
#'Test_AOA.gdb', 
#'NAGWWOPR_Housing_Density_SERGoM_20140123.gdb', 
#'Land_Cover_LAC.gdb', 
#'Land_Cover_LPI.gdb', 
#'Land_Cover_LPI5X.gdb', 
#'MONO_Land_Cover_LAC.gdb', 
#'CCAP_Reclassifications.gdb', 
#'Landfire_Reclassifications.gdb', 
#'NALC_Reclassifications.gdb', 
#'NLCD_Reclassifications.gdb', 
#'NPScape_AOA.gdb', 
#'mpaToolOut.gdb', 
#'PADToolOut.gdb', 
#'WDPAToolOut.gdb', 
#'Hostetler_Birds_v2.gdb', 
#'LCCngToolOut.gdb', 
#'LCImperToolOut.gdb', 
#'lcToolout.gdb', 
#'NCRN_PRWI_Morphology_Test.gdb', 
#'NLCD_Density.gdb', 
#'NLCDMorph.gdb', 
#'PRWI_Morphology.gdb', 
#'PRWI_Morphology2.gdb', 
#'Areas_Without_Roads.gdb', 
#'CATO_5x_Road_Density.gdb', 
#'CATO_Park_Road_Density.gdb', 
#'CATO_Road_Density.gdb', 
#'CATO_Road_Density_2.gdb', 
#'CATO_Road_Density_v18.gdb', 
#'CATO_Road_Density_v20_5x.gdb', 
#'CATO_Road_Density_v3.gdb', 
#'CATO_Road_Density_v5.gdb', 
#'CATO_Road_Density_v6.gdb', 
#'CATO_Road_Density_v7.gdb', 
#'rdDens.gdb', 
#'RdDens4.gdb', 
#'RdDist3.gdb', 
#'RdDist4.gdb', 
#'Road_Density.gdb', 
#'Road_Density_CATO_30Only.gdb', 
#'Road_Density_v10.gdb', 
#'Road_Density_v11.gdb', 
#'Road_Density_v15.gdb', 
#'Road_Density_v6.gdb', 
#'Road_Density_v8.gdb', 
#'Road_Density_v9.gdb', 
#'Road_Distance.gdb', 
#'THRONoRds.gdb', 
#'THRONoRds4.gdb', 
#'NCRN_AOA_20130529b.gdb', 
#'NCRN_PADUS_1_2.gdb', 
#'NCRN_PFM81_20130603.gdb', 
#'NCRNa_HD_SERGoM_1980_20130602.gdb', 
#'NCRNa_HD_SERGoM_1980_20130603.gdb', 
#'NCRNa_HD_SERGoM_1990_20130602.gdb', 
#'NCRNa_HD_SERGoM_2010_20130602.gdb', 
#'NCRNa_HD_SERGoM_20130602.gdb', 
#'NCRNa_HD_SERGoM_2030_20130602.gdb', 
#'NCRNa_HD_SERGoM_Nxt_20130603.gdb', 
#'NCRNa_LAC2_20130601.gdb', 
#'NCRNa_LCI_2001_2006_20130602.gdb', 
#'NCRNa_LNC_20130602.gdb', 
#'NCRNa_LPI_20130602.gdb', 
#'NCRNa_PDT1990_20130603c.gdb', 
#'NCRNa_PDT2000_20130603.gdb', 
#'NCRNa_PDT2010_20130601.gdb', 
#'NCRNa_PFD27_20130602.gdb', 
#'NCRNa_PFD27_20130604.gdb', 
#'NCRNa_PFD7_20130601.gdb', 
#'NCRNa_PFD81_20130603.gdb', 
#'NCRNa_PFM1_20130601.gdb', 
#'NCRNa_PFM5_20130602.gdb', 
#'NCRNa_RDDw_20130602.gdb', 
#'MONO5x_Housing_Density_SERGoM.gdb', 
#'NCRNa_HD_SERGoM_20130603.gdb', 
#'NCRNa_LAC1_20130603.gdb', 
#'Land_Cover_LAC_2001.gdb', 
#'Park_Land_Cover_LAC.gdb', 
#'Park_Percent_Land_Cover_Level_1.gdb', 
#'NLCD_Morphology.gdb', 
#'CHOH_All_2001_Land_Cover_LAC.gdb', 
#'CHOH_All_2001_Land_Cover_LPI.gdb', 
#'CHOH_All_2006_Land_Cover_LAC.gdb', 
#'CHOH_All_2006_Land_Cover_LPI.gdb', 
#'CHOH_All_2011_Land_Cover_LAC.gdb', 
#'CHOH_All_2011_Land_Cover_LPI.gdb', 
#'GWMP30k_PADUS_1_3.gdb', 
#'NACE30k_PADUS_1_3.gdb', 
#'NAGWWOPR_Housing_Density_SERGoM.gdb', 
#'NAGWWOPR_Land_Cover_LAC_01.gdb', 
#'NAGWWOPR_Land_Cover_LAC_06.gdb', 
#'NAGWWOPR_Land_Cover_LAC_11.gdb', 
#'NAGWWOPR_Land_Cover_LPI_01.gdb', 
#'NAGWWOPR_Land_Cover_LPI_06.gdb', 
#'NAGWWOPR_Land_Cover_LPI_11.gdb', 
#'NLCD_Morphology_FWW_8301_2011.gdb', 
#'PRWI30k_PADUS_1_3.gdb', 
#'NCRN_Road_Distance_20140205.gdb', 
#'WOTR30k_PADUS_1_3.gdb', 
#'AOA_CHOH_2014.gdb', 
#'AOA_COHFECAT.gdb', 
#'AOA_NAGWWOPR.gdb', 
#'AOA_NCRN_20130529.gdb', 
#'AOA_NCRN_20130529b.gdb', 
#'AOA_NCRN_Boundaries.gdb', 
#'AOA_NCRN_Test.gdb', 
#'NCRN_Roads.gdb', 
#'PADUS1_3.gdb', 
#'Population_Census1990.gdb', 
#'Population_Census2000.gdb', 
#'Population_Census2010.gdb', 
#'COHFECAT_AOAs.gdb', 
#'ConservationStatus_ProtectedAreas_Governance_WDPA2011.gdb', 
#'ConservationStatus_ProtectedAreas_MPA2010.gdb', 
#'NAGWWOPR_AOAs.gdb', 
#'NAGWWOPR_AOAs_LT.gdb', 
#'NCRN_20130529.gdb', 
#'NCRN_Boundaries_AOI.gdb', 
#'NCRN_Roads_Old.gdb', 
#'Population_DensityTotal_Census1990.gdb', 
#'Population_DensityTotal_Census2000.gdb', 
#'Population_DensityTotal_Census2010.gdb', 
#'Population_HistoricDensityTotal_County.gdb', 
#'Population_ProjectedDensityTotal_County.gdb', 
#'Roads_AreasWithoutAll_ESRI2005.gdb', 
#'Roads_AreasWithoutMajor_ESRI2005.gdb', 
#'Landcover_CCAP_1996_2006.gdb', 
#'Landcover_Change_CCAP.gdb', 
#'Landcover_NALC2005.gdb', 
#'Landcover_NaturalConverted_NLCD2006.gdb', 
#'Pattern_ForestDensity_NALC2005.gdb', 
#'Pattern_ForestMorphology_EdgeWidth1_NALC2005.gdb', 
#'Pattern_ForestMorphology_EdgeWidth4_NALC2005.gdb', 
#'Pattern_GrasslandDensity_NALC2005.gdb', 
#'Pattern_GrasslandMorphology_EdgeWidth1_NALC2005.gdb', 
#'Pattern_GrasslandMorphology_EdgeWidth4_NALC2005.gdb', 
#'Population_Census2010_CNMI.gdb', 
#'Population_DensityTotal_CNMICensus2010.gdb', 
#'Road_Density_AllRoads_ESRI2005.gdb', 
#'Road_Density_MajorRoads_ESRI2005.gdb', 
#'Road_Density_WeightedRoads_ESRI2005.gdb', 
#'Roads_AreasWithoutAll_2005.gdb', 
#'CATO_Products.gdb', 
#'CATO_Elevation.gdb', 
#'CHOH_Watershed_Analysis.gdb', 
#'CHOH_WS_Analysis.gdb', 
#'Buffer.gdb', 
#'MerryGoRound_Farms.gdb', 
#'scratch.gdb', 
#'Parking_Lot.gdb', 
#'NCRN_Fraxinus_Data.gdb', 
#'Eastern_Forests_0_1.gdb', 
#'Eastern_Forests.gdb', 
#'Eastern_Forests_Population.gdb', 
#'Historic Forest Cover.gdb', 
#'NCRN_Plot_Properties.gdb', 
#'Wetlands.gdb', 
#'Camp_Monitoring.gdb', 
#'RTK_Survey.gdb', 
#'HAFE_Deer.gdb', 
#'New File Geodatabase.gdb', 
#'HAFETest.gdb', 
#'ANTIPat.gdb', 
#'BirdBuffers.gdb', 
#'CATOPat.gdb', 
#'CHOHCPatO.gdb', 
#'CHOHEPatO.gdb', 
#'CHOHWPatO.gdb', 
#'Birds_30m_NLCD_Morphology.gdb', 
#'Hostetler_Birds_Landcover_Morphology.gdb', 
#'HAFEPat.gdb', 
#'Hostetler_Landcover.gdb', 
#'MANAPat.gdb', 
#'MONOPat.gdb', 
#'NACEPat.gdb', 
#'PRWIEPatO.gdb', 
#'PRWIWPatO.gdb', 
#'ROCRPat.gdb', 
#'ROCTPatO.gdb', 
#'WOTRPat.gdb', 
#'NCRN_LandscapeDynamics_CustomAOAs.gdb', 
#'PRWI_107.gdb', 
#'MONO_Grasslands_Intern.gdb', 
#'NACE_Seeps_Transects_2011.gdb', 
#'NCRN_Bounds.gdb', 
#'NALC_Forest_Density.gdb', 
#'NALC_Forest_Morphology.gdb', 
#'NALC_Grassland_Density.gdb', 
#'NALC_Grassland_Morphology.gdb', 
#'LCC_Road_Stats.gdb', 
#'NALC_LAC.gdb', 
#'NALC_LNC.gdb', 
#'ROCR_Watersheds.gdb', 
#'Sewer_System.gdb', 
#'PRWI_Watersheds.gdb', 
#'Training_Data.gdb', 
#'Park Watershed Area.gdb', 
#'Standard Annotation.gdb', 
#'WOTR_NRCA_Basedata.gdb', 
#'PRWI_Birds.gdb', 
#'PRWI_NRCA_Basedata.gdb', 
#'PRWI_Park_Atlas_20130110_1324.gdb', 
#'PRWI.gdb', 
#'NHDPlusFGDB.gdb', 
#'WOTR.gdb', 
#'WOTR_ParkAtlas.gdb'])

#exclude_folders = [r'U:\GIS\~~GIS_Database_Lite~~',
#r'U:\GIS\~Documentation',
#r'U:\GIS\~To Be Deleted',
#r'U:\GIS\ANTI',
#r'U:\GIS\ANTI\Boundary',
#r'U:\GIS\ANTI\Boundary\Retired',
#r'U:\GIS\ANTI\Geology',
#r'U:\GIS\ANTI\Soil',
#r'U:\GIS\ANTI\Structures',
#r'U:\GIS\ANTI\Water',
#r'U:\GIS\CATO',
#r'U:\GIS\CATO\Boundary',
#r'U:\GIS\CATO\Boundary\Archive',
#r'U:\GIS\CATO\Elevation',
#r'U:\GIS\CATO\Elevation\Hypsography',
#r'U:\GIS\CATO\Flora',
#r'U:\GIS\CATO\Flora\Exotic',
#r'U:\GIS\CATO\Geology',
#r'U:\GIS\CATO\Soil',
#r'U:\GIS\CATO\Structures',
#r'U:\GIS\CATO\Transportation',
#r'U:\GIS\CATO\Utilities',
#r'U:\GIS\CATO\Water',
#r'U:\GIS\CHOH',
#r'U:\GIS\CHOH\Boundary',
#r'U:\GIS\CHOH\Elevation',
#r'U:\GIS\CHOH\Elevation\Hypsography',
#r'U:\GIS\CHOH\Geology',
#r'U:\GIS\CHOH\Imagery',
#r'U:\GIS\CHOH\Imagery\ortho_imagery',
#r'U:\GIS\CHOH\Structures',
#r'U:\GIS\CHOH\Transportation',
#r'U:\GIS\DC',
#r'U:\GIS\DC\Air',
#r'U:\GIS\DC\Boundary',
#r'U:\GIS\DC\Boundary\Geodetic',
#r'U:\GIS\DC\Civic',
#r'U:\GIS\DC\Cultural',
#r'U:\GIS\DC\Cultural\Historic',
#r'U:\GIS\DC\Cultural\Historic\Boschke_1861',
#r'U:\GIS\DC\Cultural\Historic\historic_usgs',
#r'U:\GIS\DC\Cultural\Historic\Hodasevich_1863a',
#r'U:\GIS\DC\Cultural\Historic\Hodasevich_1863b',
#r'U:\GIS\DC\Cultural\Historic\Klingle_1892',
#r'U:\GIS\DC\Cultural\Historic\NGS_1892',
#r'U:\GIS\DC\Elevation',
#r'U:\GIS\DC\Elevation\DEM',
#r'U:\GIS\DC\Elevation\DEM\Aspect',
#r'U:\GIS\DC\Elevation\DEM\Hillshade',
#r'U:\GIS\DC\Elevation\DEM\Slope',
#r'U:\GIS\DC\Elevation\Hypsography',
#r'U:\GIS\DC\Flora',
#r'U:\GIS\DC\Hazmat',
#r'U:\GIS\DC\Landcover',
#r'U:\GIS\DC\Soil',
#r'U:\GIS\DC\Structures',
#r'U:\GIS\DC\Transportation',
#r'U:\GIS\DC\Utilities',
#r'U:\GIS\DC\Water',
#r'U:\GIS\DC\Water\Floodplain',
#r'U:\GIS\DC\Water\Watershed',
#r'U:\GIS\DC\Wetlands',
#r'U:\GIS\GPS',
#r'U:\GIS\GPS\Garmin',
#r'U:\GIS\GPS\Garmin\Waypoints',
#r'U:\GIS\GPS\Topcon',
#r'U:\GIS\GPS\Trimble',
#r'U:\GIS\GPS\Trimble\GPS-to-GIS Proccess Series',
#r'U:\GIS\GWMP',
#r'U:\GIS\GWMP\Boundary',
#r'U:\GIS\GWMP\Boundary\Archive',
#r'U:\GIS\GWMP\Geology',
#r'U:\GIS\GWMP\Structures',
#r'U:\GIS\GWMP\Transportation',
#r'U:\GIS\HAFE',
#r'U:\GIS\HAFE\Boundary',
#r'U:\GIS\HAFE\Boundary\Archive',
#r'U:\GIS\HAFE\Elevation',
#r'U:\GIS\HAFE\Elevation\Hypsography',
#r'U:\GIS\HAFE\Elevation\Lidar_Draft',
#r'U:\GIS\HAFE\Elevation\Lidar_Draft\HAFE_LiDAR_DEM_corrected',
#r'U:\GIS\HAFE\Elevation\Lidar_Draft\LIDAR_DEM_HAFE',
#r'U:\GIS\HAFE\Geology',
#r'U:\GIS\HAFE\LandCover',
#r'U:\GIS\HAFE\Soil',
#r'U:\GIS\HAFE\Structures',
#r'U:\GIS\HAFE\Transportation',
#r'U:\GIS\Imagery',
#r'U:\GIS\Imagery\Aerial',
#r'U:\GIS\Imagery\Aerial\dcmetroarea_03101949_opt',
#r'U:\GIS\Imagery\Bathymetry',
#r'U:\GIS\Imagery\Bathymetry\1973_DykeMarshBathymetry',
#r'U:\GIS\Imagery\Bathymetry\1974_DykeMarshBathymetry',
#r'U:\GIS\Imagery\Bathymetry\1992_DykeMarshBathymetry',
#r'U:\GIS\Imagery\Bathymetry\1992_DykeMarshBathymetry\WorkspaceFiles',
#r'U:\GIS\Imagery\Bathymetry\1994_BelleHavenMarina_Bathymetry',
#r'U:\GIS\Imagery\Bathymetry\1994_BelleHavenMarina_Bathymetry\bh_cad9',
#r'U:\GIS\Imagery\Bathymetry\1994_BelleHavenMarina_Bathymetry\info',
#r'U:\GIS\Imagery\Bathymetry\2004_BelleHavenMarina_Bathymetry',
#r'U:\GIS\Imagery\Bathymetry\2009_DM_Bathymetric Survey - Final_Data\elev1992_ft',
#r'U:\GIS\Imagery\Bathymetry\2009_DM_Bathymetric Survey - Final_Data\elev2009_ft',
#r'U:\GIS\Imagery\CDOQQ',
#r'U:\GIS\Imagery\CIR_Lidar',
#r'U:\GIS\Imagery\CIR_Lidar\DykeMarsh_CIR_2009',
#r'U:\GIS\Imagery\CIR_Lidar\PRWI_CIR_2009',
#r'U:\GIS\Imagery\DOQQ',
#r'U:\GIS\Imagery\IKONOS_4',
#r'U:\GIS\Imagery\IKONOS_4\w7704n3895_12-23-2002_ik2',
#r'U:\GIS\Imagery\IKONOS_4\w7738n3860_06-11-2002_ik2',
#r'U:\GIS\Imagery\IKONOS_4\w7747n3964_11-09-2001_ik2',
#r'U:\GIS\Imagery\IKONOS_4\w7772n3944_11-23-2004_ik2',
#r'U:\GIS\Imagery\LANDSAT_15',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\Earth Explorer\elp015r033_7t20011005',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\From Regional_Data',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\From Regional_Data\18031_000414_ms_utm17',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\18031_000414_ms_utm17',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\19035_000405_ms_utm17',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\L71015033_03320000409.ETM-USGS.LPGS',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\L71015033_03320000612.ETM-USGS.LPGS',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\L71015033_03320010122.ETM-USGS',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\L71015033_03320010428.ETM-USGS',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\p015r033_7x20020906.ETM-EarthSat',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\p015r033_7x20030112.ETM-EarthSat',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\GLCF\p015r33_2m19790615.MSS-EarthSat-Orthorectified',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT050150330412199800',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT050150330503200000',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT070150330728199900',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT070150331021200100',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT070160330524200200',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT070160330804199900',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC\NZT070160331108199900',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_04-12-1998_l5_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_05-03-2000_l5_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_07-28-1999_le7_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-02-2000_le7_MRLC\info',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-21-2001_le7_MRLC\info',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_01-22-2001_le7_GLCF',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_04-09-2000_le7_GLCF',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_04-28-2001_le7_GLCF',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_06-12-2000_le7_GLCF',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_06-18-2002_le7',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_07-14-2000_le7',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_07-28-1999_le7',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_08-02-2001_le7',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_10-05-2001_le7',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_10-05-2001_le7_EE',
#r'U:\GIS\Imagery\LANDSAT_30\p015r033_11-06-2001_le7',
#r'U:\GIS\Imagery\LANDSAT_30\p016033_05-24-2000_le7_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p016033_08-04-1999_le7_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p016033_11-08-1999_le7_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p016r033_05-24-2002_le7',
#r'U:\GIS\Imagery\Lidar',
#r'U:\GIS\Imagery\Lidar\Costa Rica (Kellner paper)',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh\ASCII',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh\ASCII\ALL_POINTS',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh\ASCII\GROUND',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh\LAS',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh\LAS\ALL_POINTS',
#r'U:\GIS\Imagery\Lidar\CVI_2009_Dyke_Marsh\LAS\GROUND',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\ASCII',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\ASCII\All_Points',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\ASCII\Ground',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\LAS',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\LAS\All_Points',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\LAS\Ground',
#r'U:\GIS\Imagery\Lidar\CVI_2009_PRWI\Believed to be an old clipped version\metadata',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2019',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2022',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2025',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2028',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2031',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2034',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2319',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_1\2322',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2325',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2328',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2331',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2334',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2619',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2622',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2625',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_2\2628',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2631',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2634',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2919',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2922',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2925',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2928',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2931',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_3\2934',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3219',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3222',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3225',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3228',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3231',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3234',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3519',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_4\3522',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3525',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3528',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3531',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3534',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3819',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3822',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\3825',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\2337',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\2637',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\2937',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\3237',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\3537',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\3734',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Partial\3828',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Software',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Software\3DEM_RTV',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Software\ERDAS Viewfinder',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Software\GeoTransII',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_5\Software\MICRODEM',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_6',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_7\info',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Bare Earth',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Buildings',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Forests',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Intensity',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Last Return',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Reflective Surface',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Tile_Layout',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_2008\Trees',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\4110',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\4113',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\4410',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\4413',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\4713',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\3DEM_RTV',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\3DEM_RTV\RTV_3DEM_ver4_8',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\ERDAS Viewfinder',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII\geotrans2.2.2',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII\geotrans2.2.2\examples',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII\geotrans2.2.2\geotrans2',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII\geotrans2.2.2\geotrans2\docs',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII\geotrans2.2.2\geotrans2\help',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\GeoTransII\geotrans2.2.2\geotrans2\win',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\MICRODEM',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\MrSid_Viewer',
#r'U:\GIS\Imagery\Lidar\PRWI_Date_Unknown\Software\QT_Reader',
#r'U:\GIS\Imagery\Lidar\WVU_2010_HAFE',
#r'U:\GIS\Imagery\NAIP',
#r'U:\GIS\Imagery\NAIP\MD',
#r'U:\GIS\Imagery\NAIP\Uncompressed',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005\BAWA',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005\CATO',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005\CHOH',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005\FOWA',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005\MONO',
#r'U:\GIS\Imagery\NAIP\Uncompressed\MD 2005\PRWI',
#r'U:\GIS\Imagery\NAIP\Uncompressed\VA 2003',
#r'U:\GIS\Imagery\NAIP\Uncompressed\VA 2003\CHOH',
#r'U:\GIS\Imagery\NAIP\Uncompressed\VA 2003\FOWA',
#r'U:\GIS\Imagery\NAIP\Uncompressed\VA 2003\MANA',
#r'U:\GIS\Imagery\NAIP\Uncompressed\VA 2003\PRWI',
#r'U:\GIS\Imagery\NAIP\Uncompressed\WV 2007',
#r'U:\GIS\Imagery\NAIP\Uncompressed\WV 2007\APPA',
#r'U:\GIS\Imagery\NAIP\Uncompressed\WV 2007\CHOH',
#r'U:\GIS\Imagery\NAIP\VA',
#r'U:\GIS\Imagery\NGS_Topo_4',
#r'U:\GIS\Imagery\NGS_Topo_4\District of Columbia',
#r'U:\GIS\Imagery\NGS_Topo_4\Maryland',
#r'U:\GIS\Imagery\NGS_Topo_4\Virginia',
#r'U:\GIS\Imagery\NGS_Topo_4\West Virginia',
#r'U:\GIS\Imagery\Pilot',
#r'U:\GIS\Imagery\Pilot\ANTI',
#r'U:\GIS\Imagery\Pilot\ANTI\Accuracy_Assessment',
#r'U:\GIS\Imagery\Pilot\ANTI\AOIs',
#r'U:\GIS\Imagery\Pilot\ANTI\DOQQs',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\DEM',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\DEM\10_Meter\info',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\NWI',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\NWI\antinwi',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\NWI\info',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\PARK',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\PARK\antisoils',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\PARK\info',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_bound',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_contour',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_elev',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_hy_line',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_hy_poly',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_hy_pt',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_mt',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_rds',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_rr',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_rr_ply',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\anti_rr_pt',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\info',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\USGS\zztemp',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CO',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_build',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_cll',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_cmajl',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_cminl',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_eopl',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_eossrl',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\anti_eowl',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\WASH_CTY\info',
#r'U:\GIS\Imagery\Pilot\ANTI\IKONOS',
#r'U:\GIS\Imagery\Pilot\ANTI\LANDSAT15',
#r'U:\GIS\Imagery\Pilot\ANTI\LANDSAT30',
#r'U:\GIS\Imagery\Pilot\ANTI\SPOT',
#r'U:\GIS\Imagery\Pilot\CATO',
#r'U:\GIS\Imagery\Pilot\CATO\Accuracy_Assessment',
#r'U:\GIS\Imagery\Pilot\CATO\AOIs',
#r'U:\GIS\Imagery\Pilot\CATO\DOQQs',
#r'U:\GIS\Imagery\Pilot\CATO\GIS',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\boundary',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\boundary\cato_bnd',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\boundary\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID\10_Meter\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID\10m',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID\30m',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\cato_hy_l',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\cato_hy_ply',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\cato_hy_pts',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\cato_hydro',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\catohydr_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\catohyl_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\catohypl_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\catohypt_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hydrography\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hypsography',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hypsography\cato_contour',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hypsography\cato_hp_pts',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hypsography\catocnt_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hypsography\catohppt_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\hypsography\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\pipestrans',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\pipestrans\cato_mt_l',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\pipestrans\cato_mt_ply',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\pipestrans\catomtl_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\pipestrans\catomtply_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\pipestrans\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\railroad',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\railroad\cato_rr_l',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\railroad\cato_rr_pts',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\railroad\catorrl_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\railroad\catorrpt_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\railroad\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\roadstrails',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\roadstrails\catord_u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\roadstrails\info',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dlg\roadstrails\usgs_roads',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\drg',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\drg\100k',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\drg\24k',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\drg\24k\collar',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\drg\24k\collar\info',
#r'U:\GIS\Imagery\Pilot\CATO\IKONOS',
#r'U:\GIS\Imagery\Pilot\CATO\LANDSAT15',
#r'U:\GIS\Imagery\Pilot\CATO\LANDSAT30',
#r'U:\GIS\Imagery\Pilot\CATO\SPOT',
#r'U:\GIS\Imagery\Pilot\PRWI',
#r'U:\GIS\Imagery\Pilot\PRWI\Accuracy_Assessment',
#r'U:\GIS\Imagery\Pilot\PRWI\AOIs',
#r'U:\GIS\Imagery\Pilot\PRWI\DOQQs',
#r'U:\GIS\Imagery\Pilot\PRWI\DOQQs\PRWI_1937',
#r'U:\GIS\Imagery\Pilot\PRWI\DOQQs\PRWI_1954',
#r'U:\GIS\Imagery\Pilot\PRWI\DOQQs\PRWI_CTY',
#r'U:\GIS\Imagery\Pilot\PRWI\DOQQs\VARGIS',
#r'U:\GIS\Imagery\Pilot\PRWI\DOQQs\VARGIS\2000',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\dem',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\dem\10_meter\info',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\NWI',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\NWI\info',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\NWI\prwi_nwi_l',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\NWI\prwi_nwi_poly',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\NWI\prwi_nwi_pt',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\NWI\pw_nwi_l',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PARK',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PARK\info',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PARK\prwi_trails',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PARK\prwi_veg',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\centerlines',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\contours',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\cultply_bld',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\info',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\lakes',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\metadata',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\pwsoils',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\rdedges',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\streams_all',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\streams_arc',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\trails',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\tree',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\PRWI_CTY\veg_wood',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\info',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_bnd_dis',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_bnd_pt',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_hp_l',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_hp_pt',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_hy_dis',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_hy_l',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_ply',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_pt',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_pt_l',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_rr_l',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_rr_ply',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\USGS\pw_rt_l',
#r'U:\GIS\Imagery\Pilot\PRWI\IKONOS',
#r'U:\GIS\Imagery\Pilot\PRWI\LANDSAT15',
#r'U:\GIS\Imagery\Pilot\PRWI\LANDSAT30',
#r'U:\GIS\Imagery\Pilot\PRWI\SPOT',
#r'U:\GIS\Imagery\Pilot\ROCR',
#r'U:\GIS\Imagery\Pilot\ROCR\Accuracy_Assessment',
#r'U:\GIS\Imagery\Pilot\ROCR\AOIs',
#r'U:\GIS\Imagery\Pilot\ROCR\DOQQs',
#r'U:\GIS\Imagery\Pilot\ROCR\DOQQs\DC',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\building',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\curb',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\hydro',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\info',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\railroad',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\road',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\soil',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\topoln',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\topopnt',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\tree',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\water',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\woodland',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\DC_GOVT\zone',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\dem',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\dem\10_meter\info',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\NWI',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\NWI\info',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\NWI\nwi',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\NWI\nwi_pts',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\info',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\landuse_dc',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_10_flood',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_100_flood',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_2_flood',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_geo_wshed',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_sepsewers',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_sheds',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_strmsewer',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_subsheds',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_trail',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\Park\rcp_veg',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\info',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_dlg_pt',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_dlg_rail',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_dlg_rt',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_dlgbnd',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_hpcontour',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_hpelev',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_hy_lines',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_hy_poly',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\USGS\rc_hy_pts',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\xlsdata',
#r'U:\GIS\Imagery\Pilot\ROCR\IKONOS',
#r'U:\GIS\Imagery\Pilot\ROCR\LANDSAT15',
#r'U:\GIS\Imagery\Pilot\ROCR\LANDSAT30',
#r'U:\GIS\Imagery\Pilot\ROCR\SPOT',
#r'U:\GIS\Imagery\SPOT_10\k621j270_06-26-2003_sp5',
#r'U:\GIS\Imagery\SPOT_10\k621j271_10-15-2006_sp5',
#r'U:\GIS\Imagery\SPOT_10\k621j272_10-15-2006_sp5',
#r'U:\GIS\Imagery\SPOT_10\k622j271_09-29-2002_sp5',
#r'U:\GIS\Imagery\SPOT_10\k622j272_07-17-2003_sp5',
#r'U:\GIS\Imagery\VARGIS',
#r'U:\GIS\Imagery\Veg_Mapping_2004',
#r'U:\GIS\Imagery\Veg_Mapping_2004\ANTI\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\ANTI\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\ANTI\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\ANTI\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CATO',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CATO\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CHOH\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CHOH\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CHOH\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CHOH\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\Tiles_#1',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\Tiles_#2',
#r'U:\GIS\Imagery\Veg_Mapping_2004\HAFE\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\HAFE\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\HAFE\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\HAFE\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MANA\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MANA\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MANA\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MANA\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MONO\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MONO\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MONO\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MONO\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\NACE\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\NACE\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\NACE\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\NACE\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\PRWI\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\PRWI\DEM-Esri-Arc-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\PRWI\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\PRWI\Tile Index',
#r'U:\GIS\Imagery\Veg_Mapping_2004\WOTR\Boundary',
#r'U:\GIS\Imagery\Veg_Mapping_2004\WOTR\DEM-Esri-ARC-Grid\info',
#r'U:\GIS\Imagery\Veg_Mapping_2004\WOTR\Mosaic',
#r'U:\GIS\Imagery\Veg_Mapping_2004\WOTR\Tile Index',
#r'U:\GIS\MANA',
#r'U:\GIS\MANA\Boundary',
#r'U:\GIS\MANA\Boundary\Archive',
#r'U:\GIS\MANA\Elevation',
#r'U:\GIS\MANA\Elevation\Hypsography',
#r'U:\GIS\MANA\Fauna',
#r'U:\GIS\MANA\Fauna\Amphibians',
#r'U:\GIS\MANA\Geology',
#r'U:\GIS\MANA\Landcover',
#r'U:\GIS\MANA\Landcover\NLCD',
#r'U:\GIS\MANA\Landcover\regrasslands',
#r'U:\GIS\MANA\Soil',
#r'U:\GIS\MANA\Structures',
#r'U:\GIS\MANA\Transportation',
#r'U:\GIS\MONO',
#r'U:\GIS\MONO\Boundary',
#r'U:\GIS\MONO\Boundary\Archive',
#r'U:\GIS\MONO\Elevation',
#r'U:\GIS\MONO\Elevation\Hypsography',
#r'U:\GIS\MONO\Geology',
#r'U:\GIS\MONO\Soil',
#r'U:\GIS\MONO\Structures',
#r'U:\GIS\MONO\Transportation',
#r'U:\GIS\MONO\Water',
#r'U:\GIS\NACE',
#r'U:\GIS\NACE\Boundary',
#r'U:\GIS\NACE\Boundary\Archive',
#r'U:\GIS\NACE\Elevation',
#r'U:\GIS\NACE\Elevation\Hypsography',
#r'U:\GIS\NACE\Geology',
#r'U:\GIS\NACE\Geology\Layer_Package_For_Mikaila',
#r'U:\GIS\NACE\Legacy',
#r'U:\GIS\NACE\Structures',
#r'U:\GIS\NACE\Transportation',
#r'U:\GIS\NAMA',
#r'U:\GIS\NAMA\Structures',
#r'U:\GIS\NATIONAL',
#r'U:\GIS\NATIONAL\Boundary',
#r'U:\GIS\NATIONAL\Boundary\I&M Network Map',
#r'U:\GIS\NATIONAL\Boundary\LCC',
#r'U:\GIS\NATIONAL\Boundary\NPS Park Boundaries',
#r'U:\GIS\NATIONAL\Boundary\NPS Park Boundaries\Archive',
#r'U:\GIS\NATIONAL\Boundary\NPS Park Boundaries\Archive\Nov 2010',
#r'U:\GIS\NATIONAL\Boundary\NPS Regions',
#r'U:\GIS\NATIONAL\Elevation All Parks\info',
#r'U:\GIS\NATIONAL\Elevation All Parks\mask',
#r'U:\GIS\NATIONAL\Elevation All Parks\na_gtopo30c',
#r'U:\GIS\NATIONAL\Elevation All Parks\na_gtopo30d',
#r'U:\GIS\NATIONAL\Elevation All Parks\nps_boundr',
#r'U:\GIS\NATIONAL\Elevation All Parks\Raw Data\info',
#r'U:\GIS\NATIONAL\Elevation All Parks\Raw Data\w180n40',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\help',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\streetmap_na',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\streetmap_na\background',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\streetmap_na\data',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\streetmap_na\data\streets.rsx',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa\background',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa\census',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa\hydro',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa\landmarks',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa\other',
#r'U:\GIS\NATIONAL\ESRI_Data_10_1\usa\trans',
#r'U:\GIS\NATIONAL\Hydro',
#r'U:\GIS\NATIONAL\Hydro\USGS Gaging Stations',
#r'U:\GIS\NATIONAL\Landcover',
#r'U:\GIS\NATIONAL\Landcover\BioRegions',
#r'U:\GIS\NATIONAL\Landcover\Domains_NEON\info',
#r'U:\GIS\NATIONAL\Landcover\Ecoregion_Bailey',
#r'U:\GIS\NATIONAL\Landcover\Ecoregion_Omernik',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2001',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2001\NLCD2001_impervious_v2_5-4-11',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2001\NLCD2001_landcover_v2_2-13-11',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006\NLCD2006_impervious_5-4-11',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006\NLCD2006_landcover_4-20-11_se5',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006\NLCD2006_landcover_change_pixels_5-4-11_se5',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006\NLCD2006_landcover_fromto_change_index_5-2-11',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006\NLCD2006_max_potential_chgpix_2-14-11',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2006\NLCD2006_path_row_index_2-11-11',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2006_to_2011_impervious_change_pixels_2011_edition_2014_03_31',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2006_to_2011_impervious_change_pixels_2011_edition_2014_03_31\10_nlcd_2006_2011_impervious_change_2011_edition_20140331',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2006_to_2011_impervious_change_pixels_2011_edition_2014_03_31\10_nlcd_2006_2011_impervious_change_2011_edition_20140331\spatial_metadata',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2006_to_2011_landcover_change_pixels_2011_edition_2014_03_31',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2006_to_2011_landcover_change_pixels_2011_edition_2014_03_31\09_nlcd_2006_2011_landcover_change_pixels_2011_edition_2014031',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2006_to_2011_landcover_change_pixels_2011_edition_2014_03_31\09_nlcd_2006_2011_landcover_change_pixels_2011_edition_2014031\spatial_metadata',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_impervious_2011_edition_2014_03_31',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_impervious_2011_edition_2014_03_31\08_nlcd2011_impervious_2011_edition_20140331',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_impervious_2011_edition_2014_03_31\08_nlcd2011_impervious_2011_edition_20140331\spatial_metadata',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_landcover_2011_edition_2014_03_31',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_landcover_2011_edition_2014_03_31\07_nlcd2011_landcover_2011_edition_20140331',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_landcover_2011_edition_2014_03_31\07_nlcd2011_landcover_2011_edition_20140331\spatial_metadata',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_landcover_2011_edition_2014_10_10',
#r'U:\GIS\NATIONAL\Landcover\NLCD_2011\nlcd_2011_landcover_2011_edition_2014_10_10\spatial_metadata',
#r'U:\GIS\NATIONAL\Landcover\PADUS1_2_Geodatabase',
#r'U:\GIS\NCRN',
#r'U:\GIS\NCRN\_ARCHIVE',
#r'U:\GIS\NCRN\_ARCHIVE\2017',
#r'U:\GIS\NCRN\_ARCHIVE\2018',
#r'U:\GIS\NCRN\_ARCHIVE\2019',
#r'U:\GIS\NCRN\Air',
#r'U:\GIS\NCRN\Boundary',
#r'U:\GIS\NCRN\Boundary\Archive',
#r'U:\GIS\NCRN\Boundary\Bioblitz_Subunits',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\ANTI',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\CATO',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\CHOH',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\GWMP',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\HAFE',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\MANA',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\MONO',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\NACE',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\PRWI',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\ROCR',
#r'U:\GIS\NCRN\Boundary\NCRN_Boundaries_by_Park\WOTR',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\ANTI_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\CATO_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\FOWA_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\FRDO_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\GREE_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\GWMP_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\HAFE_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\MANA_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\MONO_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\naca_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\nps_boundary',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\PISC_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\prwi_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\DOWNLOADS_IRMA\WOTR_tracts',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\Project_Albers',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\Project_Albers\IandM_2006_Maps',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\20151028_Downloads\Project_Albers\Maps',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\Latest_IRMA_BoundaryFiles_20150425',
#r'U:\GIS\NCRN\Boundary\NPScape_Boundary_Drafts\OldBoundaryDrafts',
#r'U:\GIS\NCRN\Boundary\USGS Quad Boundaries',
#r'U:\GIS\NCRN\Civic',
#r'U:\GIS\NCRN\Cultural',
#r'U:\GIS\NCRN\Elevation',
#r'U:\GIS\NCRN\Elevation\Hypsography',
#r'U:\GIS\NCRN\Elevation\NED_10m',
#r'U:\GIS\NCRN\Elevation\NED_30m',
#r'U:\GIS\NCRN\Elevation\NED_30m\Native Projection\info',
#r'U:\GIS\NCRN\Elevation\NED_30m\Native Projection\ncrn_ned_m',
#r'U:\GIS\NCRN\Elevation\NED_3m',
#r'U:\GIS\NCRN\Elevation\NED_3m\Archive',
#r'U:\GIS\NCRN\Flora',
#r'U:\GIS\NCRN\Geology',
#r'U:\GIS\NCRN\Geology\ANTI',
#r'U:\GIS\NCRN\Geology\CATO',
#r'U:\GIS\NCRN\Geology\CATO\Geodatabase',
#r'U:\GIS\NCRN\Geology\CATO\Shapefile',
#r'U:\GIS\NCRN\Geology\CHOH',
#r'U:\GIS\NCRN\Geology\HAFE',
#r'U:\GIS\NCRN\Geology\MANA',
#r'U:\GIS\NCRN\Geology\MANA\Geodatabase',
#r'U:\GIS\NCRN\Geology\MANA\Shapefile',
#r'U:\GIS\NCRN\Geology\metadata',
#r'U:\GIS\NCRN\Geology\MONO',
#r'U:\GIS\NCRN\Geology\MONO\Geodatabase',
#r'U:\GIS\NCRN\Geology\MONO\Shapefile',
#r'U:\GIS\NCRN\Geology\NCAP - NACE_GWMP_ROCR',
#r'U:\GIS\NCRN\Geology\NCAP - NACE_GWMP_ROCR\Geodatabase',
#r'U:\GIS\NCRN\Geology\NCAP - NACE_GWMP_ROCR\Shapefile',
#r'U:\GIS\NCRN\Geology\PRWI',
#r'U:\GIS\NCRN\Geology\PRWI\Geodatabase',
#r'U:\GIS\NCRN\Geology\PRWI\Shapefile',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\ANTI',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\CATO',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\CHOH',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\GWMP',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\HAFE',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\MANA',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\MONO',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\NACE',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\PRWI',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\ROCR',
#r'U:\GIS\NCRN\Geology\Reports and Park Maps\WOTR',
#r'U:\GIS\NCRN\Geology\Retired',
#r'U:\GIS\NCRN\Geology\Retired\ANTI',
#r'U:\GIS\NCRN\Geology\Retired\CATO',
#r'U:\GIS\NCRN\Geology\Retired\CHOH',
#r'U:\GIS\NCRN\Geology\Retired\dc_gwp',
#r'U:\GIS\NCRN\Geology\Retired\greatfalls',
#r'U:\GIS\NCRN\Geology\Retired\HAFE',
#r'U:\GIS\NCRN\Geology\Retired\MANA',
#r'U:\GIS\NCRN\Geology\Retired\MONO',
#r'U:\GIS\NCRN\Geology\Retired\PRWI',
#r'U:\GIS\NCRN\Geology\Retired\ROCR',
#r'U:\GIS\NCRN\Geology\Retired\WOTR',
#r'U:\GIS\NCRN\Geology\WOTR',
#r'U:\GIS\NCRN\Geology\WOTR\Geodatabase',
#r'U:\GIS\NCRN\Geology\WOTR\Shapefile',
#r'U:\GIS\NCRN\Geology\zips',
#r'U:\GIS\NCRN\Geology\zips\2008-07 Downloads',
#r'U:\GIS\NCRN\Geology\zips\2008-07 Downloads\ROCR',
#r'U:\GIS\NCRN\Geology\zips\2008-07 Downloads\WOTR',
#r'U:\GIS\NCRN\Geology\zips\2008-07 Downloads\WOTR\wotrgdb',
#r'U:\GIS\NCRN\Geology\zips\2008-07 Downloads\WOTR\wotrshp',
#r'U:\GIS\NCRN\Geology\zips\Data Store',
#r'U:\GIS\NCRN\Geology\zips\USGS',
#r'U:\GIS\NCRN\HERP Monitoring',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\ANTI_ACS_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\ANTI_ACS_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\ANTI_MAP_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\ANTI_MAP_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\MANA_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\MANA_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\PRWI_1_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\PRWI_1_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\PRWI_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\PRWI_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\PRWI_WETLANDS_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\PRWI_WETLANDS_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_HBE_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_HBE_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_HBW1_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_HBW1_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_R071117A_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_R071117A_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_SME_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_SME_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_SMW_Trimble2016_Corrected',
#r'U:\GIS\NCRN\HERP Monitoring\Amphibian_Trimble_Processed\SHEN_SMW_Trimble2016_Raw',
#r'U:\GIS\NCRN\HERP Monitoring\GIS Layer Update',
#r'U:\GIS\NCRN\HERP Monitoring\Herp Site shp',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\CATO_HERP',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\GWMP_HERP',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\MANA_HERP',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\MONO_HERP',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\NACE_HERP',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\Shared Map Layers',
#r'U:\GIS\NCRN\HERP Monitoring\NCR_HERP_LocationMaps\WOTR_HERP',
#r'U:\GIS\NCRN\Landcover',
#r'U:\GIS\NCRN\Landcover\CCAP',
#r'U:\GIS\NCRN\Landcover\CDL',
#r'U:\GIS\NCRN\Landcover\Fauna',
#r'U:\GIS\NCRN\Landcover\Forest_Lidar',
#r'U:\GIS\NCRN\Landcover\NLCD',
#r'U:\GIS\NCRN\Landcover\NLCD\info',
#r'U:\GIS\NCRN\Plots_with_State_County_attributes',
#r'U:\GIS\NCRN\Retired',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\Birds',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\CATO_Geology',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\CATO_Geology\Geodatabase',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\Deer',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\Draft Layer Files',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\MANA_Geology',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\MANA_Geology\Geodatabase',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\MONO_Geology',
#r'U:\GIS\NCRN\Retired\2016_Redundant_Folders_Files\MONO_Geology\Geodatabase',
#r'U:\GIS\NCRN\Retired\FloraFromRegional',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI\ANTI_DRG',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI\ANTI_LYR',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI\ANTI_MapClassImages',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI\ANTI_PDF',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI\ANTI_Shapefiles',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\ANTI\ANTI_Veg_Metadata',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO\CATO_DRG',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO\CATO_LYR',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO\CATO_MapClassImages',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO\CATO_PDF',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO\CATO_Shapefiles',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\CATO\CATO_Veg_Metadata',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_DRG',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_LYR',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_MapClassImages',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_MapClassImages\ObsoleteImages',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_MapLayouts',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_PDF',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_PDF\AssociationMaps',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_PDF\SystemsMaps',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_Shapefiles',
#r'U:\GIS\NCRN\Retired\NCRN_Vegetation_Draft\GWMP\GWMP_Veg_Metadata',
#r'U:\GIS\NCRN\Soil',
#r'U:\GIS\NCRN\Soil\SSURGO',
#r'U:\GIS\NCRN\Soil\SSURGO\Alexandria_wss_SSA_VA510_soildb_US_2003_2009-12-14',
#r'U:\GIS\NCRN\Soil\SSURGO\Alexandria_wss_SSA_VA510_soildb_US_2003_2009-12-14\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Alexandria_wss_SSA_VA510_soildb_US_2003_2009-12-14\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Allegany_wss_SSA_MD001_soildb_US_2003_2009-03-12',
#r'U:\GIS\NCRN\Soil\SSURGO\Allegany_wss_SSA_MD001_soildb_US_2003_2009-03-12\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Allegany_wss_SSA_MD001_soildb_US_2003_2009-03-12\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Anne_Arundel_wss_SSA_MD003_soildb_US_2003_2011-01-27',
#r'U:\GIS\NCRN\Soil\SSURGO\Anne_Arundel_wss_SSA_MD003_soildb_US_2003_2011-01-27\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Anne_Arundel_wss_SSA_MD003_soildb_US_2003_2011-01-27\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Arlington_wss_SSA_VA013_soildb_US_2003_2010-08-09',
#r'U:\GIS\NCRN\Soil\SSURGO\Arlington_wss_SSA_VA013_soildb_US_2003_2010-08-09\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Arlington_wss_SSA_VA013_soildb_US_2003_2010-08-09\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Berkeley_wss_SSA_WV003_soildb_WV_2003_2012-09-27',
#r'U:\GIS\NCRN\Soil\SSURGO\Berkeley_wss_SSA_WV003_soildb_WV_2003_2012-09-27\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Berkeley_wss_SSA_WV003_soildb_WV_2003_2012-09-27\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Charles_wss_SSA_MD017_soildb_US_2003_2009-03-09',
#r'U:\GIS\NCRN\Soil\SSURGO\Charles_wss_SSA_MD017_soildb_US_2003_2009-03-09\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Charles_wss_SSA_MD017_soildb_US_2003_2009-03-09\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\DC_wss_SSA_DC001_soildb_DC_2003_2006-09-14',
#r'U:\GIS\NCRN\Soil\SSURGO\DC_wss_SSA_DC001_soildb_DC_2003_2006-09-14\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\DC_wss_SSA_DC001_soildb_DC_2003_2006-09-14\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Fairfax_wss_SSA_VA059_soildb_US_2003_2010-08-19',
#r'U:\GIS\NCRN\Soil\SSURGO\Fairfax_wss_SSA_VA059_soildb_US_2003_2010-08-19\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Fairfax_wss_SSA_VA059_soildb_US_2003_2010-08-19\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\FairfaxCity_wss_SSA_VA600_soildb_US_2003_2009-11-17',
#r'U:\GIS\NCRN\Soil\SSURGO\FairfaxCity_wss_SSA_VA600_soildb_US_2003_2009-11-17\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\FairfaxCity_wss_SSA_VA600_soildb_US_2003_2009-11-17\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Falls_Church_wss_SSA_VA610_soildb_US_2003_2009-12-14',
#r'U:\GIS\NCRN\Soil\SSURGO\Falls_Church_wss_SSA_VA610_soildb_US_2003_2009-12-14\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Falls_Church_wss_SSA_VA610_soildb_US_2003_2009-12-14\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Frederick_wss_SSA_MD021_soildb_US_2003_2010-08-09',
#r'U:\GIS\NCRN\Soil\SSURGO\Frederick_wss_SSA_MD021_soildb_US_2003_2010-08-09\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Frederick_wss_SSA_MD021_soildb_US_2003_2010-08-09\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Howard_wss_SSA_MD027_soildb_US_2003_2008-05-15',
#r'U:\GIS\NCRN\Soil\SSURGO\Howard_wss_SSA_MD027_soildb_US_2003_2008-05-15\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Howard_wss_SSA_MD027_soildb_US_2003_2008-05-15\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Jefferson_wss_SSA_WV037_soildb_WV_2003_2012-10-04',
#r'U:\GIS\NCRN\Soil\SSURGO\Jefferson_wss_SSA_WV037_soildb_WV_2003_2012-10-04\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Jefferson_wss_SSA_WV037_soildb_WV_2003_2012-10-04\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Loudoun_wss_SSA_VA107_soildb_US_2003_2010-08-09',
#r'U:\GIS\NCRN\Soil\SSURGO\Loudoun_wss_SSA_VA107_soildb_US_2003_2010-08-09\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Loudoun_wss_SSA_VA107_soildb_US_2003_2010-08-09\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Mineral_wss_SSA_WV608_soildb_WV_2003_2012-09-28',
#r'U:\GIS\NCRN\Soil\SSURGO\Mineral_wss_SSA_WV608_soildb_WV_2003_2012-09-28\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Mineral_wss_SSA_WV608_soildb_WV_2003_2012-09-28\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Montogomery_wss_SSA_MD031_soildb_US_2003_2007-02-02',
#r'U:\GIS\NCRN\Soil\SSURGO\Montogomery_wss_SSA_MD031_soildb_US_2003_2007-02-02\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Montogomery_wss_SSA_MD031_soildb_US_2003_2007-02-02\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Morgan_wss_SSA_WV065_soildb_WV_2003_2012-09-28',
#r'U:\GIS\NCRN\Soil\SSURGO\Morgan_wss_SSA_WV065_soildb_WV_2003_2012-09-28\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Morgan_wss_SSA_WV065_soildb_WV_2003_2012-09-28\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Prince_Georges_wss_SSA_MD033_soildb_US_2003_2009-12-16',
#r'U:\GIS\NCRN\Soil\SSURGO\Prince_Georges_wss_SSA_MD033_soildb_US_2003_2009-12-16\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Prince_Georges_wss_SSA_MD033_soildb_US_2003_2009-12-16\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Prince_William_wss_SSA_VA153_soildb_US_2003_2010-01-25',
#r'U:\GIS\NCRN\Soil\SSURGO\Prince_William_wss_SSA_VA153_soildb_US_2003_2010-01-25\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Prince_William_wss_SSA_VA153_soildb_US_2003_2010-01-25\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Stafford_wss_SSA_VA179_soildb_US_2003_2010-01-11',
#r'U:\GIS\NCRN\Soil\SSURGO\Stafford_wss_SSA_VA179_soildb_US_2003_2010-01-11\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Stafford_wss_SSA_VA179_soildb_US_2003_2010-01-11\tabular',
#r'U:\GIS\NCRN\Soil\SSURGO\Washington_wss_SSA_MD043_soildb_US_2003_2009-03-12',
#r'U:\GIS\NCRN\Soil\SSURGO\Washington_wss_SSA_MD043_soildb_US_2003_2009-03-12\spatial',
#r'U:\GIS\NCRN\Soil\SSURGO\Washington_wss_SSA_MD043_soildb_US_2003_2009-03-12\tabular',
#r'U:\GIS\NCRN\Structures',
#r'U:\GIS\NCRN\Templates',
#r'U:\GIS\NCRN\Templates\1',
#r'U:\GIS\NCRN\Transportation',
#r'U:\GIS\NCRN\Transportation\NCR_Trails_v1_20100922',
#r'U:\GIS\NCRN\Water',
#r'U:\GIS\NCRN\Water\MarylandBiologicalStreamSurvey',
#r'U:\GIS\NCRN\Water\NHD',
#r'U:\GIS\NCRN\Water\NHD\NHDDocs',
#r'U:\GIS\NCRN\Water\NHD\Retired',
#r'U:\GIS\NCRN\Water\NHD\Retired\v2_0',
#r'U:\GIS\NCRN\Water\NHD\Retired\v2_0\NHDDocs',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\EROMExtension',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NEDSnapshot',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NEDSnapshot\Ned02a\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusAttributes',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusBurnComponents',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusCatchment\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusCatSeed02a\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrFac02a\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrNull02a\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFilledAreas02a\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusHydrodem02a\info',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDSnapshot',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDSnapshot\Hydrography',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\VogelExtension',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\VPUAttributeExtension',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\WBDSnapshot',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\WBDSnapshot\WBD',
#r'U:\GIS\NCRN\Water\Water_BaseFiles',
#r'U:\GIS\Other',
#r'U:\GIS\Other\APPA',
#r'U:\GIS\Other\APPA\AppalachianStreamClassification',
#r'U:\GIS\Other\APPA\AppalachianStreamClassification\flowlines_6_5_2015',
#r'U:\GIS\Other\APPA\Legacy',
#r'U:\GIS\Other\APPA\Legacy\AppTrail',
#r'U:\GIS\Other\CGAT',
#r'U:\GIS\Other\CGAT\AOA',
#r'U:\GIS\Other\CGAT\CGAT',
#r'U:\GIS\Other\CGAT\Data',
#r'U:\GIS\Other\CGAT\Documentation',
#r'U:\GIS\Other\CGAT\Old Versions',
#r'U:\GIS\Other\CGAT\Output',
#r'U:\GIS\Other\CHESAPEAKE_BAY',
#r'U:\GIS\Other\KML',
#r'U:\GIS\Other\LEGACY',
#r'U:\GIS\Other\New_Downloads',
#r'U:\GIS\Projects',
#r'U:\GIS\PRWI',
#r'U:\GIS\REGIONAL',
#r'U:\GIS\ROCR',
#r'U:\GIS\WORLD',
#r'U:\GIS\WOTR',
#r'U:\GIS\ANTI',
#r'U:\GIS\Imagery\Bathymetry\2009_DM_Bathymetric Survey - Final_Data',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\Earth Explorer',
#r'U:\GIS\Imagery\LANDSAT_30\Downloads\MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-02-2000_le7_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-02-2000_le7_MRLC\project_1',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-02-2000_le7_MRLC\project_1c1',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-02-2000_le7_MRLC\project_1c2',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-02-2000_le7_MRLC\project_1c3',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-21-2001_le7_MRLC',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-21-2001_le7_MRLC\project_1',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-21-2001_le7_MRLC\project_1c1',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-21-2001_le7_MRLC\project_1c2',
#r'U:\GIS\Imagery\LANDSAT_30\p015033_10-21-2001_le7_MRLC\project_1c3',
#r'U:\GIS\Imagery\LANDSAT_30',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_7',
#r'U:\GIS\Imagery\Lidar\DC_LiDAR_04-05\LIDAR\Disk_7\bare_mosaic',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\DEM\10_Meter',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\DEM\10_Meter\ANTI_10m_DEM',
#r'U:\GIS\Imagery\Pilot\ANTI\GIS\DEM\10_Meter\anti_d10u',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID\10_Meter',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID\10_Meter\cato_10m_dem',
#r'U:\GIS\Imagery\Pilot\CATO\GIS\dem\GRID\10_Meter\cato_d10u',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\dem\10_meter',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\dem\10_meter\PRWI_10m_DEM',
#r'U:\GIS\Imagery\Pilot\PRWI\GIS\dem\10_meter\prwi_d10u',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\dem\10_meter',
#r'U:\GIS\Imagery\Pilot\ROCR\GIS\dem\10_meter\rocr_10m_dem',
#r'U:\GIS\Imagery\SPOT_10',
#r'U:\GIS\Imagery\Veg_Mapping_2004\ANTI',
#r'U:\GIS\Imagery\Veg_Mapping_2004\ANTI\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CHOH',
#r'U:\GIS\Imagery\Veg_Mapping_2004\CHOH\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP',
#r'U:\GIS\Imagery\Veg_Mapping_2004\GWMP\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\HAFE',
#r'U:\GIS\Imagery\Veg_Mapping_2004\HAFE\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MANA',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MANA\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MONO',
#r'U:\GIS\Imagery\Veg_Mapping_2004\MONO\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\NACE',
#r'U:\GIS\Imagery\Veg_Mapping_2004\NACE\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\PRWI',
#r'U:\GIS\Imagery\Veg_Mapping_2004\PRWI\DEM-Esri-Arc-Grid',
#r'U:\GIS\Imagery\Veg_Mapping_2004\WOTR',
#r'U:\GIS\Imagery\Veg_Mapping_2004\WOTR\DEM-Esri-ARC-Grid',
#r'U:\GIS\NATIONAL\Elevation All Parks',
#r'U:\GIS\NATIONAL\Elevation All Parks\Raw Data',
#r'U:\GIS\NATIONAL\Landcover\Domains_NEON',
#r'U:\GIS\NATIONAL\Landcover\Domains_NEON\neon',
#r'U:\GIS\NCRN\Elevation\NED_30m\Native Projection',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NEDSnapshot\Ned02a',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NEDSnapshot\Ned02a\elev_cm',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NEDSnapshot\Ned02a\shdrelief',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusCatchment',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusCatchment\cat',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusCatSeed02a',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusCatSeed02a\catseed',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrFac02a',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrFac02a\fac',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrFac02a\fdr',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrNull02a',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFdrNull02a\fdrnull',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFilledAreas02a',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusFilledAreas02a\filledareas',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusHydrodem02a',
#r'U:\GIS\NCRN\Water\NHDPlus_v2_1\NHDPlusHydrodem02a\hydrodem']

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
            
    
