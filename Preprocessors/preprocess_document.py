import cv2
import numpy as np
import imutils


def get_paragraph(sheet, flag_dev=False):
    sheet_copy = sheet.copy()

    sheet_gray = cv2.cvtColor(sheet_copy, cv2.COLOR_BGR2GRAY)

    sheet_blur = cv2.GaussianBlur(sheet_gray, (7, 7), 0)

    # We invert the binary filter in order for the lettering in the sheet to be white and expandable
    sheet_otsu = cv2.threshold(sheet_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]


    # Create rectangular structuring element and dilate
    # May need to have elements in the ui in order to modify for proper detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    sheet_dilated = cv2.dilate(sheet_otsu, kernel, iterations=4)

    sheet_bboxed = draw_paragraph(sheet_dilated, sheet)

    # TODO: Manage with checkbox on UI
    flag_dev = True
    if flag_dev:
        sheet_gray_ds = imutils.resize(sheet_gray, height=600)
        sheet_blur_ds = imutils.resize(sheet_blur, height=600)
        sheet_otsu_ds = imutils.resize(sheet_otsu, height=600)
        sheet_dilated_ds = imutils.resize(sheet_dilated, height=600)
        sheet_bboxed_ds = imutils.resize(sheet_bboxed, height=600)

        cv2.imshow("Grayscale", sheet_gray_ds)
        cv2.imshow("Blur", sheet_blur_ds)
        cv2.imshow("Binary Otsu", sheet_otsu_ds)
        cv2.imshow("Dilated", sheet_dilated_ds)
        cv2.imshow("Bound Boxed", sheet_bboxed_ds)

        cv2.waitkey(0)

    return None


def draw_paragraph(dilated_sheet, sheet):
    sheet_copy = sheet.copy()

    # Find contours and draw rectangle
    contours = cv2.findContours(dilated_sheet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(sheet_copy, (x, y), (x + w, y + h), (36, 255, 12), 2)

    return sheet_copy
