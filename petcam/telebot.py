from pathlib import Path
import telepot, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup
import threading

class Telebot:

    def __init__(self, token, recipients, helpers):
        print('\t[+] initialised telebot instance')
       
        # initialise a Telegram bot with given token
        self.bot = telepot.Bot(token)

        # we will only accept messages from the given ids
        self.recipients = recipients
        print('\t[i] accepting messages from ids: ' + ", ".join(self.recipients))
       
        # get a handle on helper classes 
        self.helpers = helpers

        # each command keyword corresponds to a function
        self.cmd_dict = { 
                "/browse": self.browse_snaps,
                "/classes": self.list_classes,
                "/debug": self.dump_info,
                "/help": self.default_reply,
                "/lastseen": self.report_last_seen,
                "/lastsnap": self.send_last_snap,
                "/loop": self.toggle_timelapser_loop,
                "/photo": self.snap_and_send,
                "/show": self.show_img,
                "/shutdown": self.shutdown_now,
                "/stop": self.toggle_timelapser_loop,
                "/update": self.status_update
                }
        
        # construct a custom keyboard from our list of commands
        # then the user just has to press  buttons
        buttons = [[KeyboardButton(text=cmd)] for cmd in self.cmd_dict.keys()]
        self.keyboard = ReplyKeyboardMarkup(keyboard=buttons)
        
        # let everyone now bot is up and running
        msg = '[+] bot activated! use /loop to begin tracking'
        self.update_recipients(message=msg)

        # start listening for incoming messages
        telepot.loop.MessageLoop(self.bot, self.on_chat_message).run_as_thread()
        
    
    def show_img(self, chat_id, name):
        img_path = self.helpers['petcam'].save_dir + "/" + name
        print('[+] showing image: ' + img_path)

        with open(img_path, 'rb') as img:
            self.bot.sendPhoto(chat_id, img, caption=name, reply_markup = self.keyboard)
        

    def browse_snaps(self, chat_id):
        """Browse snapshots taken so far in current script run by name."""
        # TODO: isolate current 'current run' snapshots from other files in folder
        # potential security risk since user can ask for any photo
        
        # construct inline keyboard based on snapshot filenames
        snaps_dir = self.helpers['petcam'].save_dir
        filenames = [snap.name for snap in Path(snaps_dir).iterdir() if snap.is_file()]
        buttons = [[KeyboardButton(text='/show ' + name)] for name in filenames]
        keyboard = ReplyKeyboardMarkup(keyboard = buttons)
        
        # present the user with keyboard
        msg = '[+] pick a snapshot to view'
        self.bot.sendMessage(chat_id, msg, reply_markup = keyboard)


    def default_reply(self, chat_id):
        """Message user with fallback reply if command not recognised or they explicitly ask for /help."""

        # if command is not recognised
        # send custom keyboard with examples of available commands
        self.bot.sendMessage(chat_id, "[i] available commands:",
            reply_markup=self.keyboard)


    def on_chat_message(self, msg):
        """Contains all logic for how incoming Telegram messages should be handled."""

        # print basic information about the sender
        sender_id = str(msg['from']['id'])
        sender_name = msg['from']['first_name']
        print('\t[+] handling message from ' + sender_id + " (" + sender_name + ")")
        
        # ignore unknown senders
        if sender_id not in self.recipients:
            print('\t[!] sender unknown, dumping message' + "\n" + str(msg))
            return

        print('\t[+] message accepted')

        # get information about message type and decide on a reply
        content_type, chat_type, chat_id = telepot.glance(msg)
        if(content_type=='text'):
            text = msg['text']
            print('\t[+] received text: ' + text)
            
            # the first word in the received message should be a command
            text = text.split(" ")
            command = text[0]
            print('\t\t[+] command: ' + command)

            # but if we don't recognise the command, provide a default reply
            if not command in self.cmd_dict:
                self.cmd_dict['/help'](chat_id)
                return
            
            # single-word commands only need to know the chat_id to reply to
            if len(text) == 1:
                self.cmd_dict[command](chat_id)
            
            # many-word commands also contain parameters to be passed on to the command function    
            else:
                print('[+] command args: '+ str(text[1:]))
                self.cmd_dict[command](chat_id, *text[1:])
   

    def send_last_snap(self, chat_id):
        """Retrieves and sends the latest snapshot."""

        # get latest snapshot filename
        filename = self.helpers['petcam'].last_snap
        
        # could be None if we've just started
        if filename == None:
            msg = '[i] no photos taken yet, please try again later or request a new /photo'
            self.bot.sendMessage(chat_id, msg)
            return

        # open iamge and send
        with open(filename, 'rb') as img:
            msg = '[i] ' + str(filename)
            self.bot.sendPhoto(chat_id, img, caption=msg)
    

    def shutdown_now(self, chat_id):
        """Shuts down device immediately."""
        msg = '[+] shutting down... bye!'
        self.update_recipients(message=msg)
        os.system('sudo shutdown now')

    def update_recipients(self, message='[!] message empty error', img_path=''):
        """Send a message (optionally an image) to every recipient in turn."""
        print('\t[+] preparing to send message to all recipients:')
        print("\t" + message)

        # loop over recipients
        for rec in self.recipients:
            print("\t\t[+] updating " + rec)
            
            # if no image path was supplied just text the user
            if img_path == '':
                self.bot.sendMessage(rec, message)
            
            # if an image path is supplied, load the image and send
            # yes we need to open the image for each sendd - known issue
            else:
                with open(img_path, 'rb') as image:
                    self.bot.sendPhoto(rec, image, caption=message)


    def status_update(self, chat_id):
        """Messages information about the latest snapshot."""

        reply = "[i] last status: " + self.helpers['tracker'].last_state + " at " + self.helpers['timelapser'].last_datetime.strftime("%H:%M:%S")
        self.bot.sendMessage(chat_id, reply)

    def snap_and_send(self, chat_id):
        """Sends a photo on demand."""
        self.bot.sendMessage(chat_id, "[i] taking photo")

        # timestamp is now rather than latest to avoid overwrites
        filename = self.helpers['petcam'].snap(self.helpers['timelapser'].now(), self.helpers['timelapser'].light_outside())

        # open image and send
        with open(filename, 'rb') as image:
            self.bot.sendPhoto(chat_id, image)

    def report_last_seen(self, chat_id, state="dummy"):
        """When was a state last seen? usage: /lastseen state"""
        
        try:
            # find out from tracker when a state was last spotted 
            lastseen_datetime = self.helpers['tracker'].last_seen[state]
            
            # could be unknown if we've just started
            if lastseen_datetime == "unknown":
                reply = "[i] not yet seen, please try again later"
            
            # construct reply saying when the state was last seen
            else:
                reply = "[i] last saw " + state + " at " + lastseen_datetime.strftime("%H:%M:%S")
        
        # this can happen if the class is not in tracker's dict
        except KeyError:
            reply = "[!] invalid class provided, please use /classes to see available classes"
        
        # send the appropriate reply
        self.bot.sendMessage(chat_id, reply)


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

    def toggle_timelapser_loop(self, chat_id):
        """Start/stop timelapser loop."""
        if self.helpers['timelapser'].loop_running:
            msg = '[+] stopping main loop'
            self.helpers['timelapser'].loop_running = False
        else: 
            msg = '[+] starting main loop'
            threading.Thread(target=self.helpers['timelapser'].loop).start()

        self.update_recipients(message=msg)

