
class Paragraph:

    def __init__(self, image=None, text=None, words=[], size=None, font=None, justification=None):
        self.image = image

        self.text = text

        self.words = words  # From class word

        self.size = size

        self.font = font

        self.justification = justification

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

