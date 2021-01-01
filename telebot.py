import teleport, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

class Telebot:

    def __init__(self, token, recipients, classifier, petcam, timelapser):
        print('[+] initialised telebot instance')
        
        self.bot = telepot.Bot(token)
        self.recipients = recipients
        print('[i] accepting messages from ids: ' + ", ".join(self.recipients))
        
        self.classifier = classifier
        self.petcam = petcam
        self.timelapser = timelapser

        self.cmd_dict = {"\update": self.status_update, 
                "\info": self.dump_info,
                "\photo": self.snap_and_send,
                "\classes": self.list_classes,
                "\lastseen": self.last_seen]
        
        keyboard_buttons = []
        for cmd in self.cmd_dict.keys():
            keyboard_buttons.append(KeyboardButton(text=cmd))
        self.keyboard = ReplyKeyboardMarkup(keyboard=[keyboard_buttons])

        telepot.loop.MessageLoop(bot, handle_msg).run_as_thread()
    
    def update_recipients(self, img_path='', message):
        print('[+] preparing to send message to all recipients:')
        print("\t" + message)
        for rec in self.recipients:
            print("\t\t[+] updating " + rec)
            if img_path == '':
                self.bot.sendMessage(rec, message)
            else:
                with open(img_path, 'rb') as image:
                    self.bot.sendPhoto(rec, image, caption=message)

    def handle_msg(self, msg):
        # print basic information about the sender
        sender_id = str(msg['from']['id']
        sender_name = msg['from']['first_name']
        print('[+] handling message from ' + sender + "(" + sender_name + ")")
        
        # ignore senders not on whitelist
        if sender not in recipients:
            print('[!] sender not on whitelist, dumping message' + "\n" + str(msg))
            return

        print('[+] message accepted')

        # get information about message type and decide on a reply
        content_type, chat_type, chat_id = telepot.glance(msg)
        if(content_type=='text'):
            text = msg['text']
            print('[+] received command: ' + text)
            
            # the first word in the received message should be a command
            text = " ".split(text)
            command = text[0]
            
            # but if we don't recognise the command, provide a default reply
            if not command in self.cmd_dict:
                self.cmd_dict['default_reply'](chat_id)
                return
            
            # single-word commands only need to know the chat_id to reply to
            if len(text) == 1:
                self.cmd_dict[command](chat_id)
            
            # many-word commands also contain parameters to be passed on to the command function    
            else:
                self.cmd_dict[command](chat_id, *text[1:])

    def status_update(self, chat_id):
        # information about the latest snapshot
        reply = "[i] last status: " + self.tracker.last_result + " at " + self.timelapser.last_datetime.strftime("%H:%M:%S")
        self.telebot.bot.sendMessage(chat_id, reply)

    def snap_and_send(self, chat_id):
        # photo on demand
        # todo: can we move these functions to the Telebot class and just pass refs to other class instances loaded here?
        self.telebot.bot.sendMessage(chat_id, "[i] taking photo")
        filename = petcam.snap(timelapser.get_last_timestamp())
        with open(filename, 'rb') as image:
            self.bot.sendPhoto(chat_id, image)

    def report_last_seen(self, chat_id, state):
        # when was a state last seen? usage: /last state
        result = tracker.last_seen[state]
        if result == "unknown":
            reply = "[i] not yet seen, please try again later"
        elif type(result) == datetime:
            reply = "[i] last saw " + state + " at " + result.strftime("%H:%M:%S")
        else:
            reply = "[!] invalid class provided, please use /classes to see available classes"
            reply += "\n" + str(self.tracker.last_seen)
        telebot.bot.sendMessage(chat_id, reply)


    def list_classes(self, chat_id):
        message = "[i] available classes for use with /last command: " + ", ".join(self.classifier.classes)
        self.bot.sendMessage(chat_id, message)

    def dump_info(self, chat_id):
        # provide basic time/location info for this script run
         message = self.__dict__
         for helper in [self.classifier, self.petcam, self.timelapser, self.tracker]:
             message += helper.__dict__

         bot.sendMessage(chat_id, message)

    def default_reply(self, chat_id):
        # if command is not recognised
        # send custom keyboard with examples of available commands
        bot.sendMessage(chat_id, "[i] available commands:",
            reply_markup=self.keyboard)
