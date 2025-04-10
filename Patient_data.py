from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import re

# Set the path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# image = Image.open("text.png")
# image_text = pytesseract.image_to_string(image)
def clean_ocr_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)  
    text = re.sub(r'[=~_•""'']', '', text)     
    text = re.sub(r'[\[\]\{\}\|\\]', '', text)
    text = re.sub(r'[-–—]{2,}', '-', text)
    text = '. '.join(i.strip().capitalize() for i in text.split('.'))
    return text.strip()

# image_text = clean_ocr_text(image_text)
# print(image_text)