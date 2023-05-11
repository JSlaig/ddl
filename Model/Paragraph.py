import cv2
import pytesseract as pytesseract
from Model import Word as wd


class Paragraph:

    def __init__(self, id=0, image=None, text=None, size=None, font=None, justification=None):
        self.preview = None
        self.id = id

        self.image = image

        self.text = text

        self.words = []  # From class word

        self.size = size

        self.font = font

        self.justification = justification

        self.detect_words()
        self.ocr_image()

        words = self.text.split(" ")
        for i, word in enumerate(words):
            self.words[i].set_text(word)


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

    def detect_words(self):
        sheet_copy = self.image.copy()

        sheet_gray = cv2.cvtColor(sheet_copy, cv2.COLOR_BGR2GRAY)

        sheet_blur = cv2.GaussianBlur(sheet_gray, (7, 7), 0)

        # We invert the binary filter in order for the lettering in the sheet to be white and expandable
        sheet_otsu = cv2.threshold(sheet_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Create rectangular structuring element and dilate
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(7), int(5)))
        sheet_dilated = cv2.dilate(sheet_otsu, kernel, iterations=4)

        imagaux, contours = self.get_word_coords(sheet_dilated, sheet_copy)

        self.preview = imagaux

        word_list = []

        for id, p in enumerate(contours):
            x, y, w, h = cv2.boundingRect(p)
            cropped_word = self.image[y:y + h, x:x + w]

            word_list.append(wd.Word(id, cropped_word))

        #self.words = list(reversed(word_list))
        self.words = word_list

    @staticmethod
    def get_word_coords(dilated_sheet, default):
        image = default.copy()

        # Find contours and draw rectangle
        contours = cv2.findContours(dilated_sheet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (1, 156, 255), 2)

        return image, contours

    def write(self):
        print("Function aimed to call the .docx and use the params to write the text")

    def showimage(self):
        cv2.imshow(f"paragraph {self.id}", self.image)
        cv2.imshow(f"paragraph {self.id}", self.preview)

        for word in self.words:
            print(word.get_text())

    # Won't be used since OCR will work word by word
    def ocr_image(self):
        if self.image is not None:
            self.text = pytesseract.image_to_string(self.image)
