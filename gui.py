import tkinter as tk  # python 3
from tkinter import *
from tkinter import filedialog

import cv2
import imutils
import numpy as np
from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw
from screeninfo import get_monitors

import documentPreprocessScanner as dps

# ///////////////////////////////////// ATTRIBUTES OF GUI /////////////////////////////////////
root = Tk()  # Assignation of root window
root.title('DDL')  # Assignation of the window title
# root.iconbitmap('c:/gui/codemy.ico')  # Setting an icon for the application
frame_top = Frame(root)
frame_bottom = Frame(root)
img_file = None
lblImage = Label(root)


# ///////////////////////////////////// CLASSES /////////////////////////////////////
class ShapeCropper(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent, width, height, points, img):
        tk.Frame.__init__(self, parent)

        # Image we are setting as a background
        self.image = img

        # Init values for width and height of the canvas
        self.width = width
        self.height = height

        # create a canvas
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height, background="black")
        self.canvas.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)

        # Creation of the image in the canvas
        self.canvas.create_image(0, 0, image=self.image, anchor='nw', tags='image')

        # This data is used to keep track of an item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Flag for checking if mag glass can appear or not
        self.visible = False

        # Creation of the original points

        # TODO: Change the way these points work once they arent double listed
        self.p1 = points[0][0]
        self.p2 = points[1][0]
        self.p3 = points[2][0]
        self.p4 = points[3][0]

        self.create_tokens(self.p1, self.p2, self.p3, self.p4, "lightblue")
        self.draw_lines(self.p1, self.p2, self.p3, self.p4)

        self.z_img = None
        self.z_cycle = 0
        self.z_img_id = None

        # TODO:
        #   -dynamic size based on resolution

        # Event handling for the token drag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

        # Event handling for the magnifying glass
        root.bind("<ButtonPress-1>", self.zoomer)
        root.bind("<ButtonRelease-1>", self.unzoomer)
        self.canvas.bind("<Motion>", self.crop)

    def create_tokens(self, p1, p2, p3, p4, color):
        """Create a token at the given coordinate in the given color"""
        self.canvas.create_oval(
            p1[0] - 10,
            p1[1] - 10,
            p1[0] + 10,
            p1[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p2[0] - 10,
            p2[1] - 10,
            p2[0] + 10,
            p2[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p3[0] - 10,
            p3[1] - 10,
            p3[0] + 10,
            p3[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )
        self.canvas.create_oval(
            p4[0] - 10,
            p4[1] - 10,
            p4[0] + 10,
            p4[1] + 10,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def draw_lines(self, p1, p2, p3, p4):
        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p2[0], p2[1], p3[0], p3[1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p3[0], p3[1], p4[0], p4[1], fill="lightblue", width=2, tags="line")
        self.canvas.create_line(p4[0], p4[1], p1[0], p1[1], fill="lightblue", width=2, tags="line")
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

        p1 = [int((t1[0] + t1[2]) / 2), int((t1[1] + t1[3]) / 2)]
        p2 = [int((t2[0] + t2[2]) / 2), int((t2[1] + t2[3]) / 2)]
        p3 = [int((t3[0] + t3[2]) / 2), int((t3[1] + t3[3]) / 2)]
        p4 = [int((t4[0] + t4[2]) / 2), int((t4[1] + t4[3]) / 2)]

        return p1, p2, p3, p4

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        item = self.canvas.find_closest(event.x, event.y)[0]

        cords = self.canvas.coords(item)
        cord_x = (cords[0] + cords[2]) / 2
        cord_y = (cords[1] + cords[3]) / 2

        if item != 1:
            self._drag_data["token"] = item
            self._drag_data["x"] = cord_x
            self._drag_data["y"] = cord_y

            # Flag for magnifying glass visibility
            self.visible = True

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["token"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

        # Flag for magnifying glass visibility
        self.visible = False

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

    def zoomer(self, event):
        if self.visible:
            if self.z_cycle != 4:
                self.z_cycle += 1
            self.crop(event)

    def unzoomer(self, event):
        if self.z_cycle != 0:
            self.z_cycle -= 1
        self.crop(event)

    def crop(self, event):
        if self.z_img_id:
            self.canvas.delete(self.z_img_id)
        if self.z_cycle != 0:

            x, y = self._drag_data["x"], self._drag_data["y"]

            if self.z_cycle == 1:
                # convert PhotoImage to PIL Image
                pil_image = ImageTk.getimage(self.image)

                tmp = pil_image.crop((x - (self.width / 10), y - (self.height / 10), x + (self.width / 10), y + (self.height / 10)))

                # Draw circular mask
                mask = Image.new("L", tmp.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + tmp.size, fill=255)

                # Apply the mask to the cropped image
                tmp.putalpha(mask)

                # Paint vudu crosshair
                draw_ch = ImageDraw.Draw(tmp)

                # Center cross
                draw_ch.line((tmp.width / 2, tmp.height * (6 / 14), tmp.width / 2, tmp.height * (8 / 14)), fill="red")
                draw_ch.line((tmp.width * (6 / 14), tmp.height / 2, tmp.width * (8 / 14), tmp.height / 2), fill="red")

                # Outer crosses
                draw_ch.line((tmp.width / 2, tmp.height * (2 / 10), tmp.width / 2, tmp.height * (3 / 10)), fill="red")
                draw_ch.line((tmp.width * (2 / 10), tmp.height / 2, tmp.width * (3 / 10), tmp.height / 2), fill="red")
                draw_ch.line((tmp.width / 2, tmp.height * (7 / 10), tmp.width / 2, tmp.height * (8 / 10)), fill="red")
                draw_ch.line((tmp.width * (7 / 10), tmp.height / 2, tmp.width * (8 / 10), tmp.height / 2), fill="red")

                # Ring
                center_x, center_y = tmp.width / 2, tmp.height / 2

                # Draw the outer circle
                draw_ch.ellipse((center_x - tmp.width / 5, center_y - tmp.height / 5,
                                 center_x + tmp.width / 5, center_y + tmp.height / 5),
                                outline="red", width=1)

            size = int(self.width / 4), int(self.width / 4)
            self.z_img = ImageTk.PhotoImage(tmp.resize(size))

            if event.x < 25 * (self.width / 100) and event.y < 20 * (self.height / 100):                                                            # Case it gets close upper left corner
                self.z_img_id = self.canvas.create_image(event.x + 10 * (self.width / 100),
                                                         event.y + 10 * (self.height / 100),
                                                         image=self.z_img)                                                                          # Move down right
            elif event.x < 25 * (self.width / 100):                                                                                                 # Case it gets close on the left
                self.z_img_id = self.canvas.create_image(event.x + 10 * (self.width / 100),
                                                         event.y - 10 * (self.height / 100),
                                                         image=self.z_img)                                                                          # Move only right
            elif event.y < 22 * (self.height / 100):                                                                                                # Case in gets close up
                self.z_img_id = self.canvas.create_image(event.x - 10 * (self.width / 100),
                                                         event.y + 10 * (self.height / 100),
                                                         image=self.z_img)                                                                          # Move only down
            else:                                                          # Normal case or disappear
                self.z_img_id = self.canvas.create_image(event.x - 10 * (self.width/100), event.y - 10 * (self.height/100), image=self.z_img)


# ///////////////////////////////////// METHODS /////////////////////////////////////
def run_gui() -> object:
    # Setting the window size based on the monitor resolution
    windowWidth, windowHeight = configure_geometry()

    root.geometry(str(windowWidth) + "x" + str(windowHeight))

    # Frame in which top buttons and menus will appear
    frame_top.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)
    frame_top.config(bg="lightblue")
    frame_top.config(width=windowWidth - 10, height=50)

    # Buttons
    btn_load = Button(frame_top, text="load", width=25, command=stored_route)
    btn_load.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)

    btn_camera = Button(frame_top, text="capture", width=25, command=live_route)
    btn_camera.grid(column=1, row=0, padx=5, pady=5, sticky=W + E + N + S)

    # TODO: Need to add developer menu that lets me enable the output of image with every step of image processing

    # Frame in which images will be displayed and cleared
    frame_bottom.grid(column=0, row=1, padx=5, pady=5, sticky=W + E + N + S)
    frame_bottom.config(bg="darkgray")
    frame_bottom.config(width=windowWidth - 10, height=windowHeight - 50)

    # Manage resize ratio
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=60)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()


# Method for starting preprocess of the image taking as input the webcam (MUST BE REARRANGED AND RE-FACTORIZED ONCE
# LOAD-IMAGE VERSION IS ON A DECENT STAGE)
def live_route():
    dps.document_preprocess()


# Method will be re-factorized in order to only load the image from the filesystem and all preprocess will be actually
# moved to document preprocess scanner
def stored_route():
    path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                 ("image", ".jpeg"),
                                                 ("image", ".png")])

    if len(path) > 0:
        global img_file

        # Read image on opencv
        img_file = cv2.imread(path)

        # Adjust color
        img = cv2.cvtColor(img_file, cv2.COLOR_BGR2RGB)

        # Get the original vertices
        # Needs to be changed in order to be outputted as np array
        points = dps.detect_document_vertices(img_file)

        # TODO: Change this to work in the function downscale with the height based on the resolution
        img_downscale = imutils.resize(img, height=600)

        # Translate to tkinter
        img_preview = Image.fromarray(img)
        img_preview_TK = ImageTk.PhotoImage(image=img_preview)

        img_downscale_preview = Image.fromarray(img_downscale)
        img_downscale_preview_TK = ImageTk.PhotoImage(image=img_downscale_preview)

        # Resize canvas to fit exact same size as the picture
        img_downscale_width = img_downscale_preview_TK.width()
        img_downscale_height = img_downscale_preview_TK.height()

        img_width = img_preview_TK.width()
        img_height = img_preview_TK.height()

        # Calculation of ratio between original and downsized picture
        width_ratio = img_width / img_downscale_width
        height_ratio = img_height / img_downscale_height

        # Calculate the position of the points in the downscaled image
        points_downscaled = downscale_points(points, width_ratio, height_ratio)

        for child in frame_bottom.winfo_children():
            child.destroy()

        # TODO: Reorganize these elements to be centered and based on window size live
        shape_cropper = ShapeCropper(frame_bottom, img_downscale_width, img_downscale_height, points_downscaled,
                                     img_downscale_preview_TK)
        shape_cropper.grid(column=0, row=0, padx=5, pady=5)

        btn_next = Button(frame_bottom, text="next", width=25,
                          command=lambda: get_coordinates(shape_cropper, img_width, img_height, width_ratio,
                                                          height_ratio))
        btn_next.grid(column=0, row=1, padx=5, pady=5)


def get_coordinates(shape_cropper, original_width, original_height, width_ratio, height_ratio):
    # Get cropped coordinates
    new_downscaled_points = shape_cropper.get_tokens()

    # TODO: The next button needs to call the rest of the methods
    #   that are used to process the image and warp it, since we already have the shapeCropper as a
    #   param, should be able to nullify it, but not sure on how to remove it from the actual GUI

    for child in frame_bottom.winfo_children():
        child.destroy()

    new_points = upscale_points(new_downscaled_points, width_ratio, height_ratio)

    # This is the warped image over which we will operate
    warped_image = dps.img_warp(new_points, img_file, original_width, original_height)
    warped_downscaled = imutils.resize(warped_image, height=600)

    warped_preview = Image.fromarray(warped_downscaled)
    warped_preview_TK = ImageTk.PhotoImage(image=warped_preview)

    warp_label = Label(frame_bottom, image=warped_preview_TK)
    warp_label.grid(column=0, row=0, padx=5, pady=5)

    # Everytime That an image load is needed
    root.mainloop()


def configure_geometry():
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    windowWidth = int(3 * main_monitor.width / 4)
    windowHeight = int(3 * main_monitor.height / 4)

    return windowWidth, windowHeight


def downscale_points(points, width_ratio, height_ratio):
    # TODO: Once the structure of the array is no longer double-bracketed
    #   change the way they work from points[2][0][1] to points[2][1]

    points[0][0][0] = points[0][0][0] / width_ratio
    points[0][0][1] = points[0][0][1] / height_ratio

    points[1][0][0] = points[1][0][0] / width_ratio
    points[1][0][1] = points[1][0][1] / height_ratio

    points[2][0][0] = points[2][0][0] / width_ratio
    points[2][0][1] = points[2][0][1] / height_ratio

    points[3][0][0] = points[3][0][0] / width_ratio
    points[3][0][1] = points[3][0][1] / height_ratio

    return points


def upscale_points(points, width_ratio, height_ratio):
    points[0][0] = points[0][0] * width_ratio
    points[0][1] = points[0][1] * height_ratio

    points[1][0] = points[1][0] * width_ratio
    points[1][1] = points[1][1] * height_ratio

    points[2][0] = points[2][0] * width_ratio
    points[2][1] = points[2][1] * height_ratio

    points[3][0] = points[3][0] * width_ratio
    points[3][1] = points[3][1] * height_ratio

    return points
