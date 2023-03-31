#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial working script for downloading GIS data and formatting the NCRN GIS Library.
--------------------------------------------------------------------------------
TODO: Add more of a complete description.
"""

#__author__ = "NCRN GIS Unit"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.2"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"

# Import statements for utilized libraries / packages
import arcpy
import os
import sys
import pandas as pd
from arcpy import metadata as md

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool

_WORKSPACE = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\GIS\Geodata\NCRN' ## Update this to be the directory where the geodatabase should be created

__XCEL_LIBRARY = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_GIS_Data_Standard\NCRN-GIS-Data-Standard.xlsx' ## Create a variable to store the full path to the NCRN GIS Data Standard Excel file

in_gdb = r'NCRN_Monitoring_Locations.gdb' ## Change the name of the geodatabase as needed

ds = r'IMD' ## Change the name of the feature dataset as needed

in_srs = r'NAD_1983_UTM_Zone_18N.prj' ## Update this based on the spatial reference system standard for the network

# Names of feature classes to be created
# Need to update if adding new feature classes to the data model, renaming feature classes, etc.
locations_pt = 'ECO_MonitoringLocations_pt'
locations_data_pt = 'ECO_MonitoringLocationsData_pt'
locations_data_ln = 'ECO_MonitoringLocationsData_ln'
locations_data_py = 'ECO_MonitoringLocationsData_py'
locations_logistics_pt = 'ECO_MonitoringLocationLogistics_pt'
locations_logistics_ln = 'ECO_MonitoringLocationLogistics_ln'
locations_logistics_py = 'ECO_MonitoringLocationLogistics_py'

## Read excel into dataframes using Pandas
df_domains = pd.read_excel(__XCEL_LIBRARY, sheet_name='domains')
df_domain_values = pd.read_excel(__XCEL_LIBRARY, sheet_name='domain_values')
df_monloc_fields = pd.read_excel(__XCEL_LIBRARY, sheet_name='monloc_fields')
df_monlocdata_fields = pd.read_excel(__XCEL_LIBRARY, sheet_name='monlocdata_fields')
df_monloclogistics_fields = pd.read_excel(__XCEL_LIBRARY, sheet_name='monloclogistics_fields')

## Create a spatial reference object
sr = arcpy.SpatialReference(os.path.join(_WORKSPACE, in_srs))

# Create the geodatabase
try:
    # Create a new file geodatabase
    arcpy.CreateFileGDB_management(_WORKSPACE, in_gdb)
    print("Finished creating: {0}".format(in_gdb))
    # Create the IMD feature dataset
    arcpy.CreateFeatureDataset_management(os.path.join(_WORKSPACE,in_gdb), ds, sr)
    print("Finished creating feature dataset: {0}".format(ds))
except:
    print("File geodatabase already exists")

# Set the ArcPy workspace to the geodatabase
arcpy.env.workspace = os.path.join(_WORKSPACE, in_gdb)

# Create a list of all the domains to be created
domains_list = []
for index, row in df_domains.iterrows():
    domains_list.append(row['Domain Name'])

## Loop over all the domains in the list and create them
for domain in domains_list:
    arcpy.management.CreateDomain(arcpy.env.workspace, domain, '', 'TEXT', 'CODED', 'DEFAULT', 'DEFAULT')
    print("Created domain: {0}".format(domain))
    
## Create a list of lists for all the domain values to be created
domain_values_list = []
for index, row in df_domain_values.iterrows():
    if row['Code'] == True:
        domain_value = [arcpy.env.workspace, row['Domain Name'], 'TRUE', 'TRUE']
    elif row['Code'] == False:
        domain_value = [arcpy.env.workspace, row['Domain Name'], 'FALSE', 'FALSE']
    else:
        domain_value = [arcpy.env.workspace, row['Domain Name'], row['Code'], row['Description']]
    domain_values_list.append(domain_value)

# Added domain values to domains
for value in domain_values_list:
    arcpy.AddCodedValueToDomain_management(value[0], value[1], value[2], value[3])
    print("Added [{0}] domain value to [{1}] domain".format(value[2], value[0]))

# Set the ArcPy workspace to the Feature Dataset
arcpy.env.workspace = os.path.join(_WORKSPACE, in_gdb, ds)

# Create a dictionary of feature class names to be created as keys and geometry types as values
create_fcs_dict = {1:[locations_pt,'POINT'], 
                   2:[locations_data_pt,'POINT'], 
                   3:[locations_data_ln,'POLYLINE'], 
                   4:[locations_data_py,'POLYGON'],
                   5:[locations_logistics_pt, 'POINT'],
                   6:[locations_logistics_ln, 'POLYLINE'],
                   7:[locations_logistics_py, 'POLYGON']}

# Create all the feature classes
for k, v in create_fcs_dict.items():
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, v[0], v[1], '', 'DISABLED', 'DISABLED', sr)
    print("Done creating feature class: [{0}]".format(v[0]))

# Create a list of fields to be added to monitoring locations
monloc_fields_list = []
for index, row in df_monloc_fields.iterrows():
    if row['DataType'] == 'TEXT':
        field = [row['Field'], row['DataType'], '', '', row['Length'], row['Alias'], row['Nullable'], row['Required'], '']
        monloc_fields_list.append(field)
    else:
        field = [row['Field'], row['DataType'], '', '', '', row['Alias'], row['Nullable'], row['Required'], '']
        monloc_fields_list.append(field)

# Create a list of fields to be added to monitoring locations data
monlocdata_fields_list = []
for index, row in df_monlocdata_fields.iterrows():
    if row['DataType'] == 'TEXT':
        field = [row['Field'], row['DataType'], '', '', row['Length'], row['Alias'], row['Nullable'], row['Required'], '']
        monlocdata_fields_list.append(field)
    else:
        field = [row['Field'], row['DataType'], '', '', '', row['Alias'], row['Nullable'], row['Required'], '']
        monlocdata_fields_list.append(field)

# Create a list of fields to be added to monitoring locations logistics
monloclogistics_fields_list = []
for index, row in df_monloclogistics_fields.iterrows():
    if row['DataType'] == 'TEXT':
        field = [row['Field'], row['DataType'], '', '', row['Length'], row['Alias'], row['Nullable'], row['Required'], '']
        monloclogistics_fields_list.append(field)
    else:
        field = [row['Field'], row['DataType'], '', '', '', row['Alias'], row['Nullable'], row['Required'], '']
        monloclogistics_fields_list.append(field)

## Add the fields to the feature classes
for fc in arcpy.ListFeatureClasses():
    print("This is the fc: {0}".format(fc))
    if fc.endswith('_pt'):
        geom_type = 'POINTTYPE'
    elif fc.endswith('_ln'):
        geom_type = 'LINETYPE'
    else:
        geom_type = 'POLYGONTYPE'
    if 'Data_' in fc:
        # This will get the fields added to monitoring locations data
        for fld in monlocdata_fields_list:
            if fld[0] == '__TYPE__':
                arcpy.AddField_management(fc, geom_type, fld[1], fld[2], fld[3], fld[4], geom_type, fld[6], fld[7], fld[8])
            else:
                arcpy.AddField_management(fc, fld[0], fld[1], fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8])
            print("Done creating field [{0}] in [{1}]".format(fld[0], fc))
    elif 'Logistics' in fc:
        # This will get the fields added monitoring locations logistics
        for fld in monloclogistics_fields_list:
            if fld[0] == '__TYPE__':
                arcpy.AddField_management(fc, geom_type, fld[1], fld[2], fld[3], fld[4], geom_type, fld[6], fld[7], fld[8])
            else:
                arcpy.AddField_management(fc, fld[0], fld[1], fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8])
    else:
        # This will get the fields added to monitoring locations
        for fld in monloc_fields_list:
            if fld[0] == '__TYPE__':
                arcpy.AddField_management(fc, geom_type, fld[1], fld[2], fld[3], fld[4], geom_type, fld[6], fld[7], fld[8])
            else:
                arcpy.AddField_management(fc, fld[0], fld[1], fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8])
            print("Done creating field [{0}] in [{1}]".format(fld[0], fc))        

## Add domain constraints to appropriate fields
domain_fields_dict = {}
for index, row in df_domains.iterrows():
    domain_fields_dict[row['Field']] = row['Domain Name']
for fc in arcpy.ListFeatureClasses():
    fields = arcpy.ListFields(fc)
    for field in fields:
        for k, v in domain_fields_dict.items():
            if field.name == k:
                arcpy.management.AssignDomainToField(fc, field.name, v)
                print("Assigned [{0}] domain to: [{1}.{2}]".format(v, fc, field.name))

# Set parameters for creating related tables
primaryKey = 'FEATUREID'
foreignKey = 'IMLOCIDFEATUREID'

# Name the relationship classes
data_pt_rc = 'ECO_MonitoringLocations_pt_ECO_MonitoringLocationsData_pt'
data_ln_rc = 'ECO_MonitoringLocations_pt_ECO_MonitoringLocationsData_ln'
data_py_rc = 'ECO_MonitoringLocations_pt_ECO_MonitoringLocationsData_py'
logistics_pt_rc = 'ECO_MonitoringLocations_pt_ECO_MonitoringLocationsLogistics_pt'
logistics_ln_rc = 'ECO_MonitoringLocations_pt_ECO_MonitoringLocationsLogistics_ln'
logistics_py_rc = 'ECO_MonitoringLocations_pt_ECO_MonitoringLocationsLogistics_py'

# Create the relationship classes
arcpy.management.CreateRelationshipClass(locations_pt, locations_data_pt, os.path.join(arcpy.env.workspace, data_pt_rc), 'SIMPLE', 'ECO_MonitoringLocationsData_pt', 'ECO_MonitoringLocations_pt', 'NONE', 'ONE_TO_MANY', 'NONE', primaryKey, foreignKey)
print("Done creating relationship class: {0}".format(data_pt_rc))
arcpy.management.CreateRelationshipClass(locations_pt, locations_data_ln, os.path.join(arcpy.env.workspace, data_ln_rc), 'SIMPLE', 'ECO_MonitoringLocationsData_ln', 'ECO_MonitoringLocations_pt', 'NONE', 'ONE_TO_MANY', 'NONE', primaryKey, foreignKey)
print("Done creating relationship class: {0}".format(data_ln_rc))
arcpy.management.CreateRelationshipClass(locations_pt, locations_data_py, os.path.join(arcpy.env.workspace, data_py_rc), 'SIMPLE', 'ECO_MonitoringLocationsData_py', 'ECO_MonitoringLocations_pt', 'NONE', 'ONE_TO_MANY', 'NONE', primaryKey, foreignKey)
print("Done creating relationship class: {0}".format(data_py_rc))
arcpy.management.CreateRelationshipClass(locations_pt, locations_logistics_pt, os.path.join(arcpy.env.workspace, logistics_pt_rc), 'SIMPLE', 'ECO_MonitoringLocationLogistics_pt', 'ECO_MonitoringLocations_pt', 'NONE', 'ONE_TO_MANY', 'NONE', primaryKey, foreignKey)
print("Done creating relationship class: {0}".format(logistics_pt_rc))
arcpy.management.CreateRelationshipClass(locations_pt, locations_logistics_ln, os.path.join(arcpy.env.workspace, logistics_ln_rc), 'SIMPLE', 'ECO_MonitoringLocationLogistics_ln', 'ECO_MonitoringLocations_pt', 'NONE', 'ONE_TO_MANY', 'NONE', primaryKey, foreignKey)
print("Done creating relationship class: {0}".format(logistics_ln_rc))
arcpy.management.CreateRelationshipClass(locations_pt, locations_logistics_py, os.path.join(arcpy.env.workspace, logistics_py_rc), 'SIMPLE', 'ECO_MonitoringLocationLogistics_py', 'ECO_MonitoringLocations_pt', 'NONE', 'ONE_TO_MANY', 'NONE', primaryKey, foreignKey)
print("Done creating relationship class: {0}".format(logistics_py_rc))

# Remove geoprocessing history from metadata
class_list = locations_pt, locations_data_pt, locations_data_ln, locations_data_py, locations_logistics_pt, locations_logistics_ln, locations_logistics_py, data_pt_rc, data_ln_rc, data_py_rc, logistics_pt_rc, logistics_ln_rc, logistics_py_rc
for class_name in class_list:
    class_path = os.path.join(_WORKSPACE, in_gdb, ds, class_name)
    def removeMetaData(class_path):
        # Get the metadata for the dataset
        tgt_item_md = md.Metadata(class_path)
        # Delete all geoprocessing history from the item's metadata
        if not tgt_item_md.isReadOnly:
            tgt_item_md.deleteContent('GPHISTORY')
            tgt_item_md.deleteContent('THUMBNAIL')
            tgt_item_md.save()
    removeMetaData(class_name)
    print("Removed the geoprocessing metadata from: {0}".format(class_name))

print("### !!! ALL DONE !!! ###".format())