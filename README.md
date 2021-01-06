# petcam
A collection of python scripts that use the Raspberry Pi Camera and Telegram Messenger to keep an eye on your pet - or anything else you wish to track using image classification, timelapses, video, and motion detection. Originally a script I threw together to notify me when my tramp of a cat showed up, this is growing into a more feature-rich project, but the name has stayed.

## Table of Contents
* [Summary of Features](#summary-of-features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Configuration](#configuration)
* [Training the classifier](#training-the-classifier)

## Summary of Features
Before launching the main script, you train a custom linear regression model on a collection of images (see [Training the classifier](#training-the-classifier). For me that means gathering some photos of my cat's basket when it is occupied or empty. The trained model then has two classes: 'cat' and 'empty'.

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
Edit [config.txt](config.txt) to suit your setup.

Petcam relies on several helper classes you can tweak:

* **classifier**

  ```dataset```: The folder in which you keep manually classified images from which the classifier can learn. See [Training the classifier](#training-the-classifier).
  
  ```model_path```: The path to which the trained model is saved; the model is loaded from the same path for classification and tracking.
  
  ```resize_shape```: The height,width to which images are resized for model training and classification. Useful if your dataset contains images of multiple resolutions.
  
* **petcam**
  ```save_dir```: The folder to which all snapshots are saved.
  
  ```resolution```, ```iso```, ```shutter_speed```, ```awb_mode```: These are better explained in the [PiCamera documentation](https://picamera.readthedocs.io/en/release-1.13/api_camera.html). The defaults are optimised for my v1 camera in low light. Note that these settings are only applied in 'night' mode. 
  
  ```brightness_threshold```: Images with an average pixel value below this will be brightened up by a factor ```brighten_factor```.
  
* **telebot**

  ```token```: Your Telegram bot token (see [Get a token](https://telepot.readthedocs.io/en/latest/#get-a-token)).
  
  ```recipients```: The ids of Telegram users with which the bot is allowed to communicate. If you don't know where to get the ids, try [this](https://social.techjunkie.com/telegram-find-user-id/). Alternatively  start up petcam with a dummy id, send your bot a message and watch it freak out about 'sender unknown' as it dumps all info.
  
* **timelapser**

  ```city```: Any city in your timezone will do. We need this to know when to use night mode.
  
  ```sleep_interval```: The number of seconds to wait between iterations of the photo snapping loop. Actual interval will be longer because it takes time to take photos and classify them.
  
  
## Training the classifier
Inside the ```dataset``` folder you specified, you should have a folder with images for each class you wish to identify. The folder name becomes the class name during training. 
```
dataset -- cat
            |-- photo1.jpg
            |-- photo2.jpg
            |-- cat.jpg
            
        -- empty
            |-- photo1.jpg
            |-- empty.jpg
```

Then train the model specifying your config file:

``` python3 petcam/train_model.py -c config.txt```
