import argparse
import configparser
from time import sleep

from petcam.classifier import Classifier
from petcam.looper import Looper
from petcam.motion_manager import MotionManager
from petcam.petcam import Petcam
from petcam.sundial import Sundial
from petcam.telebot import Telebot
from petcam.tracker import Tracker

# use argparse to get the config file
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True, help="text file containing various parameters used across petcam scripts")
args = vars(ap.parse_args())

# get the rest of our settings from the config file
config = configparser.ConfigParser()
config.read(args['config'])

# instantiate helper classes

classifier = Classifier(model_path = config['classifier']['model_path'],
        resize_shape = tuple([int(x) for x in config['classifier']['resize_shape'].split(",")]),
        )
petcam = Petcam(img_save_dir = config['petcam']['img_save_dir'],
        vid_save_dir = config['petcam']['vid_save_dir'],
        resolution = tuple([int(x) for x in config['petcam']['resolution'].split(",")]),
        fps = int(config['petcam']['fps']),
        iso = int(config['petcam']['iso']),
        shutter_speed = int(config['petcam']['shutter_speed']),
        awb_mode = config['petcam']['awb_mode'],
        brightness_threshold = float(config['petcam']['brightness_threshold']),
        brighten_factor = float(config['petcam']['brighten_factor'])
        )
sundial = Sundial(city = config['sundial']['city'])
looper = Looper(
        sleep_interval = config['looper']['sleep_interval'],
        sundial = sundial
        )
tracker = Tracker(classes = classifier.classes)
motion_manager = MotionManager(
        motion_conf_dir = config['motion']['motion_conf_dir'],
        motion_save_dir = config['motion']['motion_save_dir']
        )
telebot = Telebot(token = config['telebot']['token'], 
        recipients = config['telebot']['recipients'].split(","),
        helpers = {'classifier': classifier,
            'petcam': petcam,
            'motion_manager': motion_manager,
            'looper': looper,
            'tracker': tracker,
            'sundial': sundial
            }
        )

# telebot will handle everything, just keep it alive
while True:
    sleep(10) 
