import cv2
import numpy as np
import pickle
from skimage.feature import hog

class Classifier:

    def __init__(self, model_path):
        print('[+] initialised classifier instance')
        self.model = self.load_model(model_path)
        self.classes = self.model.classes_

    def extract_hog_fd(self, img_path, resize_shape):
        """Loads an image from path img_path, applies some pre-processing including resizing to shape resize_shape, and returns its HOG feature descriptor."""
        
        print('[+] extracting HOG feature descriptor')

        # load image
        img = cv2.imread(img_path)

        # make it grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # resize to desired dimensions 
        img = cv2.resize(img, resize_shape)

        # extract HOG feature descriptor
        hog_fd = hog(img, orientations = 9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys')

        return hog_fd 

    def classify_image(self, img_path, resize_shape):
        "Takes a sklearn-trained model and uses it to classify the image located at img_path; note that pre-processing requires resizing to resize_shape."
        
        print('[+] preparing to classify image: ' + img_path)

        # get HOG feature vector
        hog_fd = self.extract_hog_fd(img_path, resize_shape)
        
        # get prediction from model
        result =  str(self.model.predict(hog_fd.reshape(1, -1))[0])
        print('[+] classification result: ' + result)
        return result

    def load_model(self, model_path):
        print('[+] loading classifier model: ' + model_path)
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
            return model
