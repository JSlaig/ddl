import tkinter as tk

import time

from tkinter import *
from tkinter import filedialog

import threading

import cv2
import imutils

from PIL import Image, ImageTk
from screeninfo import get_monitors

import PreprocessCV as dps
from ShapeCropper import ShapeCropper


# Initial window size based on resolution
def configure_geometry():
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    width = int(3 * main_monitor.width / 4)
    height = int(3 * main_monitor.height / 4)

    return width, height


class DDL(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.stream_thread = None
        self.streaming = None
        self.webcam_display = None
        self.video = None
        self.points = None
        self.img_file = None
        self.height_ratio = None
        self.width_ratio = None
        self.master = master

        self.frame_top = Frame(root)
        self.frame_bottom = Frame(root)

        self.img = None
        self.img_downscaled = None
        self.lblImage = Label(root)

        # Frame in which top buttons and menus will appear
        self.frame_top.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)
        self.frame_top.config(bg="lightblue")
        self.frame_top.config(width=root.winfo_width() - 10, height=50)

        # Buttons
        btn_load = Button(self.frame_top, text="load", width=25, command=lambda: self.display_image(True))
        btn_load.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)

        btn_camera = Button(self.frame_top, text="capture", width=25, command=self.display_webcam)
        btn_camera.grid(column=1, row=0, padx=5, pady=5, sticky=W + E + N + S)

        # TODO: Need to add developer menu that lets me enable the output of image with every step of image processing

        # Frame in which images will be displayed and cleared
        self.frame_bottom.grid(column=0, row=1, padx=5, pady=5, sticky=W + E + N + S)
        self.frame_bottom.config(bg="darkgray")
        self.frame_bottom.config(width=root.winfo_width() - 10, height=root.winfo_height() - 50)

        # Manage resize ratio
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=60)
        root.grid_columnconfigure(0, weight=1)

    def display_webcam(self):
        self.video = None

        # Set elements for the webcam
        pad_x = self.frame_bottom.winfo_width() / 3

        self.webcam_display = Label(self.frame_bottom, bg="black")
        self.webcam_display.grid(column=0, row=0, padx=pad_x, pady=5, sticky="EW")

        btn_next = Button(self.frame_bottom, text="next", width=25,
                          command=lambda: self.stop_stream())
        btn_next.grid(column=0, row=1, padx=pad_x, pady=5, sticky="EW")

        self.start_stream()

    def display_image(self, load_from_filesystem):
        if load_from_filesystem:
            self.load_image()

        # Get the original vertices
        # Needs to be changed in order to be outputted as np array
        self.points = dps.detect_document_vertices(self.img_file)

        image_height = int(85 * root.winfo_height() / 100)
        self.img_downscaled = imutils.resize(self.img, height=image_height)

        # Translate to tkinter
        img_preview = Image.fromarray(self.img)
        img_preview_TK = ImageTk.PhotoImage(image=img_preview)

        img_downscale_preview = Image.fromarray(self.img_downscaled)
        img_downscale_preview_TK = ImageTk.PhotoImage(image=img_downscale_preview)

        # Resize corners to fit exact same size as the picture
        img_downscale_width = img_downscale_preview_TK.width()
        img_downscale_height = img_downscale_preview_TK.height()

        img_width = img_preview_TK.width()
        img_height = img_preview_TK.height()

        # Calculation of ratio between original and downsized picture
        self.width_ratio = img_width / img_downscale_width
        self.height_ratio = img_height / img_downscale_height

        # Calculate the position of the points in the downscaled image
        points_downscaled = self.downscale_points(self.points)

        # TODO: Might want to alter this to be class oriented as well
        self.clear_frame()

        pad_x = self.frame_bottom.winfo_width() / 3
        shape_cropper = ShapeCropper(root, self.frame_bottom, img_downscale_width, img_downscale_height,
                                     points_downscaled,
                                     img_downscale_preview_TK)
        shape_cropper.grid(column=0, row=0, padx=pad_x, pady=5, sticky="EW")

        btn_next = Button(self.frame_bottom, text="next", width=25,
                          command=lambda: self.get_coordinates(shape_cropper, img_width, img_height))
        btn_next.grid(column=0, row=1, padx=pad_x, pady=5, sticky="EW")

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                     ("image", ".jpeg"),
                                                     ("image", ".png")])

        if len(path) > 0:
            # Read image on opencv
            self.img_file = cv2.imread(path)

            # Adjust color
            self.img = cv2.cvtColor(self.img_file, cv2.COLOR_BGR2RGB)

    def downscale_points(self, points):
        # TODO: Once the structure of the array is no longer double-bracketed
        #   change the way they work from points[2][0][1] to points[2][1]

        points[0][0][0] = points[0][0][0] / self.width_ratio
        points[0][0][1] = points[0][0][1] / self.height_ratio

        points[1][0][0] = points[1][0][0] / self.width_ratio
        points[1][0][1] = points[1][0][1] / self.height_ratio

        points[2][0][0] = points[2][0][0] / self.width_ratio
        points[2][0][1] = points[2][0][1] / self.height_ratio

        points[3][0][0] = points[3][0][0] / self.width_ratio
        points[3][0][1] = points[3][0][1] / self.height_ratio

        return points

    def upscale_points(self, points):
        points[0][0] = points[0][0] * self.width_ratio
        points[0][1] = points[0][1] * self.height_ratio

        points[1][0] = points[1][0] * self.width_ratio
        points[1][1] = points[1][1] * self.height_ratio

        points[2][0] = points[2][0] * self.width_ratio
        points[2][1] = points[2][1] * self.height_ratio

        points[3][0] = points[3][0] * self.width_ratio
        points[3][1] = points[3][1] * self.height_ratio

        return points

    def get_coordinates(self, shape_cropper, img_width, img_height):
        # Get cropped coordinates
        new_downscaled_points = shape_cropper.get_tokens()

        self.points = self.upscale_points(new_downscaled_points)

        # TODO: change this to be a new class that displays the warped image
        # Remove elements then put new in
        self.clear_frame()

        # This is the warped image over which we will operate
        warped_image = dps.img_warp(self.points, self.img_file, img_width, img_height)

        image_height = int(85 * root.winfo_height() / 100)
        warped_downscaled = imutils.resize(warped_image, height=image_height)

        warped_preview = Image.fromarray(warped_downscaled)
        warped_preview_TK = ImageTk.PhotoImage(image=warped_preview)

        warp_label = Label(self.frame_bottom, image=warped_preview_TK)
        pad_x = self.frame_bottom.winfo_width() / 3
        warp_label.grid(column=0, row=0, padx=pad_x, pady=5)

        # Everytime That an image load is needed
        root.mainloop()

    def start_stream(self):
        self.streaming = True
        self.video = cv2.VideoCapture(0)

        self.stream()

    def stop_stream(self):
        self.streaming = False

    # TODO: Fix resolution of the camera, add live detection of document shape
    def stream(self):
        ret, frame = self.video.read()

        if ret:
            # TODO:Try to crop it
            # frame = frame[0:800, 0:800]

            image_height = int(85 * root.winfo_height() / 100)
            frame_downscaled = imutils.resize(frame, height=image_height)

            # Both copies of the frame are processed in order to get the actual high-res one
            frame_corrected = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_downscaled = cv2.cvtColor(frame_downscaled, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_downscaled)
            display_img = ImageTk.PhotoImage(image=img)

            self.webcam_display.configure(image=display_img)
            self.webcam_display.image = display_img

        if self.streaming:
            self.webcam_display.after(10, self.stream)
        else:
            self.clear_frame()

            self.img_file = frame_corrected
            self.img = frame_corrected

            self.display_image(False)

    def clear_frame(self):
        for child in self.frame_bottom.winfo_children():
            child.destroy()


root = tk.Tk()

root.title('DDL')  # Assignation of the window title
root.wm_iconbitmap('Assets/DDL.ico')  # Setting an icon for the application

# Setting the window size based on the monitor resolution
window_width, window_height = configure_geometry()
root.geometry(str(window_width) + "x" + str(window_height))

app = DDL(master=root)
app.mainloop()
