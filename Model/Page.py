import Paragraph

# TODO: Implement into the code once the image and paragraphs are detected independently
#   -Subject to change

class Page:

    def __init__(self, paragraphs=[], images=[]):

        self.images = images  # From class images

        self.paragraphs = paragraphs  # From class paragraph

    def get_images(self):
        return self.images

    def get_paragraphs(self):
        return self.paragraphs

    def set_images(self, images):
        self.images = images

    def set_paragraphs(self, paragraphs):
        self.paragraphs = paragraphs
