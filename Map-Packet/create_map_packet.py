#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Abstract: Initial working script to create map packets for vegetation monitoring

Description:
1) The script will create directions sheets for NCRN Vegetation Monitoring.
An excel spreadsheet will define the parameters for populating a Word template.
Each output docx contains monitoring locations with the same "Map" and "Area" for each panel (1-4)
Finally, the script will convert the Word docx to PDFs so that they can be included in the map packet.
2) The script will create the Directions/Maps packet for NCRN vegetation monitoring.
The script will find the materials that make up the map packet in their respective folders and combine them
Current packet materials: Cover Page, Area Directions, Overview Map, Park Maps, Map Legend, Appendix

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
from sqlite3 import paramstyle
import PyPDF2
from PyPDF2 import PdfFileReader, utils
from io import StringIO
import subprocess
import os
import shutil
from cmath import nan
from logging import exception
from tkinter.tix import ROW
from openpyxl import load_workbook
#import aspose.words as aw
#import aspose.pydrawing as drawing
import docx
from docx import Document
from docx.shared import Pt
from docx.enum.section import WD_ORIENT
from docx.enum.dml import MSO_THEME_COLOR_INDEX
from docxtpl import DocxTemplate
from docx.shared import RGBColor
import pandas as pd
import sys
from reportlab.pdfgen.canvas import Canvas
import comtypes.client
import time
import fitz
from os import path

print("### GETTING STARTED ###".format())

"""
Set various global variables. Some of these could be parameterized to be used in an 
ArcGIS Toolbox script and/or command line use. 
"""

# Currently hardcoded values that may be parameterized if bundling into a tool
__ROOT_DIR = r'C:\Users\goettel\DOI\NPS-NCRN-Forest Veg - Documents\General\Field_Maps_2023' ## Set the directory path to the root directory that will be the destination for outputs. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT
__XCEL_LIBRARY = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\NCRN_Veg_Locations_Directions_Master.xlsx' ## Create a variable to store the full path to the Excel file. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT
directions_template_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\Templates\NCRN\Veg_Map_Packet\Directions_Template.docx' ## Create a variable to store the full path to the Directions template. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT
appendix_template_path = r'C:\Users\goettel\DOI\NCRN Data Management - Geospatial\Templates\NCRN\Veg_Map_Packet\Appendix_Template.docx' ## Create a variable to store the full path to the Appendix template. NEED TO UPDATE PREFIX TO YOUR ONEDRIVE ACCOUNT

# Create some functions to be used in various places
def Clear_Folder(folder_path):
    """Takes the path of a folder or geodatabase and deletes the files within it"""
    for filename in os.listdir(folder_path):
        fullpath_filename = os.path.join(folder_path, filename)
        if os.path.isfile(fullpath_filename):
            try:
                os.remove(fullpath_filename)
            except:
                print("ERROR CLEARING FOLDERS! Word may be running in the background and using the files. RESTART COMPUTER AND TRY AGAIN...")

def create_blank_docx(panel_folder, Map_List):
    """
    Use to create a blank Word .docx
    e.g. panel_folder = 'Panel_1' (The panel folder the maps are located in. All maps must be in the same panel folder.)
    e.g. Map_List = 'Map_Name1', 'Map_Name3', 'Map_Name5' (The maps that a blank document will be placed behind)
    """
    for Map in Map_List:
        document = Document()
        # Change orientation of the output document to landscape
        sections = document.sections
        section = sections[0]
        new_width, new_height = section.page_height, section.page_width
        section.page_width = new_width
        section.page_height = new_height
        section.orientation = WD_ORIENT.LANDSCAPE
        # '03' orders blank page after the directions sheets
        filename = Map + " 03 " + "blank page.docx"
        fullpath_filename = os.path.join(__ROOT_DIR, panel_folder, 'Directions', filename)
        document.save(fullpath_filename)

def covx_to_pdf(in_file, out_file):
    """
    Convert a Word .docx to PDF
    Requires the name of the input Word .docx and the name of the output PDF
    """
    wdFormatPDF = 17
    word = comtypes.client.CreateObject('Word.Application')
    # Keep the program hidden while running in the background
    word.Visible = False
    doc = word.Documents.Open(in_file)
    # add a 7 second delay so that the program doesn't crash
    time.sleep(7)
    doc.SaveAs(out_file, FileFormat = wdFormatPDF)
    doc.Close()
    word.Quit()

def pdf_delete_page(panel_folder, filename, page_to_delete):
    ''' 
    Deletes a single page from a PDF
    e.g. page_to_delete = 1
    The page associated with the number is deleted in the specified PDF. indexing starts from 1 so if we pass 1 as an argument the second page will be deleted.
    '''
    folder_path = os.path.join(__ROOT_DIR, panel_folder, 'Directions')
    input_file = os.path.join(folder_path, filename)
    root_ext = os.path.splitext(filename)
    root = root_ext[0]
    new_filename = root + " update" + '.pdf'
    output_file = os.path.join(folder_path, new_filename)
    # try/except will skip if the page has already been deleted
    try:
        file_handle = fitz.open(input_file)
        file_handle.delete_page(page_to_delete)
        file_handle.save(output_file)
        file_handle.close()
        os.remove(input_file)
    except:
        pass


def add_hyperlink(paragraph, url, text, color):

    # This gets access to the document.xml.rels file and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )

    # Create a w:r element
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')

    # Join all the xml elements together add add the required text to the w:r element
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)

    # Create a new Run object and add the hyperlink into it
    r = paragraph.add_run ()
    r._r.append (hyperlink)

    # A workaround for the lack of a hyperlink style (doesn't go purple after using the link)
    # Delete this if using a template that has the hyperlink style in it
    r.font.color.theme_color = MSO_THEME_COLOR_INDEX.HYPERLINK
    r.font.underline = True

    return hyperlink

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


def reset_eof_of_pdf_return_stream(txt, pdf_stream_in:list):
    # find the line position of the EOF
    for i, x in enumerate(txt[::-1]):
        if b'%%EOF' in x:
            actual_line = len(pdf_stream_in)-i
            print(f'EOF found at line position {-i} = actual {actual_line}, with value {x}')
            break

    # return the list up to that point
    return pdf_stream_in[:actual_line]


def fix_pdf_EOF_marker(fullpath_filename):
    EOF_MARKER = b'%%EOF'

    with open(fullpath_filename, 'rb') as f:
        contents = f.read()

    # check if EOF is somewhere else in the file
    if EOF_MARKER in contents:
        # we can remove the early %%EOF and put it at the end of the file
        contents = contents.replace(EOF_MARKER, b'')
        contents = contents + EOF_MARKER
    else:
        # Some files really don't have an EOF marker
        # In this case it helped to manually review the end of the file
        print(contents[-8:]) # see last characters at the end of the file
        # printed b'\n%%EO%E'
        contents = contents[:-6] + EOF_MARKER

    with open(fullpath_filename.replace('.pdf', '') + '_fixed.pdf', 'wb') as f:
        f.write(contents)

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

# Create a list with the four panel folders to loop over
panel_list = 'Panel_1', 'Panel_2', 'Panel_3', 'Panel_4'

# Create dataframes for Areas and Plots using the imported spreadsheet
df_areas = pd.read_excel(__XCEL_LIBRARY, sheet_name='Areas Python')
df_plots = pd.read_excel(__XCEL_LIBRARY, sheet_name='Plots', na_filter = False)

## Remove all old files from the directions folder
#for panel in panel_list:
#    Clear_Folder(os.path.join(__ROOT_DIR, panel, 'Directions'))

## Set the Directions docx as the template
#area_template = DocxTemplate(directions_template_path)

# Create empty list to populate with plots
plots_populated_list = []

## Loop over rows in the Areas dataframe to create directions Word docx
#print("Creating Directions docx...")
#for index, row in df_areas.iterrows():
#    Area = row["Area"]
#    Panel = row["Panel"]
#    Map = row["Map"]
#    # Display '0' cells as blank
#    if row["Area Warnings"] == 0:
#        Area_Warnings = ""
#    else: 
#        Area_Warnings = row["Area Warnings"]
#    # This is a dictionary with the first 3 keys matching columns in the Area dataframe. This will fill out the Area portion of the template.
#    to_fill_in_area = {
#        'Map': Map,
#        'Area': Area,
#        'Area_Directions': row["Area Directions"],
#        'Area_Warnings': Area_Warnings,
#        # The next keys refill the Plots input parameters (they are erased by the first render function)
#        'Plot': '{{Plot_Name}}',
#        'Plot_Directions': '{{Plot_Directions}}',
#        'Warnings': '{{Warnings}}',
#        'Keys': '{{Keys}}'
#        }
#    # Use the render function to fill in the word template based on the dictionary created.
#    area_template.render(to_fill_in_area)
#    # '02' orders directions sheets after the map
#    filename = Map + " 02 " + Area + '.docx'
#    filled_path = os.path.join(__ROOT_DIR, row['Panel_Folder'], 'Directions', filename)
#    # save the created template on the filled path
#    try:
#        area_template.save(filled_path)
#        # Loop over rows in the Plots dataframe to populate the docx
#        for index, row in df_plots.iterrows():
#            # Change the template to the docx just created
#            filled_template = DocxTemplate(filled_path)
#            # Only populate docx if the area, panel, and map matches
#            if (row['Area'] == Area) & (row['Panel'] == Panel) & (row['Map'] == Map):
#                # This is a dictionary with the keys matching columns in the Plots dataframe
#                to_fill_in_plot = {
#                    'Plot_Name': row["Plot Name"],
#                    'Plot_Directions': row["Plot Directions"],
#                    'Warnings': row["Plot Warnings"],
#                    'Keys': row["Keys"]
#                    }
#                plots_populated_list.append(row['Plot Name'])
#                filled_template.render(to_fill_in_plot)
#                # Create a new row in the Plots table to be filled out in the next itteration
#                table = filled_template.tables[0]
#                row = table.add_row().cells
#                row[0].text = "{{Plot_Name}}"
#                row[1].text = "{{Plot_Directions}}"
#                row[2].text = "{{Warnings}}"
#                row[3].text = "{{Keys}}"
#                # Add red font to plot warnings
#                warnings_paragraph = row[2].paragraphs[0]
#                warnings_run = warnings_paragraph.runs
#                warnings_font = warnings_run[0].font
#                warnings_font.color.rgb = RGBColor.from_string('FF0000')                
#                filled_template.save(filled_path)
#            # Delete input parameters that were left empty
#            to_fill_in_empty = {}
#        filled_template.render(to_fill_in_empty)
#        filled_template.save(filled_path)
#    except:
#        print("ERROR CREATING '{0}' in {1}".format(filename, panel))
    
# Identify plots that weren't added to a directions sheet
plots_expected_df = df_plots['Plot Name']
plots_expected_list = plots_expected_df.values.tolist()

set_difference = set(plots_expected_list) - set(plots_populated_list)
list_difference_result = list(set_difference)
#print("Plots not added to Directions: ", list_difference_result)

## Create blank docx to go behind map
## Need to run for maps that have an even number of directions sheets (2, 4, etc.)
## Panel 1
#Blank_Pages_1 = "CHOH 4 (Point of Rocks)", "CHOH 5 and HAFE", "GWMP (Mt Vernon) and NACE South (FOWA, PISC)", "MONO", "NACE (ANAC, FODU)"
#create_blank_docx('Panel_1', Blank_Pages_1)

## Panel 2
#Blank_Pages_2 = "CATO", "CHOH 2 and GWMP (GRFA)", "CHOH 5 and HAFE", "CHOH 9 (Far West - Paw Paw Tunnel)", "GWMP (Daingerfield) and NACE (Shepherd Parkway)", "MONO", "NACE (FODU, SUIT)"
#create_blank_docx('Panel_2', Blank_Pages_2)

## Panel 3
#Blank_Pages_3 = "CHOH 1, 2 and GWMP (GRFA, Turkey Run)", "CHOH 10 (Far West - Oldtown, Spring Gap)", "CHOH 5 and HAFE", "GWMP (Mt Vernon) and NACE South (PISC)", "MONO", "NACE (BAWA, GREE)", "PRWI"
#create_blank_docx('Panel_3', Blank_Pages_3)

## Panel 4
#Blank_Pages_4 = "ANTI and CHOH 6 (Snyders Landing)", "CHOH 2 and GWMP (Turkey Run)", "CHOH 3 (Violettes Lock) and GWMP (GRFA)", "CHOH 5 and HAFE"
#create_blank_docx('Panel_4', Blank_Pages_4)

## Loop over the panel folders to convert Directions docx to pdf
#for panel in panel_list:
#    print("Converting {0} Directions docx to pdf...".format(panel))
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
#            # Populate the pdf with the docx
#            try:
#                covx_to_pdf(in_file, out_file)
#            except:
#                print("ERROR CONVERTING {0} TO PDF".format(in_file))

## Remove empty pages at the end of PDFs
#pdf_delete_page('Panel_1', "PRWI 02 PRWI.pdf", 1)
#pdf_delete_page('Panel_4', "CATO 02 CATO.pdf", 1)

# Create the Appendix

## Remove all old files from the appendix folder
#for panel in panel_list:
#    Clear_Folder(os.path.join(__ROOT_DIR, panel, 'Appendix'))

# Create empty list to populate with plots
plots_populated_appendix_list = []
  
# Loop over rows in the Plots dataframe to create Appendix Word docx
print("Creating Appendix docx...")


#for panel in panel_list:
#    filled_path = os.path.join(__ROOT_DIR, panel, 'Appendix', 'Appendix.docx')
#    shutil.copyfile(appendix_template_path, filled_path)
#    # Set the Appendix docx as the template
#    #try:
#    for index, row in df_plots.iterrows():
#        Panel_Folder = row["Panel Folder"]
#        if Panel_Folder == panel:
#            # This is a dictionary with the keys matching columns in the Plots dataframe. This will fill out the table in the Appendix template.
#            plots_populated_appendix_list.append(row['Plot Name'])      
#            # Add hyperlink to first cell
#            # Create a new row in the Plots table to be filled out in the next itteration
#            appendix_template = DocxTemplate(filled_path)            
#            to_fill_in = {
#                'Plot_Name': row["Plot Name"],
#                'Parking_Lat_Long': row["Parking Lat, Long"],
#                'Plot_Lat_Long': row["Plot Lat, Long"],
#                'Map_Number': row["Map #"]
#                }
#            # Use the render function to fill in the word template based on the dictionary created.
#            appendix_template.render(to_fill_in)            
#            table = appendix_template.tables[0]

#            row_cells = table.add_row().cells

#            p_table = row_cells[0].paragraphs[0]
            
#            hyperlink = add_hyperlink(p_table, row["Parking Location (Google)"], row["Plot Name"], '#0000FF')
           
#            row_cells[1].text = "{{Parking_Lat_Long}}"
#            row_cells[2].text = "{{Plot_Lat_Long}}"
#            row_cells[3].text = "{{Map_Number}}"

#            ## save the created template on the filled path
#            appendix_template.save(filled_path)
#            to_fill_in = {
#                'Parking_Lat_Long': row["Parking Lat, Long"],
#                'Plot_Lat_Long': row["Plot Lat, Long"],
#                'Map_Number': row["Map #"]
#                }

#            # use the render function to fill in the word template based on the dictionary created.
#            appendix_template.render(to_fill_in)
#    appendix_template.save(filled_path)
#    #except:
#    #    print("ERROR CREATING Appendix in {0}".format(Panel_Folder))


set_difference_2 = set(plots_expected_list) - set(plots_populated_appendix_list)
list_difference_result_2 = list(set_difference_2)
print("Plots not added to Appendix: ", list_difference_result_2)


# Loop over the panel folders to convert Appendix docx to pdf
for panel in panel_list:
    print("Converting {0} Appendix docx to pdf...".format(panel))
    folder_path = os.path.join(__ROOT_DIR, panel, 'Appendix')
    for filename in os.listdir(folder_path):
        if filename.endswith('.docx'):
            # Full path of the docx
            in_file = os.path.join(folder_path, filename)
            # Name of the output pdf
            out_filename = filename.replace('.docx', '.pdf')
            # Full path of the output pdf
            out_file = os.path.join(folder_path, out_filename)
            # Create an empty PDF
            canvas = Canvas(out_file)
            # Populate the pdf with the docx
            #try:
            covx_to_pdf(in_file, out_file)
            #except:
            #print("ERROR CONVERTING {0} TO PDF".format(in_file))

#    # rotate portrait pdf maps to landscape and copy to Maps folder
for panel in panel_list:
    folder_path = os.path.join(__ROOT_DIR, panel, 'Appendix')
    for filename in os.listdir(folder_path):
            folder_path_land = os.path.join(folder_path, 'Landscape')
            pdf_port_to_land(folder_path, folder_path_land)

## Set the folder path to the Legend pdf
#folder_legend = os.path.join(__ROOT_DIR, 'Legend')
## Create a list to populate with the Legend pdf
#pdfiles_legend = []
#create_pdf_list(folder_legend, pdfiles_legend)

#for panel in panel_list:
#    print("Creating packet for {0}...".format(panel))
#    # Set the folder path to the Cover page pdf
#    folder_cover = os.path.join(__ROOT_DIR, panel, 'Cover')
#    # Create a list to populate with the Cover page pdf
#    pdfiles_cover = []
#    create_pdf_list(folder_cover, pdfiles_cover)
#    # Set the folder path to the Overview map pdf
#    folder_overview = os.path.join(__ROOT_DIR, panel, 'Overview')
#    # Create a list to populate with the Overview map pdf
#    pdfiles_overview = []
#    create_pdf_list(folder_overview, pdfiles_overview)
#    # Clear old files from the Maps folder
#    folder_maps = os.path.join(__ROOT_DIR, panel, 'Maps')
#    Clear_Folder(folder_maps)
#    # copy landscape map pdfs to Maps folder
#    folder_maps_land = os.path.join(__ROOT_DIR, panel, 'Maps', 'Landscape')
#    copy_paste_files(folder_maps_land, folder_maps)
#    # rotate portrait pdf maps to landscape and copy to Maps folder
#    folder_maps_port = os.path.join(__ROOT_DIR, panel, 'Maps', 'Portrait')
#    pdf_port_to_land(folder_maps_port, folder_maps)
#    # add '01' suffix to pdfs in the Maps folder
#    add_map_suffix(folder_maps)
#    # Set the folder path to the Maps/Directions folder
#    folder_maps_directions = os.path.join(__ROOT_DIR, panel, 'Maps_Directions_Combined')
#    # Clear old files from the Maps/Directions folder
#    Clear_Folder(folder_maps_directions)  
#    # Copy map pdfs to the Maps/Directions folder
#    copy_paste_files(folder_maps, folder_maps_directions)
#    # Set the folder path to the Directions pdfs
#    folder_directions = os.path.join(__ROOT_DIR, panel, 'Directions')
#    # Copy directions pdfs to the Maps/Directions folder
#    copy_paste_files(folder_directions, folder_maps_directions)
#    # Create a list to populate with the Maps and Directions
#    pdfiles_maps_directions = []
#    create_pdf_list(folder_maps_directions, pdfiles_maps_directions)
#    # Sort ABC
#    pdfiles_maps_directions.sort(key = str.lower)
#    # Create a giant list with everything to include in the merged PDF
#    pdfiles_packet = pdfiles_cover + pdfiles_overview + pdfiles_maps_directions + pdfiles_legend
#    filename = 'Packet_' + panel + '.pdf'
#    merge_pdfs(pdfiles_packet, filename)
#    print("{0} was created".format(filename))

                        
