class Helper:

    def __init__ (self):
        name = self.__class__.__name__
        self.cmd_dict = {'/demo-'+ name: [self.handle_command, None]}
    
    def register_telebot(self, telebot_instance):
        self.telebot = telebot_instance

    def create_cmd_dict_for_telebot(self):
        cmd_dict_for_telebot = {key: [self, value[1]] for key, value in self.cmd_dict.items()}
        print(str(cmd_dict_for_telebot))
        return cmd_dict_for_telebot 

    def handle_command(self, chat_id, command):
        message = "[+] I'm " + self.__class__.__name__ + " and I have received command " + str(command)
        self.telebot.bot.sendMessage(chat_id, message)
    
