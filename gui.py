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
frame_top = Frame(root)
frame_bottom = Frame(root)
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
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height, background="black")
        self.canvas.grid(column=0, row=0, padx=5, pady=5)

        # Creation of the image in the canvas
        self.canvas.create_image(0, 0, image=self.image, anchor='nw', tags='image')

        # This data is used to keep track of an
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Creation of the original points
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

        self.create_tokens(p1, p2, p3, p4, "lightblue")
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
        self.canvas.create_line(p1[0][0], p1[0][1], p2[0][0], p2[0][1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p2[0][0], p2[0][1], p3[0][0], p3[0][1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p3[0][0], p3[0][1], p4[0][0], p4[0][1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p4[0][0], p4[0][1], p1[0][0], p1[0][1], fill="lightblue", width=2, tags="line")
        self.canvas.tag_lower("line")
        self.canvas.tag_lower("image")

    def erase_lines(self):
        self.canvas.delete("line")

    def get_tokens(self):

        tokens = self.canvas.find_withtag("token")

        t1 = self.canvas.coords(tokens[0])
        t2 = self.canvas.coords(tokens[1])
        t3 = self.canvas.coords(tokens[2])
        t4 = self.canvas.coords(tokens[3])

        p1 = [[int((t1[0] + t1[2]) / 2), int((t1[1] + t1[3]) / 2)]]
        p2 = [[int((t2[0] + t2[2]) / 2), int((t2[1] + t2[3]) / 2)]]
        p3 = [[int((t3[0] + t3[2]) / 2), int((t3[1] + t3[3]) / 2)]]
        p4 = [[int((t4[0] + t4[2]) / 2), int((t4[1] + t4[3]) / 2)]]

        return p1, p2, p3, p4

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        item = self.canvas.find_closest(event.x, event.y)[0]

        if item != 1:
            self._drag_data["token"] = item
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

        # move the object the appropriate amount taking into account the boundaries of the image
        if event.x < 0 or event.x > self.width:
            delta_x = 0

        if event.y < 0 or event.y > self.height:
            delta_y = 0

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
    windowWidth = int(3 * main_monitor.width / 4)
    global windowHeight
    windowHeight = int(3 * main_monitor.height / 4)

    root.geometry(str(windowWidth) + "x" + str(windowHeight))

    # Frame in which top buttons and menus will appear
    frame_top.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)
    frame_top.config(bg="lightblue")
    frame_top.config(width=windowWidth - 10, height=50)

    # Buttons
    btn_load = Button(frame_top, text="load", width=25, command=load_image)
    btn_load.grid(column=0, row=0, padx=5, pady=5)

    btn_camera = Button(frame_top, text="capture", width=25, command=camera)
    btn_camera.grid(column=1, row=0, padx=5, pady=5)

    # Frame in which images will be displayed and cleared
    frame_bottom.grid(column=0, row=1, padx=5, pady=5, sticky=W + E + N + S)
    frame_bottom.config(bg="darkgray")
    frame_bottom.config(width=windowWidth - 10, height=windowHeight - 50)

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
        point1, point2, point3, point4 = dps.detect_document_vertices(image)

        print(point1)

        point1[0][0] = point1[0][0] / width_ratio
        point1[0][1] = point1[0][1] / height_ratio

        point2[0][0] = point2[0][0] / width_ratio
        point2[0][1] = point2[0][1] / height_ratio

        point3[0][0] = point3[0][0] / width_ratio
        point3[0][1] = point3[0][1] / height_ratio

        point4[0][0] = point4[0][0] / width_ratio
        point4[0][1] = point4[0][1] / height_ratio

        for child in frame_bottom.winfo_children():
            child.destroy()

        shape_cropper = ShapeCropper(frame_bottom, img_width, img_height, point1, point2, point3, point4, img)
        shape_cropper.grid(column=0, row=0, padx=5, pady=5)

        btn_next = Button(frame_bottom, text="next", width=25, command=lambda: get_coordinates(shape_cropper))
        btn_next.grid(column=0, row=1, padx=5, pady=5)

        return point1, point2, point3, point4, img


def get_coordinates(shape_cropper):
    # Get cropped coordinates
    values = shape_cropper.get_tokens()

    # TODO: The next button needs to call the rest of the methods
    #   that are used to process the image and warp it, since we already have the shapeCropper as a
    #   param, should be able to nullify it, but not sure on how to remove it from the actual GUI

    for child in frame_bottom.winfo_children():
        child.destroy()

    print("values: ")
    print(values)
