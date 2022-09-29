from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import imutils
import numpy as np
import cv2
import documentPreprocessScanner as dps
from screeninfo import get_monitors
import utlis

# ///////////////////////////////////// GLOBAL VARIABLES ///////////////////////////////////// 
root = Tk()
image = None
lblImage = Label(root)
windowHeight = 0
windowWidth = 0


# ///////////////////////////////////// METHODS ///////////////////////////////////// 
def run_gui() -> object:
    # Setting the window size based on the monitor resolution
    main_monitor = None
    for m in get_monitors():
        if m.is_primary:
            main_monitor = m

    global windowWidth
    windowWidth = int(main_monitor.height / 16 * 7)
    global windowHeight
    windowHeight = int(main_monitor.width / 16 * 7)

    root.geometry(str(windowWidth) + "x" + str(windowHeight))

    # Label where image will appear
    lblImage.grid(column=0, row=2)

    # Image read button
    btn_load = Button(root, text="load", width=25, command=load_image)
    btn_load.grid(column=0, row=0, padx=5, pady=5)

    # Camera option button
    btn_camera = Button(root, text="capture", width=25, command=camera)
    btn_camera.grid(column=2, row=0, padx=5, pady=5)

    root.mainloop()


# Method for starting preprocess of the image taking as input the webcam (MUST BE REARRANGED AND RE-FACTORIZED ONCE 
# LOAD-IMAGE VERSION IS ON A DECENT STAGE)
def camera():
    dps.document_preprocess()


# Method for doing all the preprocessing of an image from the filesystem
def load_image():
    path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                 ("image", ".jpeg"),
                                                 ("image", ".png")])

    if len(path) > 0:
        global image

        # Read image on opencv
        image = cv2.imread(path)

        # Whole process contained in a specific method
        final_image, image = image_preprocess(image)

        # Visualization of image in gui
        show_image = imutils.resize(final_image, height=600)
        show_image = cv2.cvtColor(show_image, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(show_image)
        img = ImageTk.PhotoImage(image=im)

        lblImage.configure(image=img)
        lblImage.image = img

        # Label input image
        lbl_info = Label(root, text="Input image")
        lbl_info.grid(column=0, row=1, padx=5, pady=5)

        # Debugging for finding the actual optimal thresholds for the contour detection to be able to maximize its 
        # accuracy
        final_image = imutils.resize(final_image, height=600)
        image = imutils.resize(image, height=600)
        cv2.imshow('finalImage', final_image)
        cv2.imshow('image', image)
        cv2.waitKey()
        cv2.destroyAllWindows()


# Parameter: Raw-Image
# Return_Value: Image with contour of the image drawn
# Observations: Might have to actually just return the values of the vertices in order to make it loop-able and make the
# pinpoint selection system
def image_preprocess(image_source):
    image = image_source

    # Copy of the original image
    original_image = image.copy()
    original_image2 = image.copy()

    # Firstly, we turn the image into grayScale
    image = dps.get_image_grayscale(image)

    # Secondly, we run edge detector through the image
    image = dps.get_image_edge_detector(image)

    # Thirdly, we have to find the contours present in the picture
    image, contours = dps.get_image_contours(image, original_image)

    # Fourth step is to find the actual biggest contour and draw it on the image
    biggest = dps.get_image_biggest_contour(contours)

    # We need to loop this stuff in order to be able to create the effect of an interface that lets us drag the
    # points of the vertices

    # We draw on the picture the coordinates of the vertices of the biggest contour
    final_image = original_image2.copy()

    if biggest.size != 0:
        dps.draw_image_biggest_contour_auto(biggest, final_image)
    else:
        height, width = image.shape[:2]

        # Set up the 4 points of the image based on the resolution of the picture, with an aspect ratio of 1:1.4
        point1 = np.array([width / 4, height / 4])
        point2 = np.array([3 * width / 4, height / 4])
        point3 = np.array([width / 4, int(3 * height / 4)])
        point4 = np.array([3 * width / 4, int(3 * height / 4)])

        dps.draw_image_biggest_contour_w_points(point1, point2, point3, point4, final_image)

    return final_image, image
