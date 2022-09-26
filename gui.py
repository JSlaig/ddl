from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import imutils
import numpy as np
import cv2
import documentPreprocessScanner as dps
import imagePinPointTesting as ipptasdf
from screeninfo import get_monitors
import utlis

#Global variables
root = Tk()
image = None
lblImage = Label(root)
windowHeight=0
windowWidth=0

def camera():
    dps.documentPreprocess()

def loadImage():
    path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                 ("image", ".jpeg"),
                                                 ("image", ".png")])

    if len(path) > 0:
        global image

        # Read image on opencv
        image = cv2.imread(path)

        # Copy of the original image
        originalImage = image.copy()
        originalImage2 = image.copy()


        # Firstly, we turn the image into grayScale
        image = dps.getImageGrayscale(image)

        # Secondly, we run edge detector through the image
        image = dps.getImageEdgeDetector(image)

        # Thirdly, we have to find the contours present in the picture
        image, contours = dps.getImageContours(image, originalImage)

        # Fourth step is to find the actual biggest contour and draw it on the image
        biggest = dps.getImageBiggestContour(contours)

        # We need to loop this stuff in order to be able to create the effect of an interface that lets us drag the
        # points of the vertices

        # We draw on the picture the coordinates of the vertices of biggest contour (pending to draw default ones
        # otherwise)
        if biggest.size != 0:
            biggest = utlis.reorder(biggest)
            finalImage = originalImage2.copy()
            cv2.drawContours(finalImage, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
            utlis.drawRectangle(finalImage, biggest, 2)

        # Visualization of image in gui
        showImage = imutils.resize(finalImage, height=600)
        showImage = cv2.cvtColor(showImage, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(showImage)
        img = ImageTk.PhotoImage(image=im)

        lblImage.configure(image=img)
        lblImage.image = img

        #Label input image
        lblInfo = Label(root, text="Input image")
        lblInfo.grid(column=0, row=1, padx=5, pady=5)

        #Debugging
        finalImage = imutils.resize(finalImage, height=600)
        image = imutils.resize(image, height=600)
        cv2.imshow('finalImage', finalImage)
        cv2.imshow('image', image)
        cv2.waitKey()
        cv2.destroyAllWindows()


def runGUI():

    # Setting the window size based on the monitor resolution
    mainMonitor = None
    for m in get_monitors():
        if m.is_primary == True:
            mainMonitor = m

    global windowWidth
    windowWidth = int(mainMonitor.height / 16 * 7)
    global windowHeight
    windowHeight = int(mainMonitor.width / 16 * 7)

    root.geometry(str(windowWidth)+"x"+str(windowHeight))

    # Label where image will appear
    lblImage.grid(column=0, row=2)

    # Image read button
    btnLoad = Button(root, text="load", width=25, command=loadImage)
    btnLoad.grid(column=0, row=0, padx=5, pady=5)

    # Camera option button
    btnCamera = Button(root, text="capture", width=25, command=camera)
    btnCamera.grid(column=2, row=0, padx=5, pady=5)

    root.mainloop()