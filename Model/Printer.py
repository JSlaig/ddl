import docx

import tkinter as tk
from tkinter import filedialog

from Model import Word
from Model import Paragraph


def write_document(paragraphs):
    document = docx.Document()

    for paragraph in paragraphs:
        write_paragraph(document, paragraph)

    save_document(document)


def write_paragraph(document, paragraph):
    p = document.add_paragraph()

    words = paragraph.get_words()

    font = paragraph.get_font()

    style = document.styles['Normal']
    style.font.name = paragraph.get_font()

    for word in words:
        if word.get_weight() == 'normal':
            p.add_run(word.get_text())
        elif word.get_weight() == 'bold':
            p.add_run(word.get_text()).bold = True
        elif word.get_weight() == 'italic':
            p.add_run(word.get_text()).italic = True
        elif word.get_weight() == 'underlined':
            p.add_run(word.get_text()).underlined = True
        else:
            print(f'there was an error writing the word {word.get_id()}:  {word.get_text()}')


def save_dialog(document):
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    file_path = filedialog.asksaveasfilename(defaultextension='.docx')

    if file_path:
        save_document(document, file_path)
    else:
        print("Save operation cancelled.")


def save_document(document, file_path):
    document.save(file_path)
