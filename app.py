#Python libraries that we need to import for our bot
import random
from flask import Flask, request
#from pymessager.message import Messager
from messnger_syntax.bot import Bot
import os

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

bot = Bot (ACCESS_TOKEN)
#client = Messager(ACCESS_TOKEN)
app = Flask(__name__)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                sender_id = message['sender']['id']
                if message['message'].get('text'):
                    if message['message'].get('text')=='start':
                        #response_sent_text = get_message()
                        #send_message(recipient_id, response_sent_text)
                        image_url = 'https://raw.githubusercontent.com/clvrjc2/drpedia/master/images/'
                        quick_replies = {
                            "content_type":"text",
                            "title":"Physical Health",
                            "payload":"physical",
                            "image_url":image_url+"physical.png"
                          },{
                            "content_type":"text",
                            "title":"Behavioral Coaching",
                            "payload":"behavioral",
                            "image_url":image_url+"behavioral.png"
                          }
                        bot.send_quick_replies_message(sender_id, 'Choose Pediatric Concern', quick_replies)
                    if message['message'].get('text')=='physical': 
                        buttons = [
                                        {
                                        "type": "postback",
                                        "title": "Diagnose",
                                        "payload": "diagnose"
                                        }

                                        ]

                        bot.send_button_message(sender_id,'Diagnose',buttons)   
                        
                    if message['message'].get('text')=='behavioral':
                        buttons = [
                                {
                                "type": "postback",
                                "title": "ADHD",
                                "payload": "adhd"
                                },
                                {
                                "type": "postback",
                                "title": "Autism",
                                "payload": "autism"
                                },
                                {
                                "type": "postback",
                                "title": "Writing Disorder",
                                "payload": "writing_disorder"
                                }
                          ]
                        bot.send_button_message(sender_id,'Choose Behavioral Disorder',buttons)    
                   
                    
                    
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(sender_id, response_sent_nontext)
                    
            if message.get("postback"):  # user clicked/tapped "postback" button in earlier message
                received_postback(message)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    payload = event["postback"]["payload"]
    
    if payload == 'physical':
        buttons = [
                        {
                        "type": "postback",
                        "title": "Diagnose",
                        "payload": "diagnose"
                        }
        
                        ]

        bot.send_button_message(sender_id,'Diagnose',buttons)
    if payload == 'behavioral':
        buttons = [
                        {
                        "type": "postback",
                        "title": "ADHD",
                        "payload": "adhd"
                        },
                        {
                        "type": "postback",
                        "title": "Autism",
                        "payload": "autism"
                        },
                        {
                        "type": "postback",
                        "title": "Writing Disorder",
                        "payload": "writing_disorder"
                        }
                  ]
        bot.send_button_message(sender_id,'Choose Behavioral Disorder',buttons)
    
#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

        
#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
