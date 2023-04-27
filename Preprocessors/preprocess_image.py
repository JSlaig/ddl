import cv2
import imutils
import numpy as np

from Utils import utlis


def get_edges(img, dev_flag, threshold_1=10, threshold_2=80):
    img_blur = cv2.GaussianBlur(img, (5, 5), 1)  # ADD GAUSSIAN BLUR

    img_threshold = cv2.Canny(img_blur, threshold_1, threshold_2)  # APPLY CANNY BLUR

    kernel = np.ones((5, 5))

    img_dilated = cv2.dilate(img_threshold, kernel, iterations=2)  # APPLY DILATION

    img_eroded = cv2.erode(img_dilated, kernel, iterations=1)  # APPLY EROSION

    ret, img_otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    dev = {}

    # TODO: Make this actually be triggered by checkbox in UI
    if dev_flag != 0:
        dev["Gaussian Blurred"] = img_blur
        dev["Dilated"] = img_dilated
        dev["Eroded"] = img_eroded
        dev["Otsu"] = img_otsu

    return img_otsu, dev


def get_contours(img, original):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS

    drawn_contours = cv2.drawContours(original, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

    return drawn_contours, contours


def get_biggest_contour(contours):
    # FIND THE BIGGEST CONTOUR
    biggest, max_area = utlis.biggest_contour(contours)  # FIND THE BIGGEST CONTOUR

    return biggest


def draw_image_contour(biggest, img):
    biggest = utlis.reorder(biggest)
    drawn_img = utlis.draw_rectangle(img, biggest, 2)

    return drawn_img


def detect_document_vertices(img, dev_flag, t1=10, t2=80):
    # Flag used in the webcam mode to see if the prediction is default
    # or a real one indeed
    flag_default = False

    # Copy of the original image
    img_copy = img.copy()

    # Firstly, we turn the image into grayScale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Secondly, we run edge detector through the image
    img, dev_imgs = get_edges(img, dev_flag, t1, t2)

    # Thirdly, we have to find the contours present in the picture
    img, contours = get_contours(img, img_copy)

    if dev_flag != 0:
        dev_imgs["Contoured image"] = img

    # Fourth step is to find the actual biggest contour and draw it on the image
    biggest = get_biggest_contour(contours)

    # In case no contour is detected, we establish a default one
    if biggest.size == 0:
        flag_default = True

        height, width = img.shape[:2]

        # Set up the 4 points of the image based on the resolution of the picture, with an aspect ratio of 1:1.4
        biggest = np.array([[int(width / 4), int(height / 4)], [int(3 * width / 4), int(height / 4)],
                            [int(width / 4), int(3 * height / 4)],
                            [int(3 * width / 4), int(3 * height / 4)]])

    return biggest, flag_default, dev_imgs


def img_warp(contour, img, width, height):
    contour = utlis.reorder(contour)

    pts1 = np.float32(contour)  # PREPARE POINTS FOR WARP
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])  # PREPARE POINTS FOR WARP

    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    img_warp_colored = cv2.warpPerspective(img, matrix, (width, height))

    # REMOVE 20 PIXELS FORM EACH SIDE
    img_warp_colored = img_warp_colored[20:img_warp_colored.shape[0] - 20, 20:img_warp_colored.shape[1] - 20]
    img_warp_colored = cv2.resize(img_warp_colored, (width, height))

    return img_warp_colored
