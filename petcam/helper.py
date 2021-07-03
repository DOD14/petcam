class Helper:
    def register_telebot(self, telebot_instance):
        self.telebot = telebot_instance

    def init_cmd_dict(self):
        return {}

    def handle_command(self, chat_id, command):
        message = "[+] I'm " + self.__class__.__name__ + " and I have received command " + str(command)
        self.telebot.bot.sendMessage(chat_id, message)

