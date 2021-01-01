import telepot, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

class Telebot:

    def __init__(self, token, recipients, classifier, petcam, timelapser, tracker):
        print('[+] initialised telebot instance')
        
        self.bot = telepot.Bot(token)
        self.recipients = recipients
        print('\t[i] accepting messages from ids: ' + ", ".join(self.recipients))
        
        self.classifier = classifier
        self.petcam = petcam
        self.timelapser = timelapser
        self.tracker = tracker

        self.cmd_dict = { "/update": self.status_update, 
                "/info": self.dump_info,
                "/photo": self.snap_and_send,
                "/classes": self.list_classes,
                "/lastseen": self.report_last_seen,
                "/help": self.default_reply }
        
        keyboard_buttons = []
        for cmd in self.cmd_dict.keys():
            keyboard_buttons.append(KeyboardButton(text=cmd))
        self.keyboard = ReplyKeyboardMarkup(keyboard=[keyboard_buttons])

        telepot.loop.MessageLoop(self.bot, self.handle_msg).run_as_thread()
    
    def update_recipients(self, message, img_path=''):
        print('\t[+] preparing to send message to all recipients:')
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
        sender_id = str(msg['from']['id'])
        sender_name = msg['from']['first_name']
        print('\t[+] handling message from ' + sender_id + " (" + sender_name + ")")
        
        # ignore senders not on whitelist
        if sender_id not in self.recipients:
            print('\t[!] sender not on whitelist, dumping message' + "\n" + str(msg))
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
                self.cmd_dict[command](chat_id, *text[1:])

    def status_update(self, chat_id):
        # information about the latest snapshot
        reply = "[i] last status: " + self.tracker.last_result + " at " + self.timelapser.last_datetime.strftime("%H:%M:%S")
        self.bot.sendMessage(chat_id, reply)

    def snap_and_send(self, chat_id):
        # photo on demand
        # todo: can we move these functions to the Telebot class and just pass refs to other class instances loaded here?
        self.bot.sendMessage(chat_id, "[i] taking photo")
        filename = self.petcam.snap(self.timelapser.get_last_timestamp())
        with open(filename, 'rb') as image:
            self.bot.sendPhoto(chat_id, image)

    def report_last_seen(self, chat_id, state="dummy"):
        # when was a state last seen? usage: /last state
        try: 
            result = self.tracker.last_seen[state]
            if result == "unknown":
                reply = "[i] not yet seen, please try again later"
            elif type(result) == datetime:
                reply = "[i] last saw " + state + " at " + result.strftime("%H:%M:%S")
        except KeyError:
            reply = "[!] invalid class provided, please use /classes to see available classes"
        
        self.bot.sendMessage(chat_id, reply)


    def list_classes(self, chat_id):
        message = "[i] available classes for use with /lastseen command: " + ", ".join(self.classifier.classes)
        self.bot.sendMessage(chat_id, message)

    def dump_info(self, chat_id):
        # provide basic time/location info for this script run
        message = str(self.__dict__)
        for helper in [self.classifier, self.petcam, self.timelapser, self.tracker]:
             message += "\n" + str(helper.__dict__)

        self.bot.sendMessage(chat_id, message)

    def default_reply(self, chat_id):
        # if command is not recognised
        # send custom keyboard with examples of available commands
        self.bot.sendMessage(chat_id, "[i] available commands:",
            reply_markup=self.keyboard)
