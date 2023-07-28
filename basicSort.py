# Crops and sorts images by blurriness and number of white pixels
# Written by Alex Garrett May 2023


import cv2, glob, os
import numpy as np


def isBlurry(img):
    # calculate laplacian variance
    lap = cv2.Laplacian(img, cv2.CV_64F).var()

    return lap

def isEmpty(gray):
    # Apply binary thresholding to extract the snowflake
    _, threshold_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Find contours in the threshold image
    contours, _ = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    try:
        # Find the contour with the largest area (assumed to be the snowflake)
        largest_contour = max(contours, key=cv2.contourArea)

    except:
        return 0
    # Calculate the size of the snowflake
    size = cv2.contourArea(largest_contour)/gray.size

    return size

def process(imgpaths):
    ''' Processes all images in masc folder and added their sharpness and size values'''
    valid = []
    for image in imgpaths:
        try:
            img = cv2.imread(image[0])

            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            image.append(-1)
            image.append(-1)
            continue
        
        blurThresh =  isBlurry(gray)
        emptyThresh = isEmpty(gray)

        if emptyThresh == 0:
            image.append(0)            
            image.append(0)
            continue

        image.append(blurThresh)
        image.append(emptyThresh)

        valid.append(image)

    return valid

def check(image):
    '''Gets sharpness and size values for one image'''
    try:
        img = cv2.imread(image[0])

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        image.append(-1)
        image.append(-1)
        return image
    
    blurThresh =  isBlurry(gray)
    emptyThresh = isEmpty(gray)
    
    image.append(blurThresh)
    image.append(emptyThresh)
    return image
    
    








