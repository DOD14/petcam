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

if 'media_handler' in config:
    from petcam.media_handler import MediaHandler
    helpers['media_handler'] = MediaHandler(img_save_dir = config['media_handler']['img_save_dir'],
            vid_save_dir = config['media_handler']['vid_save_dir'],
            mode = config['media_handler']['mode'],
            save_photos = config['media_handler'].getboolean('save_photos'),
            adjust_gamma = config['media_handler'].getboolean('adjust_gamma'),
            video_fps = int(config['media_handler']['fps']),
            resolution = tuple([int(x) for x in config['media_handler']['resolution'].split(",")])
    )

telebot = Telebot(token = config['telebot']['token'], 
        recipients = config['telebot']['recipients'].split(","),
        helpers = helpers
        )


# telebot will handle everything, just keep it alive
while True:
    sleep(10) 
