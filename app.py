import os
from flask import Flask, request
from fbmessenger import BaseMessenger
from fbmessenger import quick_replies
from fbmessenger.elements import Text
from fbmessenger.thread_settings import GreetingText, GetStartedButton, MessengerProfile

class Messenger(BaseMessenger):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token
        super(Messenger, self).__init__(self.page_access_token)

    def message(self, message):
        response = Text(text= str(message['message']['text']))
        action = response.to_dict()
        res = self.send(action)
        app.logger.debug('Response: {}'.format(res))

    def delivery(self, message):
        pass

    def read(self, message):
        pass

    def account_linking(self, message):
        pass

    def postback(self, message):
        payload = message['postback']['payload']

        if 'start' in payload:
            quick_reply_1 = quick_replies.QuickReply(title='Location', content_type='location')
            quick_replies_set = quick_replies.QuickReplies(quick_replies=[
                quick_reply_1
            ])
            text = {'text': 'Share your location'}
            text['quick_replies'] = quick_replies_set.to_dict()
            self.send(text)

    def optin(self, message):
        pass

    def init_bot(self):
        greeting_text = GreetingText('Welcome to weather bot')
        messenger_profile = MessengerProfile(greetings=[greeting_text])
        messenger.set_messenger_profile(messenger_profile.to_dict())

        get_started = GetStartedButton(payload='start')

        messenger_profile = MessengerProfile(get_started=get_started)
        messenger.set_messenger_profile(messenger_profile.to_dict())


app = Flask(__name__)
app.debug = True
messenger = Messenger(os.environ.get('ACCCESS_TOKEN'))


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == os.environ.get('FB_VERIFY_TOKEN'):
            messenger.init_bot()
            return request.args.get('hub.challenge')
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        messenger.handle(request.get_json(force=True))
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0')
