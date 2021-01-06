# petcam
A collection of python scripts that use the Raspberry Pi Camera and Telegram Messenger to keep an eye on your pet - or anything else you wish to track using image classification, timelapses, video, and motion detection. Originally a script I threw together to notify me when my tramp of a cat showed up, this is growing into a more feature-rich project, but the name has stayed.

## Table of Contents
* [Summary of Features](#summary-of-features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Configuration](#configuration)
* [Training the classifier](#training-the-classifier)

## Summary of Features
Before taking advantage of any features, you train a custom linear regression model on images of several states. For me that means gathering some photos of my cat's basket when it is occupied or empty. The trained model then has two classes: 'cat' and 'empty'.

When all runs smoothly, you interact with the module through a Telegram bot and can issue the following commands:

* **tracking**:

  ```/loop```: Start a loop that takes photos at an interval, classifies each photo based on the model you trained, and messages you when a change in state has ocurred. In my case, when the cat arrives home I get the message 'empty -> cat', and when he leaves, 'cat -> empty'.

  ```/update```: Lets you know which state was most recently seen and when: 'cat spotted at 19:38:52'

  ```/lastseen [state]```: You explicitly ask when a state was last seen: 'last saw cat at 15:01:20'
  
  ```/lastsnap```: Shows you the latest taken photo.

  ```/stop```: Stops running the loop.
  
* **photos**:

  ```/photo```: Takes a photo and sends it to you.


  ```/browse```: Browse photos taken so far by filename.

  ```/show [pic.jpg]```: Sends you the photo you specified by filename.
  
* **information**

  ```/classes```: Lists the classes of the trained model.
  
  ```/help```: Sends a ReplyKeyboardMarkup so that you conveniently get all commands as buttons.
  
  ```/debug```: Dumps info about important objects.
  
  
* **quitting**

  ```/exitscript```: Kills the process associated with running the scripts.

  ```/shutdown```: Shuts down the Raspberry Pi by issuing 'sudo shutdown now'


## Requirements
I use Python 3.7.3 on a Raspberry Pi Zero W with Raspberry Pi Camera v1. See also [requirements.txt](petcam/requirements.txt).

```pip3 install astral opencv-python picamera pillow scikit-image scikit-learn telepot```

## Installation
Just clone the repository:

```git clone --depth 1 https://github.com/DOD14/petcam.git```

## Configuration

