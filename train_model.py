import configparser
import cv2
from pathlib import Path
import pickle
import numpy as np
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

# will import a function for convenience but this is unrelated to the trained model
from classifier import Classifier
classifier = Classifier()

# parse config file config.txt
config = configparser.ConfigParser()
config.read('config.txt')
print("[+] read config file")

# get the folders corresponding to the classes
folders = [directory for directory in Path(config['training']['dataset']).iterdir() if directory.is_dir()]
folders_len = len(folders)

# initialise lists
data = []
labels = []
classes = []

print("[+] preparing to process images")
# loop over the class folders
for i, direc in enumerate(folders):
    
    # this label applies to all images in this folder by design
    label = direc.name
    classes.append(label)
    
    # get a handle on the number of image paths so we can enumerate and show progress info
    image_paths = [img for img in direc.iterdir() if not img.name.startswith(".")]
    images_len = len(image_paths)
   
    # loop over the images in each class folder
    for j, imagePath in enumerate(image_paths):
       
        print('[progress] ' + label + " (" +str(i+1) + "/" + str(folders_len)+ "): " + str(j+1) + "/" + str(images_len), end="\r")
     
        # append HOG feature descriptor and image label to data
        hog_fd = classifier.extract_hog_fd(str(imagePath), (int(config['global']['resize_shape_h']), int(config['global']['resize_shape_w'])))
        data.append(hog_fd)
        labels.append(label)
    
    print("\n")

# encode the labels to integers
le = LabelEncoder()
labels = le.fit_transform(labels)

# split data into test/train sets
(trainData, testData, trainLabels, testLabels) = train_test_split(
	np.array(data), labels, test_size=0.25, random_state=147)

# train the classifier
print("[+] training  classifier")
model = LinearSVC()
model.fit(trainData, trainLabels)

# evaluate the classifier
print("[+] evaluating classifier")
predictions = model.predict(testData)
print(classification_report(testLabels, predictions,
        target_names=classes))

# retrain on all avilable data
print("[+] re-training on entire dataset")
model.fit(np.array(data), labels)

# evaluate the classifier
print("[+] evaluating classifier")
predictions = model.predict(data)
print(classification_report(labels, predictions,
	target_names=classes))

# replace int with string labels 
model.classes_ = np.array(classes)
print("[i] model classes: " + str(model.classes_))

# save the model with pickle
print("[+] saving model")
with open(config['training']['model_name'], 'wb') as file:
    pickle.dump(model, file)
