import math
import tkinter as tk

from tkinter import *
from tkinter import filedialog

import cv2
import imutils

from PIL import Image, ImageTk
from screeninfo import get_monitors

from Preprocessors import preprocess_image as ipp
from Preprocessors import preprocess_document as ppd

from UI import shape_cropper as sp
from Utils import utlis

class DDL(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.streaming = None
        self.webcam_display = None
        self.video = None
        self.points = None
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

        self.clear_frame()

        self.video = cv2.VideoCapture(0)

        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)

        size = int(60 * root.winfo_width() / 100)

        # Set elements for the webcam
        pad_x = int((self.frame_bottom.winfo_width() - size) / 2)

        self.webcam_display = Label(self.frame_bottom, bg="black")
        self.webcam_display.grid(column=0, row=0, padx=pad_x, pady=5, sticky="EW")

        btn_next = Button(self.frame_bottom, text="next", width=25,
                          command=lambda: self.stop_stream())
        btn_next.grid(column=0, row=1, padx=pad_x, pady=5, sticky="EW")

        self.start_stream()

    def start_stream(self):
        self.streaming = True

        res_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        res_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("Resolution: {} x {}".format(res_width, res_height))

        self.stream()

    def stop_stream(self):
        self.streaming = False

    # TODO:
    #   -Extract elements as a class
    #   -Enhance UI to be able to apply thresholds through a set of sliders
    def stream(self):
        ret, frame = self.video.read()

        if ret:
            image_height = int(85 * root.winfo_height() / 100)
            frame_downscaled = imutils.resize(frame, height=image_height)

            # Both copies of the frame are processed in order to get the actual high-res one
            frame_corrected = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_downscaled = cv2.cvtColor(frame_downscaled, cv2.COLOR_BGR2RGB)

            img_vertices, default = ipp.detect_document_vertices(frame_downscaled)
            boxed_img = ipp.draw_image_contour(img_vertices, frame_downscaled)

            if not default:
                img = Image.fromarray(boxed_img)
            else:
                img = Image.fromarray(frame_downscaled)

            display_img = ImageTk.PhotoImage(image=img)

            self.webcam_display.configure(image=display_img)
            self.webcam_display.image = display_img

        if self.streaming:
            self.webcam_display.after(10, self.stream)
        else:
            self.clear_frame()

            self.img = frame_corrected

            self.display_image(False)

    # ///////////////////////////////// AUXILIARY /////////////////////////////////

    def clear_frame(self):
        for child in self.frame_bottom.winfo_children():
            child.destroy()

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                     ("image", ".jpeg"),
                                                     ("image", ".png")])

        if len(path) > 0:
            # Read image on opencv
            img_file = cv2.imread(path)

            # Adjust color
            self.img = cv2.cvtColor(img_file, cv2.COLOR_BGR2RGB)

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


root = tk.Tk()

app = DDL(master=root)
app.mainloop()
