import cv2
import numpy as np
from skimage.feature import hog

class Classifier:

    def __init__(self):
        print('[+] initalised classifier instance')

    def extract_hog_fd(self, img_path, resize_shape):
        """Loads an image from path img_path, applies some pre-processing including resizing to shape resize_shape, and returns its HOG feature descriptor."""

        # load image
        img = cv2.imread(img_path)

        # make it grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # resize to desired dimensions 
        img = cv2.resize(img, resize_shape)

        # extract HOG feature descriptor
        hog_fd = hog(img, orientations = 9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys')

        return hog_fd 

    def classify_image(self, model, img_path, resize_shape):
        "Takes a sklearn-trained model and uses it to classify the image located at img_path; note that pre-processing requires resizing to resize_shape."
        
        # get HOG feature vector
        hog_fd = self.extract_hog_fd(img_path, resize_shape)
        
        # get prediction from model
        result =  model.predict(hog_fd.reshape(1, -1))

        return str(result[0])
