import atexit
import os, signal
from time import sleep

import emoji
import telepot, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

class Telebot:

    def __init__(self, token, recipients, helpers):
        print('[+][telebot] initialised telebot instance')
       
        # initialise a Telegram bot with given token
        self.bot = telepot.Bot(token)

        # we will only accept messages from the given ids
        self.recipients = recipients
        print('[i] accepting messages from ids: ' + ", ".join(self.recipients))
        
        # ensure cleanup function runs and notifies recipients if this crashes
        atexit.register(self.exit_script)
       
        # get a handle on helper classes and provide them with a reference to this telebot
        for helper in helpers.values():
            helper.register_telebot(self)
        self.helpers = helpers

        # get a list of commands from helpers to format as a keyboard with buttons
        self.construct_cmd_keyboard()
        
        # let everyone know bot is up and running
        msg = '[+] bot activated! use /startloop to begin tracking or /help for a list of available commands'
        self.update_recipients(message=msg, reply_markup=self.keyboard)
        
        # start listening for incoming messages
        telepot.loop.MessageLoop(self.bot, self.on_chat_message).run_as_thread(relax=2)
        

    def construct_cmd_keyboard(self):
 # construct a dictionary of the form 'command: [helper, emoji]' by asking each helper for their own list of custom commands and putting these together
        cmd_dict = {} 
        for helper in self.helpers.values():
            new_entries = helper.init_cmd_dict()
            print('[debug] new_entries: ' + str(new_entries))
            cmd_dict = {**cmd_dict, **new_entries}

        print('[debug] dictionary: ' + str(cmd_dict))
        #cmd_dict = sorted(cmd_dict)
        self.cmd_dict = cmd_dict
         
        # cmds = emoji + command text
        cmds = [value[1] + " " + key for key, value in cmd_dict.items()]
        #cmds.append(u'\U0001F534' "/shutdown")
        cmds.append(u'\U0001F6AA' + "/exit-script")
        cmds = sorted(cmds)

        print('[debug] len: ' + str(len(cmds)))
        print('[debug] cmds: ' + str(cmds))

        # split commands into 2 columns because it looks nice in telegram
        left_col = cmds[:len(cmds)//2]
        right_col = cmds[len(cmds)//2:]
        buttons = [[KeyboardButton(text=left),
                    KeyboardButton(text=right)
                ] for left, right in zip(left_col, right_col)]
        self.keyboard =  ReplyKeyboardMarkup(keyboard=buttons)
        
    
    def exit_script(self):
        """Kills current process after notifying all recipients."""

        # tell eveyone we're going offline
        msg = '[+] exiting script... bye!'
        self.update_recipients(message=msg)
        
        # mark last message as read to avoid death loop
        # where bot keeps reading /exit-script on startup
        self.bot.getUpdates()
        sleep(5)

        # finally kill process
        os.kill(os.getpid(), signal.SIGTERM)

    def shutdown_now(self):
        """Shuts down device immediately."""
        # let everyone know
        msg = '[+] shutting down... bye!'
        self.update_recipients(message=msg)
        
        # mark last message as read to prevent death loop
        self.bot.getUpdates()
        sleep(5)
        
        # issue shutdown command
        os.system('sudo nohup shutdown now')
    
    def on_chat_message(self, msg):
        """Contains all logic for how incoming Telegram messages should be handled."""

        # print basic information about the sender
        sender_id = str(msg['from']['id'])
        sender_name = msg['from']['first_name']
        chat_id = msg['chat']['id']
        
        print('[+][telebot] handling message from ' + sender_id + " (" + sender_name + ")")
        
        # ignore unknown senders
        if sender_id not in self.recipients:
            print('[!] sender unknown, dumping message' + "\n" + str(msg))
            return

        print('[+][telebot] message accepted')

        # get information about message type and decide on a reply
        try:    
            text = msg['text']
            print('[+][telebot] received text: ' + text)
            
            # ignore anything before /command (it's probably an emoji)"
            text = "/" + text.split("/", 1)[1]

            # the first word in the received message should be a command
            text_words = text.split(" ")
            command = text_words[0]
            print('[+][telebot] command: ' + command)
           
            # handle these separately as they should work regardless of what helpers are loaded
            if command == "/exit-script":
                self.exit_script()
            if command == "/shutdown":
                self.shutdown_now()

            target_helper = self.cmd_dict[command][0]
            print('[+][telebot] command args: '+ str(text_words[1:]))
            target_helper.handle_command(chat_id, command, *text_words[1:])

        except TypeError as err:
            print(err)
            msg = '[!] invalid number of arguments provided'
            self.bot.sendMessage(chat_id, msg)
        except KeyError as err:
            #if we don't recognise the command, provide a default reply
            print('[i] KeyError: ', err)
            self.bot.sendMessage(chat_id, "[i] available commands:",
            reply_markup=self.keyboard)

        except Exception as err:
            print(err)
            msg = '[!] an error occurred while processing command'
            self.bot.sendMessage(chat_id, msg)


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
            # yes we need to open the image for each send - known issue
            else:
                with open(img_path, 'rb') as image:
                    self.bot.sendPhoto(rec, image, caption=message, reply_markup = reply_markup)

