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
    """ Takes the path of a folder and deletes the files within it """
    try:
        for filename in os.listdir(folder_path):
            fullpath_filename = os.path.join(folder_path, filename)
            if os.path.isfile(fullpath_filename):
                os.remove(fullpath_filename)
    except:
        pass

def add_map_suffix(map_folder_path):
    """
    Adds '01' to the end of all PDF files in the given map folder 
    '01' orders map before the directions sheets
    """
    for filename in os.listdir(map_folder_path):
        # Skip if already has '01'
        if filename.endswith('01.pdf'):
            pass
        else:
            if filename.endswith('.pdf'):
                src = os.path.join(map_folder_path, filename)
                root_ext = os.path.splitext(filename)
                root = root_ext[0]
                new_filename = root + ' 01' + '.pdf'
                dst = os.path.join(map_folder_path, new_filename)
                os.rename(src, dst)

def create_pdf_list(pdf_folder_path, pdf_list_name):
    """
    Creates a list of PDFs
    Requires (1) the folder containg the pdfs and (2) what you want to call the output list
    """
    for filename in os.listdir(pdf_folder_path):
        # only PDFs are added to the list
        if filename.endswith('.pdf'):
            pdf_list_name.append(os.path.join(pdf_folder_path, filename))
    # Sorts list ABC
    pdf_list_name.sort(key = str.lower)

def merge_pdfs(pdf_list, name):
    """
    Takes a list of PDFs and merges them into one PDF
    Requires (1) a list of PDFs (2) what you want to name the output PDF
    """
    pdfMerge = PyPDF2.PdfFileMerger()
    for filename in pdf_list:
        pdfFile = open(filename, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        pdfMerge.append(pdfReader)
    pdfFile.close()
    pdfMerge.write(os.path.join(__ROOT_DIR, 'Packets', name))

def copy_paste_files(source_folder, destination_folder):
    """
    Copies all PDFs from one folder to another
    """
    for filename in os.listdir(source_folder):
        source = os.path.join(source_folder, filename)
        destination = os.path.join(destination_folder, filename)
        # only PDFs are copied
        if filename.endswith('.pdf'):
            shutil.copy(source, destination)

def pdf_port_to_land(portrait_folder, new_folder):
    # takes a folder of PDFs with portrait orientation
    # function rotates all PDFs to landscape orientation
    # Exports to a new folder
    for filename in os.listdir(portrait_folder):
        input_fullpath_filename = os.path.join(portrait_folder, filename)
        output_fullpath_filename = os.path.join(new_folder, filename)
        pdf_in = open(input_fullpath_filename, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf_in)
        pdf_writer = PyPDF2.PdfFileWriter()
        numofpages = pdf_reader.numPages
        numrotated = 0 
        for pagenum in range(numofpages):
            page = pdf_reader.getPage(pagenum)
            mb = page.mediaBox
            if (mb.upperRight[1] > mb.upperRight[0]) and (page.get('/Rotate') is None):
                page.rotateCounterClockwise(90)
                numrotated = numrotated + 1
            pdf_writer.addPage(page)
        pdf_out = open(output_fullpath_filename, 'wb')
        pdf_writer.write(pdf_out)
        pdf_out.close()
        pdf_in.close()

# Set the folder path to the Legend pdf
folder_legend = os.path.join(__ROOT_DIR, 'Legend')
# Create a list to populate with the Legend pdf
pdfiles_legend = []
create_pdf_list(folder_legend, pdfiles_legend)

# Create a list with the four panel folders to loop over
panel_list = 'Panel_1', 'Panel_2', 'Panel_3', 'Panel_4'

for panel in panel_list:
    print("Creating packet for {0}...".format(panel))
    # Set the folder path to the Cover page pdf
    folder_cover = os.path.join(__ROOT_DIR, panel, 'Cover')
    # Create a list to populate with the Cover page pdf
    pdfiles_cover = []
    create_pdf_list(folder_cover, pdfiles_cover)
    # Set the folder path to the Overview map pdf
    folder_overview = os.path.join(__ROOT_DIR, panel, 'Overview')
    # Create a list to populate with the Overview map pdf
    pdfiles_overview = []
    create_pdf_list(folder_overview, pdfiles_overview)
    # Clear old files from the Maps folder
    folder_maps = os.path.join(__ROOT_DIR, panel, 'Maps')
    Clear_Folder(folder_maps)
    # copy landscape map pdfs to Maps folder
    folder_maps_land = os.path.join(__ROOT_DIR, panel, 'Maps', 'Landscape')
    copy_paste_files(folder_maps_land, folder_maps)
    # rotate portrait pdf maps to landscape and copy to Maps folder
    folder_maps_port = os.path.join(__ROOT_DIR, panel, 'Maps', 'Portrait')
    pdf_port_to_land(folder_maps_port, folder_maps)
    # add '01' suffix to pdfs in the Maps folder
    add_map_suffix(folder_maps)
    # Set the folder path to the Maps/Directions folder
    folder_maps_directions = os.path.join(__ROOT_DIR, panel, 'Maps_Directions_Combined')
    # Clear old files from the Maps/Directions folder
    Clear_Folder(folder_maps_directions)  
    # Copy map pdfs to the Maps/Directions folder
    copy_paste_files(folder_maps, folder_maps_directions)
    # Set the folder path to the Directions pdfs
    folder_directions = os.path.join(__ROOT_DIR, panel, 'Directions')
    # Copy directions pdfs to the Maps/Directions folder
    copy_paste_files(folder_directions, folder_maps_directions)
    # Create a list to populate with the Maps and Directions
    pdfiles_maps_directions = []
    create_pdf_list(folder_maps_directions, pdfiles_maps_directions)
    # Sort ABC
    pdfiles_maps_directions.sort(key = str.lower)
    # Create a giant list with everything to include in the merged PDF
    pdfiles_packet = pdfiles_cover + pdfiles_overview + pdfiles_maps_directions + pdfiles_legend
    filename = 'Packet_' + panel + '.pdf'
    merge_pdfs(pdfiles_packet, filename)
    print("{0} was created".format(filename))

                        
