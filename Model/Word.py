import cv2
from pytesseract import pytesseract


class Word:
    def __init__(self, id=0, image=None, text=None, weight=None, color=None):
        self.id = id
        self.image = image
        self.text = text
        self.weight = weight
        self.color = color

        # self.ocr_image()

    def get_id(self):
        return self.id

    def get_image(self):
        return self.image

    def get_word(self):
        return self.text

    def get_weight(self):
        return self.weight

    def get_color(self):
        return self.color

    def set_id(self, id):
        self.id = id

    def set_image(self, image):
        self.image = image

    def set_word(self, text):
        self.text = text

    def set_weight(self, weight):
        self.weight = weight

    def set_color(self, color):
        self.color = color

    def write(self):
        print("This function will write in the document word per word")

    def ocr_image(self):
        if self.image is not None:
            self.text = pytesseract.image_to_string(self.image)

            return self.text

        return ""
