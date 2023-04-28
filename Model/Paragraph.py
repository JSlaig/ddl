import cv2
import pytesseract as pytesseract


class Paragraph:

    def __init__(self, id=0, image=None, text=None, words=[], size=None, font=None, justification=None):
        self.id = id

        self.image = image

        self.text = text

        self.words = words  # From class word

        self.size = size

        self.font = font

        self.justification = justification

    def get_id(self):
        return self.id

    def get_image(self):
        return self.image

    def get_text(self):
        return self.text

    def get_words(self):
        return self.words

    def get_size(self):
        return self.size

    def get_font(self):
        return self.font

    def get_justification(self):
        return self.justification

    def set_id(self, id):
        self.id = id

    def set_image(self, image):
        self.image = image

    def set_text(self, text):
        self.text = text

    def set_words(self, words):
        self.words = words

    def set_size(self, size):
        self.size = size

    def set_font(self, font):
        self.font = font

    def set_justification(self, justification):
        self.justification = justification

    def write(self):
        print("Function aimed to call the .docx and use the params to write the text")

    def showimage(self):
        cv2.imshow(f"paragraph {self.id}", self.image)

    def ocr_image(self):
        if self.image is not None:
            self.text = pytesseract.image_to_string(self.image)

            return self.text

        return ""
