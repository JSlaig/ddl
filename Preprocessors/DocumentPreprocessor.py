import cv2
import numpy as np
import imutils


def get_paragraph(sheet, size, min_area, dev_flag=False):
    sheet_copy = sheet.copy()

    sheet_gray = cv2.cvtColor(sheet_copy, cv2.COLOR_BGR2GRAY)

    sheet_blur = cv2.GaussianBlur(sheet_gray, (7, 7), 0)

    # We invert the binary filter in order for the lettering in the sheet to be white and expandable
    sheet_otsu = cv2.threshold(sheet_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    # kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (int(size * 0.25), int(size * 0.25)))
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (int(size * 1.5), int(size)))

    sheet_dilated = cv2.dilate(sheet_otsu, kernel_dilate, iterations=4)

    sheet_bboxed, contours = draw_paragraph(sheet_dilated, sheet, min_area)

    dev = {}

    if dev_flag != 0:
        dev["Inverse Binary"] = sheet_otsu
        dev["Dilated Text"] = sheet_dilated

    return sheet_bboxed, contours, dev


def filter_contours(contours, min_area=0):
    # Sort contours by area in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    filtered_contours = []
    for contour in contours:
        # Calculate the area of the contour
        area = cv2.contourArea(contour)

        # Check if the area meets the minimum area threshold
        if area >= min_area:
            # Get the bounding rectangle of the contour
            x, y, w, h = cv2.boundingRect(contour)

            # Check if any coordinate of the contour belongs to any of the filtered contours
            belongs_to_filtered = False
            for filtered_contour in filtered_contours:
                for point in contour:
                    point = np.float32(point[0])  # Convert the point coordinates to float32
                    if cv2.pointPolygonTest(filtered_contour, tuple(point), False) >= 0:
                        belongs_to_filtered = True
                        break
                if belongs_to_filtered:
                    break

            # Add the contour to the filtered list if it meets the area threshold and doesn't belong to any other filtered contour
            if not belongs_to_filtered:
                filtered_contours.append(contour)

    return filtered_contours


def draw_paragraph(dilated_sheet, sheet, min_area):
    sheet_copy = sheet.copy()

    # Find contours and draw rectangle
    contours = cv2.findContours(dilated_sheet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    contours = filter_contours(contours, min_area)

    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(sheet_copy, (x, y), (x + w, y + h), (1, 156, 255), 2)

    return sheet_copy, contours
