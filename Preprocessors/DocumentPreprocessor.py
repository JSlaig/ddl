import cv2
import numpy as np
import imutils


def get_paragraph(sheet, size, dev_flag=False):
    sheet_copy = sheet.copy()

    sheet_gray = cv2.cvtColor(sheet_copy, cv2.COLOR_BGR2GRAY)

    sheet_blur = cv2.GaussianBlur(sheet_gray, (7, 7), 0)

    # We invert the binary filter in order for the lettering in the sheet to be white and expandable
    sheet_otsu = cv2.threshold(sheet_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(size * 1.5), int(size)))
    sheet_dilated = cv2.dilate(sheet_otsu, kernel, iterations=4)

    sheet_bboxed, contours = draw_paragraph(sheet_dilated, sheet)

    dev = {}

    if dev_flag != 0:
        dev["Inverse Binary"] = sheet_otsu
        dev["Dilated Text"] = sheet_dilated

    return sheet_bboxed, contours, dev


def draw_paragraph(dilated_sheet, sheet):
    sheet_copy = sheet.copy()

    # Find contours and draw rectangle
    contours = cv2.findContours(dilated_sheet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(sheet_copy, (x, y), (x + w, y + h), (1, 156, 255), 2)

    return sheet_copy, contours


