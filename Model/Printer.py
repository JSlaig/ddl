from docx import Document
from docx.shared import Cm

from Model import Word
from Model import Paragraph

document = Document()

def write_paragraph(paragraph):
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