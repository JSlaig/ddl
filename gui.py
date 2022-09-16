from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import imutils
import numpy as np
import cv2
import documentPreprocessScanner as dps
import imagePinPointTesting as ipptasdf

#Global variables
root = Tk()
image = None
lblImage = Label(root)

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
        image = imutils.resize(image, height=380)

        # Visualization of image in gui(subject to change)
        showImage = imutils.resize(image, width=600)
        showImage = cv2.cvtColor(showImage, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(showImage)
        img = ImageTk.PhotoImage(image=im)

        lblImage.configure(image=img)
        lblImage.image = img

        #Label input image
        lblInfo = Label(root, text="Input image")
        lblInfo.grid(column=0, row=1, padx=5, pady=5)

def runGUI():

    #Label where image will appear

    lblImage.grid(column=0, row=2)

    # Image read button
    btnLoad = Button(root, text="load", width=25, command=loadImage)
    btnLoad.grid(column=0, row=0, padx=5, pady=5)

    # Camera option button
    btnCamera = Button(root, text="capture", width=25, command=camera)
    btnCamera.grid(column=2, row=0, padx=5, pady=5)

    root.mainloop()