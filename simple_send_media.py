#!/usr/bin/env python3

import argparse
import configparser
import telepot

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True, help="text file containing various parameters used across petcam scripts")
ap.add_argument("-v", "--video", required=True, help="video file to send via telegram to recipients")
args = vars(ap.parse_args())

vid_path = args['video']

config = configparser.ConfigParser()
config.read(args['config'])

token = config['telebot']['token']
recipients = config['telebot']['recipients'].split(",")

bot = telepot.Bot(token)
for recipient in recipients:
    with open (vid_path, 'rb') as video:
        bot.sendVideo(recipient, video, caption = vid_path)

