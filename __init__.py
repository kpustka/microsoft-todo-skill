from mycroft import MycroftSkill, intent_file_handler

import requests
import json
import msal
import os.path

app_id = '00d864b0-093b-4290-98ab-fd7f69ddd665'
#tenant_id = 'f8cdef31-a31e-4b4a-93e4-5f571e91255a'
#tenant_id = 'common'

tenant_id = 'consumers'
client_secret = '_0Au.wi0g4uKNeXkJ7oDD8QZCIJi~yy94~'
token_url = 'https://login.microsoftonline.com/f8cdef31-a31e-4b4a-93e4-5f571e91255a/oauth2/token'
AUTHORITY = 'https://login.microsoftonline.com/' + tenant_id
#token_url = 'https://login.microsoftonline.com/common/oauth2/token'
graph_url = 'https://graph.microsoft.com/v1.0'

SCOPES = [
  'Tasks.Read',
  'Tasks.Read.Shared',
  'Tasks.ReadWrite',
  'Tasks.ReadWrite.Shared',
  'User.Read'
]

token_data = {
 'grant_type': 'password',
 'client_id': app_id,
 'client_secret': client_secret,
 'resource': 'https://graph.microsoft.com',
 'scope':'https://graph.microsoft.com',
 'username':'dakonny@gmail.com', #Account with no 2MFA
 'password':'mict;B9f#!y',
}

token = ''

class MicrosoftTodo(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.log.info('initialize')
        self.cache = msal.SerializableTokenCache()

        if os.path.exists('/home/pi/token_cache.bin'):
            self.cache.deserialize(open('/home/pi/token_cache.bin', 'r').read())

        #atexit.register(lambda: open('/home/pi/token_cache.bin', 'w').write(cache.serialize()) if cache.has_state_changed else None)

        self.app = msal.PublicClientApplication(app_id, authority=AUTHORITY, token_cache=self.cache)
        token = self._get_token()
        result = requests.get(f'{graph_url}/me', headers={'Authorization': 'Bearer ' + token})
        result.raise_for_status()
        self.log.info(result.json())
 
    def _get_token(self):
        accounts = self.app.get_accounts()
        result = None
        if len(accounts) > 0:
            result = self.app.acquire_token_silent(SCOPES, account=accounts[0])

        if result is None:
            flow = self.app.initiate_device_flow(scopes=SCOPES)
            if 'user_code' not in flow:
                raise Exception('Failed to create device flow')

            self.log.info(flow['message'])

            result = self.app.acquire_token_by_device_flow(flow)

        if 'access_token' in result:
            open('/home/pi/token_cache.bin', 'w').write(self.cache.serialize())
            return result['access_token']

        else:
            raise Exception('no access token in result')        

    @intent_file_handler('todo.microsoft.intent')
    def handle_todo_microsoft(self, message):
        item = message.data.get('item')
        if item is not None:
            token = self._get_token()
            headers = {
                'Authorization': 'Bearer ' + token
            }
            self.log.info(headers)
            result = requests.get(f'{graph_url}/me/todo/lists', 
                headers=headers)
            self.log.info(result.json())
            lists = result.json()['value']
            for list in lists:
                if list['displayName'] == 'Einkaufsliste':
                    shoppingListId = list['id']
            self.log.info('Einkaufsliste: ' + shoppingListId)
            self.log.info('Item: ' + item)
            new_item = {
                "title": item
            }
            headers = {
                'Authorization': 'Bearer {0}'.format(token),
                'Content-Type': 'application/json'
            }
            result = requests.post(f'{graph_url}/me/todo/lists/{shoppingListId}/tasks',
                headers=headers, 
                json=new_item)

            self.log.info(result.json())

            self.speak_dialog('todo.microsoft', {'item': item})
        else:
            self.speak_dialog('nix verstehen')


def create_skill():
    return MicrosoftTodo()

