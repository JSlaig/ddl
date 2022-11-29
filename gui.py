import tkinter as tk  # python 3
from tkinter import *
from tkinter import filedialog

import cv2
import imutils
import numpy as np
from PIL import Image
from PIL import ImageTk
from screeninfo import get_monitors

import documentPreprocessScanner as dps

# ///////////////////////////////////// ATTRIBUTES OF GUI /////////////////////////////////////
root = Tk()  # Assignation of root window
root.title('DocClone')  # Assignation of the window title
# root.iconbitmap('c:/gui/codemy.ico')  # Setting an icon for the application
image = None
lblImage = Label(root)


# ///////////////////////////////////// CLASSES /////////////////////////////////////
class ShapeCropper(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent, width, height, p1, p2, p3, p4, img):
        tk.Frame.__init__(self, parent)

        # Image we are setting as a background
        self.image = img

        # Init values for width and height of the canvas
        self.width = width
        self.height = height

        # create a canvas
        self.canvas = tk.Canvas(width=self.width, height=self.height, background="black")
        self.canvas.grid(column=0, row=3, padx=5, pady=5)

        # Creation of the image in the canvas
        self.canvas.create_image(0, 0, image=self.image, anchor='nw', state='disabled', tags='image')

        # This data is used to keep track of an
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Creation of the original points
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

        self.create_tokens(p1, p2, p3, p4, "green")
        self.draw_lines(p1, p2, p3, p4)

        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

    def create_tokens(self, p1, p2, p3, p4, color):
        """Create a token at the given coordinate in the given color"""
        self.canvas.create_oval(
            p1[0][0] - 10,
            p1[0][1] - 10,
            p1[0][0] + 10,
            p1[0][1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p2[0][0] - 10,
            p2[0][1] - 10,
            p2[0][0] + 10,
            p2[0][1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p3[0][0] - 10,
            p3[0][1] - 10,
            p3[0][0] + 10,
            p3[0][1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p4[0][0] - 10,
            p4[0][1] - 10,
            p4[0][0] + 10,
            p4[0][1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def draw_lines(self, p1, p2, p3, p4):
        self.canvas.create_line(p1[0][0], p1[0][1], p2[0][0], p2[0][1], fill="green", width=2, tags="line")
        self.canvas.create_line(p2[0][0], p2[0][1], p3[0][0], p3[0][1], fill="green", width=2, tags="line")
        self.canvas.create_line(p3[0][0], p3[0][1], p4[0][0], p4[0][1], fill="green", width=2, tags="line")
        self.canvas.create_line(p4[0][0], p4[0][1], p1[0][0], p1[0][1], fill="green", width=2, tags="line")
        self.canvas.tag_lower("line")
        self.canvas.tag_lower("image")

    def erase_lines(self):
        self.canvas.delete("line")

    def get_tokens(self):
        t1 = self.canvas.coords(self.canvas.find_closest(0, 0)[0])
        t2 = self.canvas.coords(self.canvas.find_closest(self.width, 0)[0])
        t3 = self.canvas.coords(self.canvas.find_closest(self.width, self.height)[0])
        t4 = self.canvas.coords(self.canvas.find_closest(0, self.height)[0])

        p1 = [[int((t1[0] + t1[2]) / 2), int((t1[1] + t1[3]) / 2)]]
        p2 = [[int((t2[0] + t2[2]) / 2), int((t2[1] + t2[3]) / 2)]]
        p3 = [[int((t3[0] + t3[2]) / 2), int((t3[1] + t3[3]) / 2)]]
        p4 = [[int((t4[0] + t4[2]) / 2), int((t4[1] + t4[3]) / 2)]]

        return p1, p2, p3, p4

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        self._drag_data["token"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["token"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount

        self.canvas.move(self._drag_data["token"], delta_x, delta_y)
        self.erase_lines()
        p1, p2, p3, p4 = self.get_tokens()
        self.draw_lines(p1, p2, p3, p4)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


# ///////////////////////////////////// METHODS /////////////////////////////////////
def run_gui() -> object:
    # Setting the window size based on the monitor resolution
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    global windowWidth
    windowWidth = int(main_monitor.width / 2)
    global windowHeight
    windowHeight = int(main_monitor.height / 2)

    root.geometry(str(windowWidth) + "x" + str(windowHeight))

    # Image read button
    btn_load = Button(root, text="load", width=25, command=load_image)
    btn_load.grid(column=0, row=0, padx=5, pady=5)

    # Camera option button
    btn_camera = Button(root, text="capture", width=25, command=camera)
    btn_camera.grid(column=2, row=0, padx=5, pady=5)

    # These two might need to be loaded in a later method once the button is chosen

    # Label where image will appear
    lblImage.grid(column=0, row=2)

    root.mainloop()


# Method for starting preprocess of the image taking as input the webcam (MUST BE REARRANGED AND RE-FACTORIZED ONCE
# LOAD-IMAGE VERSION IS ON A DECENT STAGE)
def camera():
    dps.document_preprocess()


# Method will be re-factorized in order to only load the image from the filesystem and all preprocess will be actually
# moved to document preprocess scanner
def load_image():
    path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                 ("image", ".jpeg"),
                                                 ("image", ".png")])

    if len(path) > 0:
        global image

        # Read image on opencv
        image = cv2.imread(path)

        # Visualization of image in gui
        show_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Need to change the color scheme for proper visuals
        show_image_small = imutils.resize(show_image, height=600)
        im = Image.fromarray(show_image_small)
        img = ImageTk.PhotoImage(image=im)

        # Resize canvas to fit exact same size as the picture
        img_width = img.width()
        img_height = img.height()

        # Calculate the new coordinates for the points since the original image has been resized
        original_im = Image.fromarray(show_image)
        original_image = ImageTk.PhotoImage(image=original_im)

        original_width = original_image.width()
        original_height = original_image.height()

        width_ratio = original_width / img_width
        height_ratio = original_height / img_height

        print(width_ratio)
        print(height_ratio)

        # Get the original vertices
        point1, point2, point3, point4 = detect_document_vertices(image)

        point1[0][0] = point1[0][0] / width_ratio
        point1[0][1] = point1[0][1] / height_ratio

        point2[0][0] = point2[0][0] / width_ratio
        point2[0][1] = point2[0][1] / height_ratio

        point3[0][0] = point3[0][0] / width_ratio
        point3[0][1] = point3[0][1] / height_ratio

        point4[0][0] = point4[0][0] / width_ratio
        point4[0][1] = point4[0][1] / height_ratio

        # Canvas to show the picture
        ShapeCropper(root, img_width, img_height, point1, point2, point3, point4, img).grid(column=0, row=3, padx=5,
                                                                                            pady=5)

        # We'll do an initialization of how the first image autodetected looks and later on we will refresh the widget
        # in order to update the position of the points that are the vertices of the document sheet

        # final_image is made for mere display purposes, since the actual image used for processing later on will be the
        # original(high_res) and the coordinates scaled up to match the resolution of the original image
        # final_image = dps.draw_image_contour(point1, point2, point3, point4, image)

        return point1, point2, point3, point4, img


# Parameter: Raw-Image
# Return_Value: Estimated vertices of the document contained in the image
# Observations: Originally it already returned the modified image with the contour, but since I want to enable contours
#               to be edited after the initial estimation, the function will only return the vertices coordinates.
def detect_document_vertices(image_source):
    image_aux = image_source

    # Copy of the original image
    original_image = image_aux.copy()

    # Firstly, we turn the image into grayScale
    image_aux = dps.get_image_grayscale(image_aux)

    # Secondly, we run edge detector through the image
    image_aux = dps.get_image_edge_detector(image_aux)

    # Thirdly, we have to find the contours present in the picture
    image_aux, contours = dps.get_image_contours(image_aux, original_image)

    # Fourth step is to find the actual biggest contour and draw it on the image
    biggest = dps.get_image_biggest_contour(contours)

    # We get the coordinates for the vertices of the shape

    if biggest.size != 0:
        point1 = biggest[0]
        point2 = biggest[1]
        point3 = biggest[2]
        point4 = biggest[3]
    else:
        height, width = image_aux.shape[:2]

        # Set up the 4 points of the image based on the resolution of the picture, with an aspect ratio of 1:1.4
        point1 = np.array([width / 4, height / 4])
        point2 = np.array([3 * width / 4, height / 4])
        point3 = np.array([width / 4, int(3 * height / 4)])
        point4 = np.array([3 * width / 4, int(3 * height / 4)])

    return point1, point2, point3, point4
