import argparse
import configparser
import importlib
from time import sleep
from petcam.telebot import Telebot

# use argparse to get the config file
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True, help="text file containing various parameters used across petcam scripts")
args = vars(ap.parse_args())

# get the rest of our settings from the config file
config = configparser.ConfigParser()
config.read(args['config'])


# instantiate helper classes
helpers = {}

if 'petcam' in config:
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
    helpers['petcam'] = petcam

if 'classifier' in config:
    classifier = Classifier(model_path = config['classifier']['model_path'],
        resize_shape = tuple([int(x) for x in config['classifier']['resize_shape'].split(",")]),
        )
    helpers['classifier'] = classifier


telebot = Telebot(token = config['telebot']['token'], 
        recipients = config['telebot']['recipients'].split(","),
        helpers = helpers
        )


# telebot will handle everything, just keep it alive
while True:
    sleep(10) 
