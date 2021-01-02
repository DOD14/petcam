import argparse
import configparser

from classifier import Classifier
from petcam import Petcam
from telebot import Telebot
from timelapser import Timelapser
from tracker import Tracker

def snap_check_update():        
   
    # snap photo with timestamp
    filename =  petcam.snap(timelapser.get_last_timestamp(), 
            timelapser.light_outside())
   
    # classify image
    result = classifier.classify_image(img_path=filename, 
            resize_shape=(int(config['classifier']['resize_shape_h']), 
               int(config['classifier']['resize_shape_w'])
                )
            )
    
    # update our records of what was spotted when
    # and notify recipients if there has been a state change
    message = tracker.check_state_change(result, timelapser.last_datetime)
    if message != None:
        telebot.update_recipients(img_path=filename, message=message)

# use argparse to get the config file
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True, help="text file containing various parameters used across petcam scripts")
args = vars(ap.parse_args())

# get the rest of our settings from the config file
config = configparser.ConfigParser()
config.read(args['config'])

# instantiate helper classes
classifier = Classifier(model_path = config['classifier']['model_path'])

petcam = Petcam(save_dir = config['petcam']['save_dir'],
        day_snap_cmd = config['petcam']['day_snap_cmd'], 
        night_snap_cmd = config['petcam']['night_snap_cmd'],
        brightness_threshold = float(config['petcam']['brightness_threshold']),
        brighten_factor = float(config['petcam']['brighten_factor'])
        )

timelapser = Timelapser(city = config['timelapse']['city'],
        sleep_interval = config['timelapse']['sleep'])

tracker = Tracker(classes = classifier.classes)

# the bot needs to keep track of everything to be useful
telebot = Telebot(token = config['telebot']['token'], 
        recipients = config['telebot']['recipients'].split(","),
        classifier = classifier,
        petcam = petcam,
        timelapser = timelapser,
        tracker = tracker)

# enter main loop
timelapser.loop(snap_check_update)

