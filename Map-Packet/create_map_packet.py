#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Abstract: Initial working script to create map packets for vegetation monitoring

Description:
The purpose of this script is to create the Directions/Maps packet for NCRN vegetation monitoring.
The script will find the materials that make up the map packet in their respective folders and combine them
Current packet materials: Cover Page, Area Directions, Overview Map, Park Maps, and Map Legend

TODO: Additional Refactoring
--------------------------------------------------------------------------------
References:
# https://python-bloggers.com/2022/04/merging-pdfs-with-python-2/

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
import PyPDF2
import os
import shutil


print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""
# Currently hardcoded values that may be parameterized if bundling into a tool
__ROOT_DIR = r'C:\Users\goettel\DOI\NPS-NCRN-Forest Veg - Documents\General\Field_Maps_2023' ## Set the directory path to the root directory that will be the destination for outputs. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT

def Clear_Folder(folder_path):
    """
    Takes the path of a folder or geodatabase and deletes the files within it
    """
    try:
        for filename in os.listdir(folder_path):
            fullpath_filename = os.path.join(folder_path, filename)
            if os.path.isfile(fullpath_filename):
                os.remove(fullpath_filename)
    except:
        pass

def add_map_suffix(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('01.pdf'):
            pass
        else:
            src = os.path.join(folder_path, filename)
            root_ext = os.path.splitext(filename)
            root = root_ext[0]
            new_filename = root + ' 01' + '.pdf'
            dst = os.path.join(folder_path, new_filename)
            os.rename(src, dst)

def create_pdf_list(folder_path, list_name):
    """
    Creates a list of PDFs
    Takes (1) the folder path to the PDFs that will be added to the list (2) what you want to name the list 
    """
    for filename in os.listdir(folder_path):
        # Makes sure only PDFs are added to the list
        if filename.endswith('.pdf'):
            list_name.append(os.path.join(folder_path, filename))
    # Sorts the list alphabetically
    list_name.sort(key = str.lower)

def merge_pdfs(pdfiles, name):
    """
    Merges PDFs into one document
    Takes (1) a list of PDFs (2) what you want to name the document
    """
    pdfMerge = PyPDF2.PdfFileMerger()
    for filename in pdfiles:
            pdfFile = open(filename, 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFile)
            pdfMerge.append(pdfReader)
    pdfFile.close()
    pdfMerge.write(os.path.join(__ROOT_DIR, 'Packets', name))

def copy_paste_files(source_folder, destination_folder):
    for filename in os.listdir(source_folder):
        if filename.endswith('.pdf'):
            # construct full file path
            source = os.path.join(source_folder, filename)
            destination = os.path.join(destination_folder, filename)
            # copy only files
            if os.path.isfile(source):
                shutil.copy(source, destination)
                print('copied', filename)

panel_list = 'Panel_1', 'Panel_2', 'Panel_3', 'Panel_4'

for panel in panel_list:
    folder_path = os.path.join(__ROOT_DIR, panel, 'Maps')
    add_map_suffix(folder_path)

# Clear maps/directions folder
for panel in panel_list:
    Clear_Folder(os.path.join(__ROOT_DIR, panel, 'Maps_Directions_Combined'))

# Set the folder path to the Legend pdf
folder_legend = os.path.join(__ROOT_DIR, 'Legend')
# Create a list to populate with the Legend pdf
pdfiles_legend = []
create_pdf_list(folder_legend, pdfiles_legend)


# Eventually refactor so that it is a loop
#for panel in panel_list = 

# Create the Panel 1 packet
# Set the folder path to the Cover page pdf
folder_cover_panel1 = os.path.join(__ROOT_DIR, 'Panel_1', 'Cover')
# Create a list to populate with the Cover page pdf
pdfiles_cover_panel1 = []
create_pdf_list(folder_cover_panel1, pdfiles_cover_panel1)

# Set the folder path to the Overview map pdf
folder_overview_panel1 = os.path.join(__ROOT_DIR, 'Panel_1', 'Overview')
# Create a list to populate with the Overview map pdf
pdfiles_overvew_panel1 = []
create_pdf_list(folder_overview_panel1, pdfiles_overvew_panel1)

folder_maps_panel1 = os.path.join(__ROOT_DIR, 'Panel_1', 'Maps')
folder_directions_panel1 = os.path.join(__ROOT_DIR, 'Panel_1', 'Directions')
folder_maps_directions_panel1 = os.path.join(__ROOT_DIR, 'Panel_1', 'Maps_Directions_Combined')

copy_paste_files(folder_maps_panel1, folder_maps_directions_panel1)
copy_paste_files(folder_directions_panel1, folder_maps_directions_panel1)

# Create a list to populate with the Maps and Directions
pdfiles_maps_directions_panel1 = []
create_pdf_list(folder_maps_directions_panel1, pdfiles_maps_directions_panel1)
# Sort ABC
pdfiles_maps_directions_panel1.sort(key = str.lower)

# Create a giant list with everything you want to include in the merged PDF
pdfiles_panel1 = pdfiles_cover_panel1 + pdfiles_overvew_panel1 + pdfiles_maps_directions_panel1 + pdfiles_legend
packet1 = 'Packet_Panel_1.pdf'
merge_pdfs(pdfiles_panel1, packet1)
print("{0} was created".format(packet1))

                        
