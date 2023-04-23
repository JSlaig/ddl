import cv2
import numpy as np


# TO STACK ALL THE IMAGES IN ONE WINDOW
def stack_images(img_array, scale, labels=[]):
    rows = len(img_array)
    cols = len(img_array[0])
    rows_available = isinstance(img_array[0], list)
    width = img_array[0][0].shape[1]
    height = img_array[0][0].shape[0]
    if rows_available:
        for x in range(0, rows):
            for y in range(0, cols):
                img_array[x][y] = cv2.resize(img_array[x][y], (0, 0), None, scale, scale)
                if len(img_array[x][y].shape) == 2: img_array[x][y] = cv2.cvtColor(img_array[x][y], cv2.COLOR_GRAY2BGR)
        image_blank = np.zeros((height, width, 3), np.uint8)
        hor = [image_blank] * rows
        hor_con = [image_blank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(img_array[x])
            hor_con[x] = np.concatenate(img_array[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            img_array[x] = cv2.resize(img_array[x], (0, 0), None, scale, scale)

            if len(img_array[x].shape) == 2:
                img_array[x] = cv2.cvtColor(img_array[x], cv2.COLOR_GRAY2BGR)

        hor = np.hstack(img_array)
        hor_con = np.concatenate(img_array)
        ver = hor
    if len(labels) != 0:
        each_img_width = int(ver.shape[1] / cols)
        each_img_height = int(ver.shape[0] / rows)

    return ver


def biggest_contour(contours):
    biggest = np.array([])
    max_peri = 0
    for i in contours:
        area = cv2.contourArea(i)

        # This if determines the min area the picture must have to be able to work with
        # the program itself, thing is that it affects the detection of shape somehow
        # by avoiding areas smaller than the value specified, when the picture is way too
        # small, the if does not trigger and therefore a later error is triggered
        # TODO: Find sweet-spot for the area value
        if area > 2000:
            peri = cv2.arcLength(i, True)

            approx = cv2.approxPolyDP(i, 0.0555 * peri, True)

            if peri > max_peri and len(approx) == 4:
                biggest = approx
                max_peri = peri

    return biggest, max_peri


def draw_rectangle(img, biggest, thickness):

    img_copy = img.copy()

    cv2.line(img_copy, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (173, 216, 230),
             thickness)
    cv2.line(img_copy, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (173, 216, 230),
             thickness)
    cv2.line(img_copy, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (173, 216, 230),
             thickness)
    cv2.line(img_copy, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (173, 216, 230),
             thickness)

    return img_copy


def reorder(my_points):
    my_points = np.array(my_points)
    my_points = my_points.reshape((4, 2))
    my_points_new = np.zeros((4, 1, 2), dtype=np.int32)

    add = my_points.sum(1)

    my_points_new[0] = my_points[np.argmin(add)]
    my_points_new[3] = my_points[np.argmax(add)]

    diff = np.diff(my_points, axis=1)

    my_points_new[1] = my_points[np.argmin(diff)]
    my_points_new[2] = my_points[np.argmax(diff)]

    return my_points_new


def nothing(x):
    pass


def initialize_trackbars():
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Threshold1", "Trackbars", 200, 255, nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 200, 255, nothing)


def val_trackbars():
    threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    src = threshold1, threshold2
    return src
