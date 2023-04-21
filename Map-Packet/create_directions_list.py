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

# Create a docx template for the word document downloaded earlier.
template = DocxTemplate(template_path)

# Create dataframes for Areas and Plots using __XCEL_LIBRARY
df_areas = pd.read_excel(__XCEL_LIBRARY, sheet_name='Areas Python')
df_plots = pd.read_excel(__XCEL_LIBRARY, sheet_name='Plots', na_filter = False)

# Loop over rows in the Areas dataframe to create the directions documents
for index, row in df_areas.iterrows():
    # Display '0' cells as blank
    Area_Name = row['Area Name']
    if row['Area Warnings'] == 0:
        Area_Warnings = ""
    else: 
        Area_Warnings = row['Area Warnings']
    # This is a dictionary with the first 3 keys matching columns in the Area dataframe. This will fill out the Area portion of the template.
    to_fill_in_area = {
        'Area_Name': Area_Name,
        'Area_Directions': row['Area Directions'],
        'Area_Warnings': Area_Warnings,
        # The next keys refill the Plots input parameters (they are erased by the first render function)
        'Plot_Name': '{{Plot_Name}}',
        'Plot_Directions': '{{Plot_Directions}}',
        'Warnings': '{{Warnings}}',
        'Keys': '{{Keys}}',
        'Map_N': '{{Map_N}}'
        }
    # Use the render function to fill in the word template based on the dictionary created.
    template.render(to_fill_in_area)
    filename = str(to_fill_in_area['Area_Name']) + ' Directions.docx'
    filled_path = os.path.join(__ROOT_DIR, row['Panel'], 'Directions', filename)
    # save the created template on the specified path
    template.save(filled_path)
    print("Created %s" % str(to_fill_in_area['Area_Name']))
    # Loop over rows in the Plots dataframe to populate the directions documents
    for index, row in df_plots.iterrows():
        # Set the template to the document just created
        filled_template = DocxTemplate(filled_path)
        # Only populate document if the plot matches the area
        if row['Area/Route - Panel'] == Area_Name:
            # This is a dictionary with the keys matching columns in the Plots dataframe
            to_fill_in_plot = {
                'Plot_Name': row['Plot Name'],
                'Plot_Directions': row['Plot Directions'],
                'Warnings': row['Plot Warnings'],
                'Keys': row['Keys'],
                'Map_N': row['Map #']
                }
            filled_template.render(to_fill_in_plot)
            # Create a new row in the Plots table to be filled out in the next itteration
            table = filled_template.tables[0]
            row = table.add_row().cells
            row[0].text = '{{Plot_Name}}'
            row[1].text = '{{Plot_Directions}}'
            row[2].text = '{{Warnings}}'
            row[3].text = '{{Keys}}'
            row[4].text = '{{Map_N}}'
            filled_template.save(filled_path)
        #Delete input parameters that were left empty
        to_fill_in = {}
    filled_template.render(to_fill_in)
    filled_template.save(filled_path)
    print("Populated %s" % str(to_fill_in_area['Area_Name']))

panel_list = 'Panel_1', 'Panel_2', 'Panel_3', 'Panel_4'
#Loop over the panel folders to convert docx to pdf
for panel in panel_list:
    folder_path = os.path.join(__ROOT_DIR, panel, 'Directions')
    for filename in os.listdir(folder_path):
        # Full path of the docx
        in_file = os.path.join(folder_path, filename)
        # Name of the output pdf
        out_filename = filename.replace('.docx', '.pdf')
        # Full path of the output pdf
        out_file = os.path.join(folder_path, out_filename)
        # Create an empty PDF
        canvas = Canvas(out_file)
        # Populate the pdf with the specified docx
        covx_to_pdf(in_file, out_file)
        print("Success: {0} was converted to PDF".format(filename))
