import cv2
import imutils
import numpy as np

import utlis


def get_edges(image, threshold_1=10, threshold_2=80, flag_dev=False):
    img_blur = cv2.GaussianBlur(image, (5, 5), 1)  # ADD GAUSSIAN BLUR

    # TODO: make these work as params
    # Thresholds will be calculated automatically, since I need to find the sweetspot
    # to make it detect the edges correctly, currently it works from values from
    # 200 to 255.
    img_threshold = cv2.Canny(img_blur, threshold_1, threshold_2)  # APPLY CANNY BLUR

    kernel = np.ones((5, 5))

    img_dilated = cv2.dilate(img_threshold, kernel, iterations=2)  # APPLY DILATION

    img_eroded = cv2.erode(img_dilated, kernel, iterations=1)  # APPLY EROSION

    # TODO: Make this actually be triggered by checkbox in UI
    if flag_dev:
        # downscale each pic to be able to see them
        img_blur_ds = imutils.resize(img_blur, height=400)
        img_dilated_ds = imutils.resize(img_dilated, height=400)
        img_eroded_ds = imutils.resize(img_eroded, height=400)

        cv2.imshow("Gaussian Blurred", img_blur_ds)
        cv2.imshow("Dilated", img_dilated_ds)
        cv2.imshow("Eroded", img_eroded_ds)

        cv2.waitkey(0)

    return img_eroded


def get_contours(image, original, dev=False):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS

    drawn_contours = cv2.drawContours(original, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

    # TODO: dependant on dev flag
    if dev:
        drawn_contours_ds = imutils.resize(drawn_contours, height=600)

        cv2.imshow("Contoured img", drawn_contours_ds)

        cv2.waitkey(0)

    return drawn_contours, contours


def get_biggest_contour(contours):
    # FIND THE BIGGEST CONTOUR
    biggest, max_area = utlis.biggest_contour(contours)  # FIND THE BIGGEST CONTOUR

    return biggest


def draw_image_contour(biggest, image):
    biggest = utlis.reorder(biggest)
    drawn_image = utlis.draw_rectangle(image, biggest, 2)

    return drawn_image


def detect_document_vertices(image_source):
    # Flag used in the webcam mode to see if the prediction is default
    # or a real one indeed
    flag_default = False

    image_aux = image_source

    # Copy of the original image
    original_image = image_aux.copy()

    # Firstly, we turn the image into grayScale
    image_aux = cv2.cvtColor(image_aux, cv2.COLOR_BGR2GRAY)

    # Secondly, we run edge detector through the image
    image_aux = get_edges(image_aux)

    # Thirdly, we have to find the contours present in the picture
    image_aux, contours = get_contours(image_aux, original_image)

    # Fourth step is to find the actual biggest contour and draw it on the image
    biggest = get_biggest_contour(contours)

    # In case no contour is detected, we establish a default one
    if biggest.size == 0:
        flag_default = True

        height, width = image_aux.shape[:2]

        # Set up the 4 points of the image based on the resolution of the picture, with an aspect ratio of 1:1.4
        biggest = np.array([[int(width / 4), int(height / 4)], [int(3 * width / 4), int(height / 4)],
                            [int(width / 4), int(3 * height / 4)],
                            [int(3 * width / 4), int(3 * height / 4)]])

    return biggest, flag_default


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
