# config.py
import os
from PyPDF2 import PdfReader

parentDirectory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
pickleDirectory = os.path.join(parentDirectory, 'Pickles')
pictureDirectory = os.path.join(parentDirectory, 'Pics')
iconDirectory = os.path.join(pictureDirectory, 'icons')
wallpaperDirectory = os.path.join(pictureDirectory, 'wallpapers')


def get_pdf_content(file_path):
    pdf_reader = PdfReader(file_path)

    # Initialize an empty string to hold the PDF text
    pdf_text = ""

    # Loop through each page in the PDF and add its text to the string
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    return pdf_text

initialPrompt = get_pdf_content(os.path.join(os.getcwd(), "trainingData", "initialPrompt.pdf"))
selfAwareness = get_pdf_content(os.path.join(os.getcwd(), "trainingData", "selfAwareness.pdf"))
commandPrompt = get_pdf_content(os.path.join(os.getcwd(), "trainingData", "commandPrompt.pdf"))
