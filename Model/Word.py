class Word:
    def __init__(self, image=None, text=None, weight=None, color=None):
        self.image = image
        self.text = text
        self.weight = weight
        self.color = color

    def get_image(self):
        return self.image

    def get_word(self):
        return self.text

    def get_weight(self):
        return self.weight

    def get_color(self):
        return self.color

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
