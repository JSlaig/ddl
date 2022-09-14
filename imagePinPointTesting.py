import cv2
import numpy as np

def testing():
    image = cv2.imread("img/img.png", 1)

    # Draw a red point
    image2 = cv2.circle(image, (300, 100), radius=8, color = (0, 255, 0), thickness=-1)

    cv2.imshow("Red Point on Black Image", image2)

    cv2.waitKey(0)
    cv2.destroyAllWindows()