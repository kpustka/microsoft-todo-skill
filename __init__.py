from mycroft import MycroftSkill, intent_file_handler


class MicrosoftTodo(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('todo.microsoft.intent')
    def handle_todo_microsoft(self, message):
        self.speak_dialog('todo.microsoft')


def create_skill():
    return MicrosoftTodo()

