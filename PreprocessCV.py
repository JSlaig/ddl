import cv2
import numpy as np

import utlis


# Since the function goes through several steps, I will split it into different
# functions that don't use a loop to start to make it able to use the image we
# load in the gui from the filesystem

def get_image_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE


def get_image_edge_detector(image):
    img_blur = cv2.GaussianBlur(image, (5, 5), 1)  # ADD GAUSSIAN BLUR

    # Thresholds will be calculated automatically, since I need to find the sweetspot
    # to make it detect the edges correctly, currently it works from values from
    # 200 to 255.
    # Idea is to make them fixed and maybe have a settings tab where I could change
    # them if necessary.
    # So currently what I am gonna do is to set them manually as a parameter and tweak
    # them right there until I figure out how I really want to make the actual menu

    img_threshold = cv2.Canny(img_blur, 10, 80)  # APPLY CANNY BLUR

    kernel = np.ones((5, 5))

    img_dial = cv2.dilate(img_threshold, kernel, iterations=2)  # APPLY DILATION
    return cv2.erode(img_dial, kernel, iterations=1)  # APPLY EROSION


def get_image_contours(image, original):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
    return cv2.drawContours(original, contours, -1, (0, 255, 0), 10), contours  # DRAW ALL DETECTED CONTOURS


def get_image_biggest_contour(contours):
    # FIND THE BIGGEST CONTOUR
    biggest, max_area = utlis.biggest_contour(contours)  # FIND THE BIGGEST CONTOUR

    return biggest


def draw_image_contour(point1, point2, point3, point4, image):
    biggest = np.array([[point1], [point2], [point3], [point4]])
    biggest = utlis.reorder(biggest)
    cv2.drawContours(image, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
    utlis.draw_rectangle(image, biggest, 2)
    return image

# TODO: Something gets fucked up in here always in terms of detection
def detect_document_vertices(image_source):
    image_aux = image_source

    # Copy of the original image
    original_image = image_aux.copy()

    # Firstly, we turn the image into grayScale
    image_aux = get_image_grayscale(image_aux)

    # Secondly, we run edge detector through the image
    image_aux = get_image_edge_detector(image_aux)

    # Thirdly, we have to find the contours present in the picture
    image_aux, contours = get_image_contours(image_aux, original_image)

    # Fourth step is to find the actual biggest contour and draw it on the image
    biggest = get_image_biggest_contour(contours)

    # In case no contour is detected, we establish a default one
    if biggest.size == 0:
        height, width = image_aux.shape[:2]

        # Set up the 4 points of the image based on the resolution of the picture, with an aspect ratio of 1:1.4
        biggest = np.array([[int(width / 4), int(height / 4)], [int(3 * width / 4), int(height / 4)], [int(width / 4), int(3 * height / 4)],
                            [int(3 * width / 4), int(3 * height / 4)]])
    return biggest


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


# Function is currently outdated, still maintaining it in here because I need some code contained inside, but the
# whole branch of execution will be remade in order to work with the functions above in a loop with some changes
def document_preprocess():
    ########################################################################
    web_cam_feed = True
    path_image = "1.jpg"

    cap = cv2.VideoCapture(0)
    cap.set(10, 160)

    height_img = 640
    width_img = 480
    ########################################################################

    utlis.initialize_trackbars()
    count = 0

    # Whole infinite loop is working with the webcam frame by frame trying to detect
    # the stuff, lot of tweaking required still
    while True:

        if web_cam_feed:
            success, img = cap.read()
        else:
            img = cv2.imread(path_image)
            img = cv2.resize(img, (width_img, height_img))  # RESIZE IMAGE
        img_blank = np.zeros((height_img, width_img, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGGING

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE

        img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)  # ADD GAUSSIAN BLUR
        thresholds = utlis.val_trackbars()  # GET TRACK BAR VALUES FOR THRESHOLDS
        img_threshold = cv2.Canny(img_blur, thresholds[0], thresholds[1])  # APPLY CANNY BLUR
        kernel = np.ones((5, 5))
        img_dial = cv2.dilate(img_threshold, kernel, iterations=2)  # APPLY DILATION
        img_threshold = cv2.erode(img_dial, kernel, iterations=1)  # APPLY EROSION

        # FIND ALL CONTOURS
        img_contours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        img_big_contour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        contours, hierarchy = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
        cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

        # FIND THE BIGGEST CONTOUR
        biggest = utlis.biggest_contour(contours)  # FIND THE BIGGEST CONTOUR
        if biggest != 0:
            biggest = utlis.reorder(biggest)
            cv2.drawContours(img_big_contour, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
            img_big_contour = utlis.draw_rectangle(img_big_contour, biggest, 2)

            pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
            pts2 = np.float32(
                [[0, 0], [width_img, 0], [0, height_img], [width_img, height_img]])  # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            img_warp_colored = cv2.warpPerspective(img, matrix, (width_img, height_img))

            # REMOVE 20 PIXELS FORM EACH SIDE
            img_warp_colored = img_warp_colored[20:img_warp_colored.shape[0] - 20, 20:img_warp_colored.shape[1] - 20]
            img_warp_colored = cv2.resize(img_warp_colored, (width_img, height_img))

            # APPLY ADAPTIVE THRESHOLD
            img_warp_gray = cv2.cvtColor(img_warp_colored, cv2.COLOR_BGR2GRAY)
            img_adaptive_thresholds = cv2.adaptiveThreshold(img_warp_gray, 255, 1, 1, 7, 2)
            img_adaptive_thresholds = cv2.bitwise_not(img_adaptive_thresholds)
            img_adaptive_thresholds = cv2.medianBlur(img_adaptive_thresholds, 3)

            # Image Array for Display
            image_array = ([img, img_gray, img_threshold, img_contours],
                           [img_big_contour, img_warp_colored, img_warp_gray, img_adaptive_thresholds])

        else:
            image_array = ([img, img_gray, img_threshold, img_contours],
                           [img_blank, img_blank, img_blank, img_blank])

        # LABELS FOR DISPLAY
        lables = [["Original", "Gray", "Threshold", "Contours"],
                  ["Biggest Contour", "Warp Prespective", "Warp Gray", "Adaptive Threshold"]]

        stacked_image = utlis.stack_images(image_array, 0.75, lables)
        cv2.imshow("Result", stacked_image)

        # will make modifications to this to actually use it in both filesystem and cam images.
        # SAVE IMAGE WHEN 's' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite("Scanned/myImage" + str(count) + ".jpg", img_warp_colored)
            cv2.rectangle(stacked_image,
                          ((int(stacked_image.shape[1] / 2) - 230), int(stacked_image.shape[0] / 2) + 50),
                          (1100, 350), (0, 255, 0), cv2.FILLED)
            cv2.putText(stacked_image, "Scan Saved",
                        (int(stacked_image.shape[1] / 2) - 200, int(stacked_image.shape[0] / 2)),
                        cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5, cv2.LINE_AA)
            cv2.imshow('Result', stacked_image)
            cv2.waitKey(300)
            count += 1
