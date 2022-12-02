import arcpy
import os
import sys

print('### GETTING STARTED ###'.format())

# Currently hardcoded values that may be parameterized if bundling into a tool
workspace = r'C:\Users\goettel\DOI\NCRN Data Management - GIS\NCRN_GIS_Data_Standard' ## Update this to be the directory where the geodatabase should be created

in_gdb = r'NCRN_GIS_Standard.gdb' ## Change the name of the geodatabase as needed

ds = r'IMD' ## Currently putting IMD feature classes inside a feature dataset

in_srs = r'NAD_1983_UTM_Zone_18N.prj' ## Update this based on the spatial reference system standard for the network
# Create a spatial reference object
sr = arcpy.SpatialReference(os.path.join(workspace, in_srs))

# Create a new File Geodatabase
arcpy.CreateFileGDB_management(workspace, in_gdb)
print('Finished creating: {0}'.format(in_gdb))

# Create the IMD feature dataset
arcpy.CreateFeatureDataset_management(os.path.join(workspace,in_gdb), ds, sr)
print('Finished creating feature dataset: {0}'.format(ds))

# Set workspace
arcpy.env.workspace = os.path.join(workspace, in_gdb)

# Create a list of all the domains to be created
# Needs updating if new domains are added to the data model, or if domains are removed, or if domains are renamed, etc.
domains_list = ['DOM_DATAACCESS_NPS2016',
                'DOM_ISEXTANT_NPS2016',
                'DOM_LINETYPE_NPS2016',
                'DOM_POINTTYPE_NPS2016',
                'DOM_POLYGONTYPE_NPS2016',
                'DOM_PUBLICDISPLAY_NPS2016',
                'DOM_REGIONCODE_NPS2016',
                'DOM_XYACCURACY_NPS2016',
                'DOM_YES_NO_UNK_NPS2016',
                'DOM_LOCATIONTYPE_IMD2022',
                'DOM_HABITATTYPE_IMD2022',
                'DOM_INDICATORCAT_IMD2022']

# Loop over all the domains in the list and create them
for domain in domains_list:
    arcpy.management.CreateDomain(arcpy.env.workspace, domain, '', 'TEXT', 'CODED', 'DEFAULT', 'DEFAULT')
    print('Created domain: {0}'.format(domain))
    
# Create a list of lists for all the domain values to be created
domain_values_list = [[arcpy.env.workspace, 'DOM_DATAACCESS_NPS2016', 'Unrestricted', 'Unrestricted'],
                        [arcpy.env.workspace, 'DOM_DATAACCESS_NPS2016', 'Internal NPS Only', 'Internal NPS Only'],
                        [arcpy.env.workspace, 'DOM_DATAACCESS_NPS2016', 'Secure Access Only', 'Secure Access Only'],
                        [arcpy.env.workspace, 'DOM_ISEXTANT_NPS2016', 'Unknown', 'Unknown'],
                        [arcpy.env.workspace, 'DOM_ISEXTANT_NPS2016', 'TRUE', 'TRUE'],
                        [arcpy.env.workspace, 'DOM_ISEXTANT_NPS2016', 'FALSE', 'FALSE'],
                        [arcpy.env.workspace, 'DOM_ISEXTANT_NPS2016', 'Partial', 'Partial'],
                        [arcpy.env.workspace, 'DOM_ISEXTANT_NPS2016', 'Other', 'Other'],
                        [arcpy.env.workspace, 'DOM_LINETYPE_NPS2016', 'Arbitrary line', 'Arbitrary line'],
                        [arcpy.env.workspace, 'DOM_LINETYPE_NPS2016', 'Center line', 'Center line'],
                        [arcpy.env.workspace, 'DOM_LINETYPE_NPS2016', 'Derived line', 'Derived line'],
                        [arcpy.env.workspace, 'DOM_LINETYPE_NPS2016', 'Edge line', 'Edge line'],
                        [arcpy.env.workspace, 'DOM_LINETYPE_NPS2016', 'Perimeter line', 'Perimeter line'],
                        [arcpy.env.workspace, 'DOM_LINETYPE_NPS2016', 'Other line', 'Other line'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Arbitrary point', 'Arbitrary point'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Center point', 'Center point'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Corner point', 'Corner point'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Derived point', 'Derived point'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Entrance point', 'Entrance point'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Vicinity point', 'Vicinity point'],
                        [arcpy.env.workspace, 'DOM_POINTTYPE_NPS2016', 'Other point', 'Other point'],
                        [arcpy.env.workspace, 'DOM_POLYGONTYPE_NPS2016', 'Buffer polygon', 'Buffer polygon'],
                        [arcpy.env.workspace, 'DOM_POLYGONTYPE_NPS2016', 'Circumscribed polygon', 'Circumscribed polygon'],
                        [arcpy.env.workspace, 'DOM_POLYGONTYPE_NPS2016', 'Derived polygon', 'Derived polygon'],
                        [arcpy.env.workspace, 'DOM_POLYGONTYPE_NPS2016', 'Perimeter polygon', 'Perimeter polygon'],
                        [arcpy.env.workspace, 'DOM_POLYGONTYPE_NPS2016', 'Other polygon', 'Other polygon'],
                        [arcpy.env.workspace, 'DOM_PUBLICDISPLAY_NPS2016', 'No Public Map Display', 'No Public Map Display'],
                        [arcpy.env.workspace, 'DOM_PUBLICDISPLAY_NPS2016', 'Public Map Display', 'Public Map Display'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'AKR', 'Alaska Region'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'IMR', 'Intermountain Region'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'MWR', 'Midwest Region'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'NCR', 'National Capital Region'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'NER', 'Northeast Region'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'PWR', 'Pacific-West Region'],
                        [arcpy.env.workspace, 'DOM_REGIONCODE_NPS2016', 'SER', 'Southeast Region'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', 'Unknown', 'Unknown'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', '<5cm', '<5cm'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', '>=5cm and <50cm', '>=5cm and <50cm'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', '>=50cm and <1m', '>=50cm and <1m'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', '>=1m and <5m', '>=1m and <5m'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', '>=5m and <14m', '>=5m and <14m'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', '>=14m', '>=14m'],
                        [arcpy.env.workspace, 'DOM_XYACCURACY_NPS2016', 'Scaled', 'Scaled'],
                        [arcpy.env.workspace, 'DOM_YES_NO_UNK_NPS2016', 'Unknown', 'Unknown'],
                        [arcpy.env.workspace, 'DOM_YES_NO_UNK_NPS2016', 'Yes', 'Yes'],
                        [arcpy.env.workspace, 'DOM_YES_NO_UNK_NPS2016', 'No', 'No'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Monitoring Plot', 'Monitoring Plot'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Tree', 'Tree'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Parking Location', 'Parking Location'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Warning Location', 'Warning Location'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Walking Route', 'Walking Route'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Invasive Plant Area', 'Invasive Plant Area'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Sensitive Species Area', 'Sensitive Species Area'],
                        [arcpy.env.workspace, 'DOM_LOCATIONTYPE_IMD2022', 'Other', 'Other'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Forest', 'Forest'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Grassland', 'Grassland'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'River/Stream', 'River/Stream'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Marsh River', 'Marsh River'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Marsh Creek', 'Marsh Creek'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Marsh Interior', 'Marsh Interior'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Lentic', 'Lentic'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Lotic', 'Lotic'],
                        [arcpy.env.workspace, 'DOM_HABITATTYPE_IMD2022', 'Other', 'Other'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Weather and climate', 'Weather and climate'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Water chemistry', 'Water chemistry'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Land cover and use', 'Land cover and use'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Invasive/exotic plants', 'Invasive/exotic plants'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Birds', 'Birds'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Surface water dynamics', 'Surface water dynamics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Ozone', 'Ozone'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Wet and dry deposition', 'Wet and dry deposition'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Visibility and particulate matter', 'Visibility and particulate matter'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Fire and fuel dynamics', 'Fire and fuel dynamics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Vegetation complexes', 'Vegetation complexes'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Mammals', 'Mammals'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Forest/woodland communities', 'Forest/woodland communities'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Soil function and dynamics', 'Soil function and dynamics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Stream/river channel characteristics', 'Stream/river channel characteristics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Aquatic macroinvertebrates', 'Aquatic macroinvertebrates'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Threatened and endangered species and communities', 'Threatened and endangered species and communities'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Air contaminants', 'Air contaminants'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Groundwater dynamics', 'Groundwater dynamics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Amphibians and reptiles', 'Amphibians and reptiles'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Grassland/herb communities', 'Grassland/herb communities'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Fishes', 'Fishes'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Insect pests', 'Insect pests'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Riparian communities', 'Riparian communities'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Nutrient dynamics', 'Nutrient dynamics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Primary production', 'Primary production'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Wetland communities', 'Wetland communities'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Microorganisms', 'Microorganisms'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Water toxics', 'Water toxics'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Invasive/exotic animals', 'Invasive/exotic animals'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Coastal/oceanographic features and processes', 'Coastal/oceanographic features and processes'],
                        [arcpy.env.workspace, 'DOM_INDICATORCAT_IMD2022', 'Other', 'Other']]

# Added domain values to domains
for value in domain_values_list:
    arcpy.AddCodedValueToDomain_management(value[0], value[1], value[2], value[3])
    print('Added [{0}] domain value to [{1}] domain.'.format(value[2], value[0]))

# Set workspace
arcpy.env.workspace = os.path.join(workspace, in_gdb, ds)

# Create a dictionary of feature class names to be created as keys and geometry types as values
# Need to update if adding new feature classes to the data model, renaming feature classes, etc.
create_fcs_dict = {1:['ECO_MonitoringLocations_pt','POINT'], 
                   2:['ECO_MonitoringLocationsData_pt','POINT'], 
                   3:['ECO_MonitoringLocationsData_ln','POLYLINE'], 
                   4:['ECO_MonitoringLocationsData_py','POLYGON'],
                   5:['ECO_MonitoringLocationLogistics_pt', 'POINT'],
                   6:['ECO_MonitoringLocationLogistics_ln', 'POLYLINE'],
                   7:['ECO_MonitoringLocationLogistics_py', 'POLYGON']}

# Create all the feature classes
for k, v in create_fcs_dict.items():
    arcpy.CreateFeatureclass_management(arcpy.env.workspace, v[0], v[1], '', "DISABLED", "DISABLED", sr)
    print('Done creating feature class: [{0}]'.format(v[0]))

monloc_fields_list = [
                        ['IMLOCID','TEXT','','',25,'IMLOCID','NULLABLE','NON_REQUIRED',''],
                        ['INDICATORCAT','TEXT','','',50,'INDICATORCAT','NULLABLE','NON_REQUIRED',''],
                        ['PROTOCOL','TEXT','','',50,'PROTOCOL','NULLABLE','NON_REQUIRED',''],
                        ['REGIONCODE','TEXT','','',4,'REGIONCODE','NULLABLE','NON_REQUIRED',''],
                        ['GROUPCODE','TEXT','','',10,'GROUPCODE','NULLABLE','NON_REQUIRED',''],
                        ['UNITCODE','TEXT','','',10,'UNITCODE','NULLABLE','NON_REQUIRED',''],
                        ['GROUPNAME','TEXT','','',254,'GROUPNAME','NULLABLE','NON_REQUIRED',''],
                        ['UNITNAME','TEXT','','',254,'UNITNAME','NULLABLE','NON_REQUIRED',''],
                        ['UNITTYPE','TEXT','','',254,'UNITTYPE','NULLABLE','NON_REQUIRED',''],
                        ['SITENAME','TEXT','','',254,'SITENAME','NULLABLE','NON_REQUIRED',''],
                        ['HABITATTYPE','TEXT','','',25,'HABITATTYPE','NULLABLE','NON_REQUIRED',''],
                        ['LOCATIONTYPE','TEXT','','',50,'LOCATIONTYPE','NULLABLE','NON_REQUIRED',''],
                        ['X','DOUBLE','','','','X','NULLABLE','NON_REQUIRED',''],
                        ['Y','DOUBLE','','','','Y','NULLABLE','NON_REQUIRED',''],
                        ['GRTSORDER','SHORT','','','','GRTSORDER','NULLABLE','NON_REQUIRED',''],
                        ['ELEVATION','DOUBLE','','','','ELEVATION','NULLABLE','NON_REQUIRED',''],
                        ['OBSERVABLE','TEXT','','',20,'OBSERVABLE','NULLABLE','NON_REQUIRED',''],
                        ['ISEXTANT','TEXT','','',20,'ISEXTANT','NULLABLE','NON_REQUIRED',''],
                        ['EVENTFREQUENCY','SHORT','','','','EVENTFREQUENCY','NULLABLE','NON_REQUIRED',''],
                        ['PANEL','SHORT','','','','PANEL','NULLABLE','NON_REQUIRED',''],
                        ['EVENTCOUNT','SHORT','','','','EVENTCOUNT','NULLABLE','NON_REQUIRED',''],
                        ['EVENTEARLIEST','DATE','','','','EVENTEARLIEST','NULLABLE','NON_REQUIRED',''],
                        ['EVENTLATEST','DATE','','','','EVENTLATEST','NULLABLE','NON_REQUIRED',''],
                        ['NOTES','TEXT','','',254,'NOTES','NULLABLE','NON_REQUIRED',''],
                        ['MAPLABEL','TEXT','','','','MAPLABEL','NULLABLE','NON_REQUIRED',''],
                        ['PUBLICDISPLAY','TEXT','','',50,'PUBLICDISPLAY','NULLABLE','NON_REQUIRED',''],
                        ['DATAACCESS','TEXT','','',50,'DATAACCESS','NULLABLE','NON_REQUIRED',''],
                        ['ACCESSNOTES','TEXT','','',254,'ACCESSNOTES','NULLABLE','NON_REQUIRED',''],
                        ['ORIGINATOR','TEXT','','',254,'ORIGINATOR','NULLABLE','NON_REQUIRED',''],
                        ['__TYPE__','TEXT','','',50,'','NULLABLE','NON_REQUIRED',''],
                        ['MAPMETHOD','TEXT','','',254,'MAPMETHOD','NULLABLE','NON_REQUIRED',''],
                        ['MAPSOURCE','TEXT','','',254,'MAPSOURCE','NULLABLE','NON_REQUIRED',''],
                        ['SOURCEDATE','DATE','','','','SOURCEDATE','NULLABLE','NON_REQUIRED',''],
                        ['XYACCURACY','TEXT','','',50,'XYACCURACY','NULLABLE','NON_REQUIRED',''],
                        ['GEOMETRYID','TEXT','','',38,'GEOMETRYID','NULLABLE','NON_REQUIRED',''],
                        ['FEATUREID','TEXT','','',50,'FEATUREID','NULLABLE','NON_REQUIRED',''],
                        ['CREATEDATE','DATE','','','','CREATEDATE','NULLABLE','NON_REQUIRED',''],
                        ['CREATEUSER','TEXT','','',50,'CREATEUSER','NULLABLE','NON_REQUIRED',''],
                        ['EDITDATE','DATE','','','','EDITDATE','NULLABLE','NON_REQUIRED',''],
                        ['EDITUSER','TEXT','','',50,'EDITUSER','NULLABLE','NON_REQUIRED','']
                      ]

monlocdata_fields_list = [
                ['DATAIMLOCID','TEXT','','',25,'DATAIMLOCID','NULLABLE','NON_REQUIRED',''],
                ['IMLOCID','TEXT','','',25,'IMLOCID','NULLABLE','NON_REQUIRED',''],
                ['LOCATIONTYPE','TEXT','','',50,'LOCATIONTYPE','NULLABLE','NON_REQUIRED',''],
                ['X','DOUBLE','','','','X','NULLABLE','NON_REQUIRED',''],
                ['Y','DOUBLE','','','','Y','NULLABLE','NON_REQUIRED',''],
                ['DISTANCE','DOUBLE','','','','DISTANCE','NULLABLE','NON_REQUIRED',''],
                ['AZIMUTH','DOUBLE','','','','AZIMUTH','NULLABLE','NON_REQUIRED',''],
                ['DATANOTES','TEXT','','',254,'DATANOTES','NULLABLE','NON_REQUIRED',''],
                ['MAPLABEL','TEXT','','',100,'MAPLABEL','NULLABLE','NON_REQUIRED',''],
                ['__TYPE__','TEXT','','',50,'','NULLABLE','NON_REQUIRED',''],
                ['CREATEDATE','DATE','','','','CREATEDATE','NULLABLE','NON_REQUIRED',''],
                ['CREATEUSER','TEXT','','',50,'CREATEUSER','NULLABLE','NON_REQUIRED',''],
                ['EDITDATE','DATE','','','','EDITDATE','NULLABLE','NON_REQUIRED',''],
                ['EDITUSER','TEXT','','',50,'EDITUSER','NULLABLE','NON_REQUIRED','']
               ]

# TODO: Populate this list with the fields to be added for ECO_MonitoringLocationsLogistics feature classes
# Use __TYPE__ for the Core Type DOM
monlogdata_fields_list = [
                ['LOGIMLOCID','TEXT','','',25,'LOGIMLOCID','NULLABLE','NON_REQUIRED',''],
                ['IMLOCID','TEXT','','',25,'IMLOCID','NULLABLE','NON_REQUIRED',''],
                ['LOCATIONTYPE','TEXT','','',50,'LOCATIONTYPE','NULLABLE','NON_REQUIRED',''],
                ['X','DOUBLE','','','','X','NULLABLE','NON_REQUIRED',''],
                ['Y','DOUBLE','','','','Y','NULLABLE','NON_REQUIRED',''],
                ['DRIVINGNOTES','TEXT','','',254,'DRIVINGNOTES','NULLABLE','NON_REQUIRED',''],
                ['PARKINGNOTES','TEXT','','',254,'PARKINGNOTES','NULLABLE','NON_REQUIRED',''],
                ['WALKINGNOTES','TEXT','','',254,'WALKINGNOTES','NULLABLE','NON_REQUIRED',''],
                ['WARNINGNOTES','TEXT','','',254,'WARNINGNOTES','NULLABLE','NON_REQUIRED',''],
                ['ALTNOTES','TEXT','','',254,'ALTNOTES','NULLABLE','NON_REQUIRED',''],
                ['ALTNOTESEXT','TEXT','','',254,'ALTNOTESEXT','NULLABLE','NON_REQUIRED',''],
                ['MAPLABEL','TEXT','','',100,'MAPLABEL','NULLABLE','NON_REQUIRED',''],
                ['__TYPE__','TEXT','','',50,'','NULLABLE','NON_REQUIRED',''],
                ['CREATEDATE','DATE','','','','CREATEDATE','NULLABLE','NON_REQUIRED',''],
                ['CREATEUSER','TEXT','','',50,'CREATEUSER','NULLABLE','NON_REQUIRED',''],
                ['EDITDATE','DATE','','','','EDITDATE','NULLABLE','NON_REQUIRED',''],
                ['EDITUSER','TEXT','','',50,'EDITUSER','NULLABLE','NON_REQUIRED','']
               ]

geom_type = ''

# Add the fields to the feature classes
for fc in arcpy.ListFeatureClasses():
    #print('This is the fc: {0}'.format(fc))
    if fc.endswith('_pt'):
        geom_type = 'POINTTYPE'
    elif fc.endswith('_ln'):
        geom_type = 'LINETYPE'
    else:
        geom_type = 'POLYGONTYPE'
    if 'Data_' in fc:
        # This will get the fields added to the locations data datasets
        for fld in monlocdata_fields_list:
            if fld[0] == '__TYPE__':
                arcpy.AddField_management(fc, geom_type, fld[1], fld[2], fld[3], fld[4], geom_type, fld[6], fld[7], fld[8])
            else:
                arcpy.AddField_management(fc, fld[0], fld[1], fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8])
            print('Done creating field [{0}] in [{1}]'.format(fld[0], fc))
    elif 'Logistics' in fc:
        # This will get the fields added to the logistics data datasets
        for fld in monlogdata_fields_list:
            if fld[0] == '__TYPE__':
                arcpy.AddField_management(fc, geom_type, fld[1], fld[2], fld[3], fld[4], geom_type, fld[6], fld[7], fld[8])
            else:
                arcpy.AddField_management(fc, fld[0], fld[1], fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8])
    else:
        # This will get the fields added to the primary point locations dataset
        for fld in monloc_fields_list:
            if fld[0] == '__TYPE__':
                arcpy.AddField_management(fc, geom_type, fld[1], fld[2], fld[3], fld[4], geom_type, fld[6], fld[7], fld[8])
            else:
                arcpy.AddField_management(fc, fld[0], fld[1], fld[2], fld[3], fld[4], fld[5], fld[6], fld[7], fld[8])
            print('Done creating field [{0}] in [{1}]'.format(fld[0], fc))        

# Domain fields
domain_fields_dict = {'DATAACCESS':'DOM_DATAACCESS_NPS2016', 
                      'ISEXTANT':'DOM_ISEXTANT_NPS2016',
                      'LINETYPE':'DOM_LINETYPE_NPS2016',
                      'OBSERVABLE':'DOM_YES_NO_UNK_NPS2016',
                      'POINTTYPE':'DOM_POINTTYPE_NPS2016',
                      'POLYGONTYPE':'DOM_POLYGONTYPE_NPS2016',
                      'PUBLICDISPLAY':'DOM_PUBLICDISPLAY_NPS2016',
                      'REGIONCODE':'DOM_REGIONCODE_NPS2016',
                      'XYACCURACY':'DOM_XYACCURACY_NPS2016',
                      'INDICATORCAT':'DOM_INDICATORCAT_IMD2022',
                      'HABITATTYPE':'DOM_HABITATTYPE_IMD2022',
                      'LOCATIONTYPE':'DOM_LOCATIONTYPE_IMD2022'
}

#Add domain constraints to appropriate fields
#arcpy.management.AssignDomainToField(in_table, field_name, domain_name, {subtype_code})
for fc in arcpy.ListFeatureClasses():
    fields = arcpy.ListFields(fc)
    for field in fields:
        for k, v in domain_fields_dict.items():
            if field.name == k:
                arcpy.management.AssignDomainToField(fc, field.name, v)
                print('Assigned [{0}] domain to: [{1}.{2}]'.format(v, fc, field.name))


#TODO: Create related tables
#arcpy.management.CreateTable(out_path, out_name, {template}, {config_keyword}, {out_alias})
#import arcpy
#arcpy.env.workspace = "C:/data"
#arcpy.CreateTable_management("C:/output", "habitatTemperatures.dbf", "vegtable.dbf")



#TODO: Create relationships between feature classes and tables
#https://pro.arcgis.com/en/pro-app/2.8/tool-reference/data-management/create-relationship-class.htm



print('### !!! ALL DONE !!! ###'.format())
