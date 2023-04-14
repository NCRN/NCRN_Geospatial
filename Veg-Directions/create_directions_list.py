#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial working script for creating directions to veg monitoring locations.
--------------------------------------------------------------------------------
TODO: Add more of a complete description.

References:
# https://betterprogramming.pub/automate-filling-templates-with-python-1ff6c6fd595e
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
import openpyxl
from openpyxl import load_workbook
import docx
from docx import Document
import docxtpl
from docxtpl import DocxTemplate
import os

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool

template_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\Directions_Template.docx' ## Create a variable to store the full path to the Word doc template. Set prefix to the user portion of the root directory
workbook_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_Veg_Locations_Directions_Master.xlsx' ## Create a variable to store the full path to the Excel file. Set prefix to the user portion of the root directory

workbook = load_workbook(workbook_path)
template = DocxTemplate(template_path)
worksheet_areas = workbook["Dictionary_Areas"]
worksheet_plots = workbook["Dictionary_Plots"]

# dict1 = {Area_Name:[Area_Directions, Area_Warnings]} 
for index, row in worksheet_areas.items():



## dict2 = {Area_Name:[Plot_Name, Plot_Directions, Plot_Warnings, Keys, Map_N]}
for index, row in worksheet_plots.items():


# Populate the template fresh, every time the Area Name changes
if k = a: 


#OPEN THE TEMPLATE > SAVE AS > MAKE A NEW FILE 

#FILL IT OUT WITH HEADER INFO FROM dict1 

#FILL OUT THE DIRECTIONS TABLE WITH ITEMS IN b, ADDING ROWS AS NEEDED FOR EACH b 

	#for a, b in dict2.items(): 

# This is an empty dictionary with the keys matching the first column of the excel file. For now, you assign empty values (None) and these will be filled in using the excel file in the next step.
to_fill_in = {'Area_Name' : None,
              'Area_Directions' : None,
              'Area_Warnings': None,
              'Plot_Name' : None,
              'Plot Directions': None,
              'Warnings' : None,
              'Keys' : None,
              'Map_N' : None
              }

# Set the minimum number of columns. This will be 2.
column = 2

# Perform the following code block if the colomn amount is less than the maximum column amount.
while column <= worksheet_areas.max_column:

    # Define the column index. This is a letter so you need to convert the column number to a letter (2+64) = B
    col_index = chr(column+64)
    row_index = 1
    # Retrieve the values from excel document and store in dictionary you defined earlier on
    # For each key in the dictionary, we look up the value in the excel file and store it instead of "none" in the dictionary
    for key in to_fill_in:
        cell = '%s%i' % (col_index, row_index)
        to_fill_in[key] = worksheet_areas[cell].value
        row_index += 1

## Fill in all the keys defined in the word document using the dictionary.
#   # The keys in the word document are identified by the {{}}symbols.
#   template.render(to_fill_in)
   
#   # Output the file to a docx document.
#   filename = str(to_fill_in['Company_Name']) + '_draft.docx'
#   filled_path = os.path.join(main_path, filename)
#   template.save(filled_path)
#   print("Done with %s" % str(to_fill_in['Company_Name']))
#   column += 1

