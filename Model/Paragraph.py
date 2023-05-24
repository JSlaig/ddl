import cv2
import imutils
import pytesseract as pytesseract
from Model import Word as wd


class Paragraph:

    def __init__(self, id=0, image=None, text=None, size=None, font='Calibri', justification=None):
        self.preview = None
        self.id = id

        self.image = image

        self.text = text

        self.words = []  # From class word

        self.size = size

        self.font = font

        self.justification = justification

        self.ocr_image()
        self.detect_words()

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
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(5), int(3)))

        sheet_dilated = cv2.dilate(sheet_otsu, kernel, iterations=4)
        sheet_eroded = cv2.erode(sheet_dilated, kernel, iterations=5)

        #cv2.imshow("dilated", sheet_dilated)
        #cv2.imshow("eroded", sheet_eroded)
        #cv2.waitKey()

        img_aux, contours = self.get_word_coords(sheet_eroded, sheet_copy)

        # Sort contours in read order
        #contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))

        # Calculate the average y-axis value and height for each contour
        contour_data = [(c, cv2.boundingRect(c)[1], cv2.boundingRect(c)[3]) for c in contours]

        # Sort the contours based on average y-axis value (primary key) and height (secondary key)
        contour_data = sorted(contour_data, key=lambda data: (data[1], data[2]))

        # Extract the contours from the sorted data
        contours = [data[0] for data in contour_data]

        words = self.text.split()

        word_list = []

        for id, p in enumerate(contours):
            x, y, w, h = cv2.boundingRect(p)
            cropped_word = self.image[y:y + h, x:x + w]

            # Draw the bounding box rectangle
            cv2.rectangle(img_aux, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Add the contour index label in the bounding box
            label = str(id)
            cv2.putText(img_aux, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            #print(f"\nParagraph {self.id}: {self.text}")
            #print(f"Number of words OCR'd {len(words)}: {words}")
            #print(f"Number of contours detected: {len(contours)}")
            #print(f"Word object id: {id}")
            #print(f"Corresponding word: {words[id]}")
            #print(f"Object word length: {len(word_list)}")

            #if len(contours) > len(words):
            #cv2.imshow("image", img_aux)
            #cv2.imshow(f"{words[id]},{len(contours)},{len(words)},{id}", cropped_word)
            #cv2.waitKey()

            word_list.append(wd.Word(id, cropped_word, words[id]))

            #for id, word in enumerate(word_list):
             #   print(f"paragraph {id}")
              #  print(f"{word.get_text()}")

        self.preview = imutils.resize(img_aux, width=1200)

        # Display the result or perform additional processing
        #cv2.imshow("boundboxxed", self.preview)

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

    def ocr_image(self):
        if self.image is not None:
            self.text = pytesseract.image_to_string(self.image)
