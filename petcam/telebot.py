import atexit
import os, signal
from pathlib import Path
import telepot, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup
from time import sleep
import threading

class Telebot:

    def __init__(self, token, recipients, helpers):
        print('[+][telebot] initialised telebot instance')
       
        # initialise a Telegram bot with given token
        self.bot = telepot.Bot(token)

        # we will only accept messages from the given ids
        self.recipients = recipients
        print('[i] accepting messages from ids: ' + ", ".join(self.recipients))
       
        # get a handle on helper classes 
        self.helpers = helpers

        # each command keyword corresponds to a function
        self.cmd_dict = { 
                "/browse": self.browse_snaps,
                "/classes": self.list_classes,
                "/debug": self.dump_info,
                "/exitscript": self.exit_script,
                "/help": self.default_reply,
                "/lapse": self.send_video_lapse,
                "/lastseen": self.report_last_seen,
                "/lastsnap": self.send_last_snap,
                "/photo": self.snap_and_send,
                "/show": self.show_img,
                "/shutdown": self.shutdown_now,
                "/startloop": self.start_looper,
                "/stoploop": self.stop_looper_loop,
                "/update": self.status_update
                }
        
        # construct a custom keyboard from our list of commands
        # then the user just has to press  buttons
        
        cmds = sorted(self.cmd_dict.keys())
        print('[debug] len: ' + str(len(cmds)))
        print('[debug] cmds: ' + str(cmds))

        left_col = cmds[:len(cmds)//2]
        right_col = cmds[len(cmds)//2:]
        buttons = [[KeyboardButton(text=left),
                    KeyboardButton(text=right)
                ] for left, right in zip(left_col, right_col)]
        self.keyboard = ReplyKeyboardMarkup(keyboard=buttons)
        
        # let everyone now bot is up and running
        msg = '[+] bot activated! use /startloop to begin tracking or /help for a list of available commands'
        self.update_recipients(message=msg, reply_markup=self.keyboard)
        
        atexit.register(self.exit_forced)

        # start listening for incoming messages
        telepot.loop.MessageLoop(self.bot, self.on_chat_message).run_as_thread(relax=2)
        
    def browse_snaps(self, chat_id):
        """Browse snapshots taken so far in current script run by name."""

        # construct inline keyboard based on snapshot filenames
        try:
            buttons = [[KeyboardButton(text='/show ' + name)] for name in self.helpers['petcam'].snaps]
            keyboard = ReplyKeyboardMarkup(keyboard = buttons)
            
            # present user with keyboard
            msg = '[+] pick a snapshot to view'
            self.bot.sendMessage(chat_id, msg, reply_markup = keyboard)
        
        # if no snapshots taken yet 
        except Exception as err:
            print(err)
            msg = '[i] no snapshots yet, use /photo to take one or start the photo /loop' 
            self.bot.sendMessage(chat_id, msg)
   

    def default_reply(self, chat_id):
        """Message user with fallback reply if command not recognised or they explicitly ask for /help."""

        # if command is not recognised
        # send custom keyboard with examples of available commands
        self.bot.sendMessage(chat_id, "[i] available commands:",
            reply_markup=self.keyboard)
    
        
    def exit_script(self, chat_id):
        """Kills current process after notifying all recipients."""

        # tell eveyone we're going offline
        msg = '[+] exiting script... bye!'
        self.update_recipients(message=msg)
        
        # mark last message as read to avoid death loop
        # where bot keeps reading /exitscript on startup
        self.bot.getUpdates()
        sleep(5)

        # finally kill process
        os.kill(os.getpid(), signal.SIGTERM)

   
    def exit_forced(self):
        """Method registered with atexit, notifies users of script exit and sends default keyboard."""
        msg = '[!] exiting immediately because of an error'
        self.update_recipients(message=msg, reply_markup = self.keyboard)


    def on_chat_message(self, msg):
        """Contains all logic for how incoming Telegram messages should be handled."""

        # print basic information about the sender
        sender_id = str(msg['from']['id'])
        sender_name = msg['from']['first_name']
        print('[+][telebot] handling message from ' + sender_id + " (" + sender_name + ")")
        
        # ignore unknown senders
        if sender_id not in self.recipients:
            print('[!] sender unknown, dumping message' + "\n" + str(msg))
            return

        print('[+][telebot] message accepted')

        # get information about message type and decide on a reply
        content_type, chat_type, chat_id = telepot.glance(msg)
        try:    
            text = msg['text']
            print('[+][telebot] received text: ' + text)
            
            # the first word in the received message should be a command
            text = text.split(" ")
            command = text[0]
            print('[+][telebot] command: ' + command)

            try:
                # single-word commands only need to know the chat_id to reply to
                if len(text) == 1:
                    self.cmd_dict[command](chat_id)
                
                # many-word commands also contain parameters to be passed on to the command function    
                else:
                    print('[+][telebot] command args: '+ str(text[1:]))
                    self.cmd_dict[command](chat_id, *text[1:])

            except TypeError as err:
                print(err)
                msg = '[!] invalid number of arguments provided'
                self.bot.sendMessage(chat_id, msg)
            except KeyError as err:
                #if we don't recognise the command, provide a default reply
                print(err)
                self.cmd_dict['/help'](chat_id)
        except Exception as err:
            print(err)
            msg = '[!] an error occurred while processing command'
            self.bot.sendMessage(chat_id, msg)

    def show_img(self, chat_id, img_path):
        """Loads image with given filename and sends it."""
        
        # if no snapshots yet notify user
        if len(self.helpers['petcam'].snaps) == 0:
            msg = '[i] no snapshots yet, use /photo to take one or start the photo /loop' 
            self.bot.sendMessage(chat_id, msg)
            return

        try:
            print('[+][telebot] showing image: ' + img_path)
            
            # open image and send
            with open(img_path, 'rb') as img:
                self.bot.sendPhoto(chat_id, img, caption="[i]" + img_path, reply_markup = self.keyboard)

        except FileNotFoundError as err:
            print(err)
            msg = '[!] invalid filename, please use /browse to see available snapshots'
            self.bot.sendMessage(chat_id, msg)
        

    def send_last_snap(self, chat_id):
        """Retrieves and sends the latest snapshot."""

        try:
            # get latest snapshot filename
            filename = self.helpers['petcam'].last_snap
            # open image and send
            with open(filename, 'rb') as img:
                msg = '[i] ' + str(filename)
                self.bot.sendPhoto(chat_id, img, caption=msg)

        except Exception as err:
            print(err)
            msg = '[i] no photos taken yet, please try again later or request a new /photo'
            self.bot.sendMessage(chat_id, msg)
    
    def send_video_lapse(self, chat_id):
        """Produces a timelapse video from all snapshots and sends it."""
        
        # get video path, open, send
        vid_path = self.helpers['petcam'].snaps_to_video()
        with open (vid_path, 'rb') as video:
            self.bot.sendVideo(chat_id, video, caption = vid_path)
         

    def shutdown_now(self, chat_id):
        """Shuts down device immediately."""
        
        # let everyone know
        msg = '[+] shutting down... bye!'
        self.update_recipients(message=msg)

        # mark last message as read to prevent death loop
        self.bot.getUpdates()
        sleep(5)

        # issue shutdown command
        os.system('sudo nohup shutdown now')

    
    def snap_check_update(self):
        """Take photo, classify it, notify user of changes.""" 
        
        # this will be used to determine sun position and timestamp
        current_datetime = self.helpers['looper'].last_datetime
        name = current_datetime.strftime("%d-%m-%y+%H:%M:%S") + ".jpg"
        
        # snap photo
        img_path =  self.helpers['petcam'].snap(
                name = name,
                light_outside = self.helpers['sundial'].light_outside(),
                )

        # classify image
        result = self.helpers['classifier'].classify_image(img_path=filename)

        # update our records of what was spotted when
        # and notify recipients if there has been a state change
        message = self.helpers['tracker'].check_state_change(result, current_datetime)
        try:
            telebot.update_recipients(img_path=filename, message=message)
        except Exception as err:
            print(err)
            print('[+] no change')


    def update_recipients(self, message='[!] message empty error', img_path=None, reply_markup = None):
        """Send a message (optionally an image) to every recipient in turn."""
        print('[+][telebot] preparing to send message to all recipients:')
        print(message)

        # loop over recipients
        for rec in self.recipients:
            print("[+][telebot] updating " + rec)
            
            # if no image path was supplied just text the user
            if img_path is None:
                self.bot.sendMessage(rec, message, reply_markup = reply_markup)
            # if an image path is supplied, load the image and send
            # yes we need to open the image for each sendd - known issue
            else:
                with open(img_path, 'rb') as image:
                    self.bot.sendPhoto(rec, image, caption=message, reply_markup = reply_markup)


    def status_update(self, chat_id):
        """Messages information about the latest snapshot."""

        try: 
            reply = "[i] last status: " + self.helpers['tracker'].last_state + " at " + self.helpers['looper'].last_datetime.strftime("%H:%M:%S")
        except AttributeError as err:
            print(err)
            reply = "[i] loop not yet started, use /startloop" 
        
        self.bot.sendMessage(chat_id, reply)

    def snap_and_send(self, chat_id):
        """Sends a photo on demand."""
        self.bot.sendMessage(chat_id, "[i] taking photo")
        name = self.helpers['sundial'].now().strftime("%d-%m-%y+%H:%M:%S") + ".jpg" 
        
        # timestamp is now rather than latest to avoid overwrites
        filename = self.helpers['petcam'].snap(
                name = name,
                light_outside = self.helpers['sundial'].light_outside()
                )

        # open image and send
        with open(filename, 'rb') as image:
            self.bot.sendPhoto(chat_id, image, caption = filename)
        
        print('[+] sent photo')

    def report_last_seen(self, chat_id, state="dummy"):
        """When was a state last seen? usage: /lastseen state"""
        
        # defualt is to send standard command keyboard
        keyboard = self.keyboard

        try:
            # find out from tracker when a state was last spotted 
            lastseen_datetime = self.helpers['tracker'].last_seen[state]
            
            # could be unknown if we've just started
            if lastseen_datetime == "unknown":
                reply = "[i] not yet seen, please try again later"
            
            # construct reply saying when the state was last seen
            else:
                reply = "[i] last saw " + state + " at " + lastseen_datetime.strftime("%H:%M:%S")
        
        except KeyError:
            reply = "[!] invalid class provided"

            # construct override keyboard with available classes
            buttons = [[KeyboardButton(text='/lastseen ' + state)] for state in self.helpers['classifier'].classes]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons)
        
        # send the appropriate reply
        self.bot.sendMessage(chat_id, reply, reply_markup=keyboard)


    def list_classes(self, chat_id):
        """Messages user with a list of classifier classes."""

        message = "[i] available classes for use with /lastseen command: " + ", ".join(self.helpers['classifier'].classes)
        self.bot.sendMessage(chat_id, message)


    def dump_info(self, chat_id):
        """Debug: dumps the __dict__ of every helper class."""

        message = str(self.__dict__)
        for helper in [value for value in self.helpers.values()]: 
             message += "\n" + str(helper.__dict__)

        self.bot.sendMessage(chat_id, message)

    def start_looper(self, chat_id):
        """Start looper loop."""
        if self.helpers['looper'].loop_running:
            msg = '[!] loop already running'
            self.bot.sendMessage(chat_id, msg)
        else: 
            msg = '[+] starting main loop'
            threading.Thread(target=self.helpers['looper'].loop(self.snap_check_update)).start()
            self.update_recipients(message=msg)
    
    def stop_looper_loop(self, chat_id):
        """Stop looper loop."""
        if self.helpers['looper'].loop_running:
            msg = '[+] stopping main loop'
            self.helpers['looper'].loop_running = False
            self.update_recipients(message=msg)
        else: 
            msg = '[!] loop is not running'
            self.bot.sendMessage(chat_id, msg)

