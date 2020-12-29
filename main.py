import argparse
import astral, astral.geocoder, astral.sun
import cv2
from datetime import datetime
import numpy 
import os
import pickle
import pytz
from skimage.feature import hog
import telepot, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup
from time import sleep

from classifier import Classifier

def now():
    return datetime.now(pytz.timezone(city.timezone))

def snap():
    # construct filename
    timestamp = str(now_datetime).replace(" ", "-")
    filename = "photos/"+timestamp+".jpg"
   
    # wait for camera to become available
    global camera_in_use
    while camera_in_use:
        sleep(1)
    camera_in_use = True
    
    # decide whether it's day or night and use appropriate raspistill settings
    if now_datetime > sunrise and now_datetime < sunset:
        print('[+] taking normal picture: ' + filename)
        pic_command = "raspistill -w 256 -h 256 -o " + filename
    else:
        print('[+] taking long-exposure picture: ' + filename)
        pic_command = "raspistill -w 256 -h 256 -ss 100000000 -o " + filename
    print('[debug] passing command: ' + pic_command)
    os.system(pic_command)
    print('[debug] execution finished')

    # release camera
    camera_in_use = False

    # brighten up the image even more
    convert_command = "convert -brightness-contrast 70x70 " + filename+ " " + filename
    print('[debug] passing command: ' + convert_command)
    os.system(convert_command)

    # return a handle on the new image
    return filename

# tell bot how to handle user messages
def handle(msg):
    sender = str(msg['from']['id'])
    print('[+] handling telegram message from ' + sender + " (first name: " + msg['from']['first_name'] + ")")

    # ignore if not on whitelist 
    if sender in recipients: 
        print("[+] message accepted")

        # get basic information about the message and decide on a reply
        content_type, chat_type, chat_id = telepot.glance(msg)
        if(content_type=='text'):
            command = msg['text']
            print("[+] received message: " + command)
            
            # information about the latest snapshot
            if command == "/update":
                reply = "[i] last status: " + last_result + " at " + now_datetime.strftime("%H:%M:%S")
                bot.sendMessage(chat_id, reply)
            
            # photo on demand
            elif command == "/photo":
                if camera_in_use:
                    bot.sendMessage(chat_id, "[!] camera in use, please wait a few seconds")
                    while camera_in_use:
                        sleep(1)
                bot.sendMessage(chat_id, "[i] taking photo")
                filename = snap()
                with open(filename, 'rb') as image:
                    bot.sendPhoto(chat_id, image)
            
            # when was a state last seen? usage: /last state 
            elif command.startswith("/lastseen"):
                state  = command.split(" ")[1]
                result = last_seen[state]
                if result == "unknown":
                    reply = "[i] not yet seen, please try again later"
                elif type(result) == datetime:
                    reply = "[i] last saw " + state + " at " + result.strftime("%H:%M:%S")
                else: 
                    reply = "[!] invalid class provided, please use /classes to see available classes"
                bot.sendMessage(chat_id, reply)

            # list available classes
            elif command == "/classes":
                message = "[i] available classes for use with /last command: " + ", ".join(classes)
                bot.sendMessage(chat_id, message)

            # provide basic time/location info for this script run
            elif command == "/info":
                message = "[i] started script at " + started_datetime.strftime("%H:%M:%S")
                message += "\nlocation info: " + str(city)
                message += "\nsunrise time: " + sunrise.strftime("%H:%M:%S")
                message += "\nsunset time: " + sunset.strftime("%H:%M:%S")
                message +="\ninterval between snapshots: " + str(sleep_interval) + " seconds"
                bot.sendMessage(chat_id, message)

            # if command is not recognised
            # send custom keyboard with examples of available commands
            else:
                bot.sendMessage(chat_id, "[i] available commands:", 
                    reply_markup=ReplyKeyboardMarkup(
                                keyboard=[[
                                    KeyboardButton(text="/update"),
                                    KeyboardButton(text="/info"),
                                    KeyboardButton(text="/photo"),
                                    KeyboardButton(text="/classes"),
                                    KeyboardButton(text="/lastseen [class]")
                                    ]]
                            ))
    else:
        print('[!] sender not on whitelist, dumping message' + "\n" + str(msg))

# instantiate helper classes
classifier = Classifier()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--city", required=True, help="city for which sunrise/sunset times are considered")
ap.add_argument("-m", "--model", required=True, help="path to trained classifier model")
ap.add_argument("-s",  "--sleep", required=False, help="how long to sleep between snapshots", type = int, default = 300)
ap.add_argument("-t", "--token", required=True, help="telegram both auth token for sending messages")
ap.add_argument("-r", "--recipients", required=True, help="comma-separated list of telegram ids to message with updates")
args = vars(ap.parse_args())

# get location info for city
city = astral.geocoder.lookup(args['city'], astral.geocoder.database())

# commence
started_datetime = now()

# load the trained model
print("[+] loading classifier model")
with open(args["model"], 'rb') as file:
    model = pickle.load(file)
classes = model.classes_

# dummy state before first photo is classified
last_result = "unknown"
last_seen = {key:"unknown" for key in classes}
print("[debug] last_seen: " + str(last_seen))

# amount to sleep between snapshots
sleep_interval = args['sleep']

# avoid overlapping calls to raspistill
camera_in_use = False

# initialise telegram bot
bot = telepot.Bot(args['token'])
recipients = args['recipients'].split(",")
print("[+] starting telegram bot")
telepot.loop.MessageLoop(bot, handle).run_as_thread()
print('[i] accepting messages from ids: ' + ", ".join(recipients))

# this will run until killed
# one iteration = one day
while True:
    
    print('[+] starting main loop')
    # find out what day is today so we can get sunrise/sunset times 
    # and update these when the day has changed
    today_datetime = now() 
    today_day = today_datetime.day
    today_sun = astral.sun.sun(city.observer, date = today_datetime, tzinfo=city.timezone)
    sunrise = today_sun["sunrise"]
    sunset = today_sun["sunset"]
    print('[i] location: ' + str(city) + "\n[i] sunrise: " + str(sunrise) + "\n[i] sunset: " + str(sunset))

    # take photos with today's sunrise/sunset times
    now_datetime = now() 
    while now_datetime.day == today_day:
        
        # snap photo
        filename = snap()
       
        # classify image
        result = classifier.classify_image(model=model, img_path=filename, resize_shape=(256, 256))
        print("[i] classification result: " + result)
        
        # if there has been a state change, send a message
        if last_result != "unknown" and last_result != result:
            message = "[!] update: " + last_result + " -> " + result
            print("\"" + message + "\"")
            for rec in recipients:
                with open(filename, 'rb') as image:
                    print("[+] updating " + rec)
                    bot.sendPhoto(rec, image, caption=message)
        
        # update our records of what was spotted when
        last_result = result
        last_seen[result] = now_datetime

        # wait between photos
        print('[+] will now sleep ' + str(sleep_interval) + " seconds")
        sleep(sleep_interval)
        
        # update datetime for next photo
        now_datetime = now() 
        

