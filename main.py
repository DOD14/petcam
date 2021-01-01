import argparse
import configparser

from classifier import Classifier
from petcam import Petcam
from telebot import Telebot
from timelapser import Timelapser
from tracker import Tracker

def snap_check_update():        
   
    # snap photo with timestamp
    filename =  petcam.snap(timelapser.get_last_timestamp())
   
    # classify image
    result = classifier.classify_image(img_path=filename, resize_shape=(config['classifier']['resize_shape_h'], config['classifier']['resize_shape_w']))
    
    # update our records of what was spotted when
    # and notify recipients if there has been a state change
    if tracker.check_state_change(result):
        message = "[!] update: " + tracker.last_result + " -> " + result
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
        night_snap_cmd = config['petcam']['night_snap_cmd'])

timelapser = Timelapser(city = config['timelapse']['city'])

tracker = Tracker(classes = classifier.classes)

# the bot needs to keep track of everything to be useful
telebot = Telebot(token = config['telebot']['token'], 
        recipients = config['telebot']['recipients'].split(","),
        classifier = classifier,
        petcam = petcam,
        timelapser = timelaper,
        tracker = tracker)

# enter main loop
timelapser.loop(snap_check_update)

