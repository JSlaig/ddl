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
from ShapeCropper import ShapeCropper

# ///////////////////////////////////// ATTRIBUTES OF GUI /////////////////////////////////////
root = Tk()  # Assignation of root window
root.title('DDL')  # Assignation of the window title
root.wm_iconbitmap('Assets/DDL.ico')  # Setting an icon for the application

frame_top = Frame(root)
frame_bottom = Frame(root)
img_file = None
lblImage = Label(root)

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
    btn_load = Button(frame_top, text="load", width=25, command=lambda: display_image(True))
    btn_load.grid(column=0, row=0, padx=5, pady=5, sticky=W + E + N + S)

    btn_camera = Button(frame_top, text="capture", width=25, command=webcam)
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

def webcam():
    # TODO: rewrite most of this
    dps.document_preprocess()

def display_image(path):
    if path:
        img = load_image()
    else:
        # Here image save from the cam will be taken
        print('Should have webcammed it')

    # Get the original vertices
    # Needs to be changed in order to be outputted as np array
    points = dps.detect_document_vertices(img_file)

    window_height = root.winfo_height()

    image_height = int(85 * window_height / 100)
    img_downscale = imutils.resize(img, height=image_height)

    # Translate to tkinter
    img_preview = Image.fromarray(img)
    img_preview_TK = ImageTk.PhotoImage(image=img_preview)

    img_downscale_preview = Image.fromarray(img_downscale)
    img_downscale_preview_TK = ImageTk.PhotoImage(image=img_downscale_preview)

    # Resize corners to fit exact same size as the picture
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
    #   -Set elements inside frame
    shape_cropper = ShapeCropper(root, frame_bottom, img_downscale_width, img_downscale_height, points_downscaled,
                                 img_downscale_preview_TK)
    shape_cropper.grid(column=0, row=0, padx=5, pady=5)

    btn_next = Button(frame_bottom, text="next", width=25,
                      command=lambda: get_coordinates(shape_cropper, img_width, img_height, width_ratio,
                                                      height_ratio))
    btn_next.grid(column=0, row=1, padx=5, pady=5)

def configure_geometry():
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    windowWidth = int(3 * main_monitor.width / 4)
    windowHeight = int(3 * main_monitor.height / 4)

    return windowWidth, windowHeight

def load_image():
    path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                 ("image", ".jpeg"),
                                                 ("image", ".png")])

    if len(path) > 0:
        global img_file

        # Read image on opencv
        img_file = cv2.imread(path)

        # Adjust color
        img = cv2.cvtColor(img_file, cv2.COLOR_BGR2RGB)

    return img

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
    window_height = root.winfo_height()
    image_height = int(85 * window_height / 100)
    warped_downscaled = imutils.resize(warped_image, height=image_height)

    warped_preview = Image.fromarray(warped_downscaled)
    warped_preview_TK = ImageTk.PhotoImage(image=warped_preview)

    warp_label = Label(frame_bottom, image=warped_preview_TK)
    warp_label.grid(column=0, row=0, padx=5, pady=5)

    # Everytime That an image load is needed
    root.mainloop()