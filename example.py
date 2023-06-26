import numpy as np
import cv2
import matplotlib.pyplot as plt


def apply_threshold(img_array, threshold):
    threshold_applied = []
    for row in img_array:
        threshold_applied.append([])
        for pixel in row:
            if pixel > threshold:
                threshold_applied[len(threshold_applied) -
                                  1].append([255, 255, 255])
            else:
                threshold_applied[len(threshold_applied)-1].append([0, 0, 0])
    new_img = np.array(threshold_applied, np.uint8)
    cv2.imwrite(str(threshold)+".jpg", new_img)


img = cv2.imread("img/assPai.jpg", 0)
apply_threshold(img, 210)
