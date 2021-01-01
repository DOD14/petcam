import teleport, telepot.loop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

class Telebot:

    def __init__(self, token, recipientsi, cmd_dict):
        print('[+] initialised Telebot instance')
        
        self.bot = telepot.Bot(token)
        self.recipients = recipients
        print('[i] accepting messages from ids: ' + ", ".join(self.recipients))
        
        self.cmd_dict = cmd_dict

        telepot.loop.MessageLoop(bot, handle_msg).run_as_thread()
    
    def handle_msg(self, msg):
        
        # ignore senders not on whitelist
        sender_id = str(msg['from']['id']
        sender_name = msg['from']['first_name']
        print('[+] handling message from ' + sender + "(" + sender_name + ")")

        if sender in recipients:
            print('[+] message accepted')

            # get basic information about message type and decide on a reply
            content_type, chat_type, chat_id = telepot.glance(msg)
            if(content_type=='text'):
                text = msg['text']
                print('[+] received command: ' + text)
                text = " ".split(text)
                command = text[0]
                if len(text) == 1:
                    cmd_dict[command](chat_id)
                else:
                    cmd_dict[command](chat_id, *text[1:])

