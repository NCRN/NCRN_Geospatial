#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial working script for creating map packet for vegetation monitoring
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
import PyPDF2
import os

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool

def create_directions_list(folder):
    pdfiles = []
    for filename in os.listdir(folder):
        if filename.endswith('.pdf'):
            pdfiles.append(filename)


__ROOT_DIR = r'C:\Users\goettel\DOI\NPS-NCRN-Forest Veg - Documents\General\Field_Maps_2023'

panel_list = 'Panel 1', 'Panel 2', 'Panel 3', 'Panel 4'
for panel in panel_list:


                        
pdfiles.sort(key = str.lower)