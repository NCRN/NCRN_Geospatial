#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Abstract: Initial working script for creating directions to veg monitoring locations.

Description:
The purpose of this script is to create directions sheets for NCRN Vegetation Monitoring.
An excel spreadsheet will define the parameters for populating a Word template.
Each output documents contains monitoring locations that have the same "Area" or "Route" for each panel (1-4)
Finally, the script will convert the Word documents to PDFs so that they can be included in the map packet.

TODO: Additional Refactoring
--------------------------------------------------------------------------------
References:
# https://betterprogramming.pub/automate-filling-templates-with-python-1ff6c6fd595e

#__author__ = "NCRN GIS Unit"
#__copyright__ = "None"
#__credits__ = [""]
#__license__ = "GPL"
#__version__ = "1.0.2"
#__maintainer__ = "David Jones"
#__email__ = "david_jones@nps.gov"
#__status__ = "Staging"
"""

# Import statements for utilized libraries / packages
from cmath import nan
from tkinter.tix import ROW
import openpyxl
from openpyxl import load_workbook
import docx
from docx import Document
import docxtpl
from docxtpl import DocxTemplate
import os
import pandas as pd
import sys
from reportlab.pdfgen.canvas import Canvas
import comtypes.client
import time
import fitz

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool
__ROOT_DIR = r'C:\Users\goettel\DOI\NPS-NCRN-Forest Veg - Documents\General\Field_Maps_2023' ## Set the directory path to the root directory that will be the destination for outputs. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT
template_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\Templates\NCRN\Directions_Template.docx' ## Create a variable to store the full path to the Word doc template. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT
__XCEL_LIBRARY = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_Veg_Locations_Directions_Master.xlsx' ## Create a variable to store the full path to the Excel file. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT

# Create some functions to be used in various places
def Clear_Folder(folder_path):
    """
    Takes the path of a folder or geodatabase and deletes the files within it
    """
    for filename in os.listdir(folder_path):
        fullpath_filename = os.path.join(folder_path, filename)
        if os.path.isfile(fullpath_filename):
            try:
                os.remove(fullpath_filename)
            except:
                pass

def create_blank_docx(panel, Map):
    document = Document()
    filename = 'blank page' + '03' + Map
    file_path = os.path.join(__ROOT_DIR, panel, 'Directions', filename)
    document.save(file_path)

def covx_to_pdf(in_file, out_file):
    """Convert a Word .docx to PDF"""
    wdFormatPDF = 17
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(in_file)
    time.sleep(7)
    doc.SaveAs(out_file, FileFormat = wdFormatPDF)
    doc.Close()
    word.Quit()

# DOES NOT WORK
def remove_empty_pdf_page(panel_folder, filename, page):
    input_file = os.path.join(__ROOT_DIR, panel_folder, 'Directions', filename)
    print(input_file)
    output_file = input_file
    print(output_file)
    file_handle = fitz.open(input_file)
    file_handle.delete_page(page)
    file_handle.save(output_file)
    print('worked')

## Create a docx template for the word document downloaded earlier.
#template = DocxTemplate(template_path)

## Create dataframes for Areas and Plots using __XCEL_LIBRARY
#df_areas = pd.read_excel(__XCEL_LIBRARY, sheet_name='Areas Python')
#df_plots = pd.read_excel(__XCEL_LIBRARY, sheet_name='Plots', na_filter = False)

#panel_list = 'Panel_1', 'Panel_2', 'Panel_3', 'Panel_4'

## Clear directions folder
#for panel in panel_list:
#    Clear_Folder(os.path.join(__ROOT_DIR, panel, 'Directions'))

## Loop over rows in the Areas dataframe to create the directions documents
#plots_list = []
#for index, row in df_areas.iterrows():
#    if row['Panel_Folder'] == 'Panel_1':
#        # Display '0' cells as blank
#        Area = row['Area']
#        Panel = row['Panel']
#        Map = row['Map']
#        if row['Area Warnings'] == 0:
#            Area_Warnings = ""
#        else: 
#            Area_Warnings = row['Area Warnings']
#        # This is a dictionary with the first 3 keys matching columns in the Area dataframe. This will fill out the Area portion of the template.
#        to_fill_in_area = {
#            'Map': Map,
#            'Area': Area,
#            'Area_Directions': row['Area Directions'],
#            'Area_Warnings': Area_Warnings,
#            # The next keys refill the Plots input parameters (they are erased by the first render function)
#            'Plot': '{{Plot_Name}}',
#            'Plot_Directions': '{{Plot_Directions}}',
#            'Warnings': '{{Warnings}}',
#            'Keys': '{{Keys}}',
#            }
#        # Use the render function to fill in the word template based on the dictionary created.
#        template.render(to_fill_in_area)
#        filename = Map + ' 02 ' + row['Area'] + '.docx'
#        #filename = str(to_fill_in_area['Area']) + ' Directions.docx'
#        filled_path = os.path.join(__ROOT_DIR, row['Panel_Folder'], 'Directions', filename)
#        # save the created template on the specified path
#        template.save(filled_path)
#        print("Created %s" % str(to_fill_in_area['Area']))
#        # Loop over rows in the Plots dataframe to populate the directions documents
#        for index, row in df_plots.iterrows():
#            # Set the template to the document just created
#            filled_template = DocxTemplate(filled_path)
#            # Only populate document if the plot matches the area and map
#            if (row['Area'] == Area) & (row['Panel'] == Panel) & (row['Map'] == Map):
#                # This is a dictionary with the keys matching columns in the Plots dataframe
#                to_fill_in_plot = {
#                    'Plot_Name': row['Plot Name'],
#                    'Plot_Directions': row['Plot Directions'],
#                    'Warnings': row['Plot Warnings'],
#                    'Keys': row['Keys'],
#                    'Map_N': row['Map #']
#                    }
#                plots_list.append(row['Plot Name'])
#                filled_template.render(to_fill_in_plot)
#                # Create a new row in the Plots table to be filled out in the next itteration
#                table = filled_template.tables[0]
#                row = table.add_row().cells
#                row[0].text = '{{Plot_Name}}'
#                row[1].text = '{{Plot_Directions}}'
#                row[2].text = '{{Warnings}}'
#                row[3].text = '{{Keys}}'
#                filled_template.save(filled_path)
#            #Delete input parameters that were left empty
#            to_fill_in = {}
#        filled_template.render(to_fill_in)
#        filled_template.save(filled_path)
#        print("Populated %s" % str(to_fill_in_area['Area']))
#len(plots_list)

### Create blank documents as needed
##Map1 = 

##Loop over the panel folders to convert docx to pdf
#for panel in panel_list:
#    folder_path = os.path.join(__ROOT_DIR, panel, 'Directions')
#    for filename in os.listdir(folder_path):
#        if filename.endswith('.docx'):
#            # Full path of the docx
#            in_file = os.path.join(folder_path, filename)
#            # Name of the output pdf
#            out_filename = filename.replace('.docx', '.pdf')
#            # Full path of the output pdf
#            out_file = os.path.join(folder_path, out_filename)
#            # Create an empty PDF
#            canvas = Canvas(out_file)
#            # Populate the pdf with the specified docx
#            covx_to_pdf(in_file, out_file)
#            print("Success: {0} was converted to PDF".format(filename))

# Remove empty pages from pdf
remove_empty_pdf_page('Panel_1', 'PRWI 02 PRWI.pdf', 2)