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


# ///////////////////////////////////// CLASS /////////////////////////////////////
class App:
    def __init__(self, root):
        self.root = root
        self.mouse_pressed = False

    def OnMouseDown(self, event):
        self.mouse_pressed = True
        self.poll()

    def OnMouseUp(self, event):
        self.root.after_cancel(self.after_id)

    def poll(self):
        if self.mouse_pressed:
            self.do_work()
            self.after_id = self.root.after(250, self.poll)


# ///////////////////////////////////// GLOBAL VARIABLES /////////////////////////////////////
root = Tk()
app = App(root)
image = None
lblImage = Label(root)
windowHeight = 0
windowWidth = 0
mouse_x = 0
mouse_y = 0
mouse_1 = False


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

    # Label where image will appear
    lblImage.grid(column=0, row=2)

    # Image read button
    btn_load = Button(root, text="load", width=25, command=load_image)
    btn_load.grid(column=0, row=0, padx=5, pady=5)

    # Camera option button
    btn_camera = Button(root, text="capture", width=25, command=camera)
    btn_camera.grid(column=2, row=0, padx=5, pady=5)

    root.bind('<Motion>', motion)
    root.bind('<ButtonPress-1>', lclick_hold)
    root.bind('<ButtonRelease-1>', lclick_release)
    root.mainloop()


def motion(event):
    mouse_x, mouse_y = event.x, event.y
    print('x, y -> {}, {}'.format(mouse_x, mouse_y))

def lclick_hold(event):
    mouse_1 = True
    print('left click pressed!')

def lclick_release(event):
    mouse_1 = False
    print('Left click released!')

# Method for starting preprocess of the image taking as input the webcam (MUST BE REARRANGED AND RE-FACTORIZED ONCE 
# LOAD-IMAGE VERSION IS ON A DECENT STAGE)
def camera():
    dps.document_preprocess()


# Method will be refactorized in order to only load the image from the filesystem and all preprocess will be actually
# moved to document preprocess scanner
def load_image():
    path = filedialog.askopenfilename(filetypes=[("image", ".jpg"),
                                                 ("image", ".jpeg"),
                                                 ("image", ".png")])

    if len(path) > 0:
        global image

        # Read image on opencv
        image = cv2.imread(path)

        # When we resize the image here what we are really doing is lowering the actual resolution of the image
        # which alters the way the document shape is detected, which in some cases has helped to "autopinpoint" the
        # right shape but in others it might fuck it up.
        image_lowres = imutils.resize(image, height=600)
        cv2.imshow('preImage', image_lowres)

        # Get the auto-detected borders of the shape
        point1, point2, point3, point4 = detect_document_vertices(image_lowres)

        print("--------------------------------------")
        print("Coordinates for vertices are: ")
        print(point1)
        print(point2)
        print(point3)
        print(point4)
        print("--------------------------------------")

        # Got to loop this in order to find current mouse coordinates and refresh the position of each point
        # Loop must be constraint with the value of a button that actually stores the final vertices value in
        # order to warp perspective afterwards

        #while True:
            #if app.mouse_pressed:
                # If mouse is pressed then we have to check the coordinates in order to change the value of them
                # and the value must be refreshed on the screen as well, so the loop must start here until the end

        # final_image is made for mere display purposes, since the actual image used for processing later on will be the
        # original(high_res) and the coordinates scaled up to match the resolution of the original image
        final_image = dps.draw_image_biggest_contour(point1, point2, point3, point4, image_lowres)



        # Visualization of image in gui
        show_image = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB) # Need to change the color scheme for proper visuals
        show_image = imutils.resize(show_image, height=600)
        im = Image.fromarray(show_image)
        img = ImageTk.PhotoImage(image=im)

        lblImage.configure(image=img)
        lblImage.image = img

        # Label input image
        lbl_info = Label(root, text="Input image")
        lbl_info.grid(column=0, row=1, padx=5, pady=5)

        final_image = imutils.resize(final_image, height=600)
        cv2.imshow('finalImage', final_image)
        cv2.waitKey()
        cv2.destroyAllWindows()


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
