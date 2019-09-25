#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from messnger_syntax.bot import Bot
import os

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
image_url = 'https://raw.githubusercontent.com/clvrjc2/drpedia/master/images/'
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
                    #received_text(message)
                    if message['message'].get('quick_reply'):
                        received_qr(message)
                        #send_message(sender_id, 'postback is good')  
                    else:
                        received_text(message)
                #if user sends us a GIF, photo,video, or any other non-text item
                elif message['message'].get('attachments'):
                    #TO BE EDIT
                    bot.send_text_message(sender_id,get_message())
            elif message.get("postback"):  # user clicked/tapped "postback" button in earlier message
                received_postback(message)
                    
    return "Message Processed"

def received_qr(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["quick_reply"]["payload"]
    
    if text=='physical':
            bot.send_text_message(sender_id,'Physical Infection Quick reply tapped.')
    if text=='behavioral':
            bot.send_text_message(sender_id,'Behavioral Disorder Quick reply tapped.')
            
def received_text(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["text"]
    
    if text:
        bot.send_text_message(sender_id,'Just a random compliment'+ get_message())
    if text.lower()=='about':
        bot.send_text_message(sender_id,'Intruction on how to user this chatbot under development')
   
def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    payload = event["postback"]["payload"]
    
    
    if payload=='start':
        send_choose_concern(sender_id)
    #Persistent Menu Buttons        
    if payload=='pm_get_pediatrician':
        bot.send_text_message(sender_id,'Get a pediatrician Geo Mapping ToBeDevelop/not')
    if payload=='pm_dengue_prevention':
        bot.send_text_message(sender_id,'Dengue Prevention Under Construction')
    if payload=='pm_about':
        bot.send_text_message(sender_id,'About Under Construction')
        
def send_choose_concern(sender_id):
    bot.send_text_message(sender_id, "Hi I'm DrPedia\nI'm here to cater your pediatric concern.")
    bot.send_text_message(sender_id, "For that you'll have to answer a few questions about your concerns.")
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
    bot.send_quick_replies_message(sender_id, 'What is your concern?', quick_replies)
    return "success"

def init_bot():
    #Greetings 
    greetings =  {"greeting":[
          {
            "locale":"default",
            "text":"Hello {{user_full_name}}!, Thank you for your interest in DrPedia."
          },{
            "locale":"default",
            "text":"Disclaimer: This chatbot do not attempt to represent a real Pediatrician in any way."
          }
        ]}
    
    bot.set_greetings(greetings)
    #Get started button
    gs ={ 
              "get_started":{
                "payload":'start'
              }
        }
    bot.set_get_started(gs)
    #Persistent Menu
    false=False
    pm_menu = {
                "persistent_menu": [
                    {
                        "locale": "default",
                        "composer_input_disabled": false,
                        "call_to_actions": [
                            {
                                "type": "postback",
                                "title": "Get a Pediatrician",
                                "payload": "pm_get_pediatrician"
                            },
                            {
                                "type": "postback",
                                "title": "Dengue Prevention",
                                "payload": "pm_dengue_prevention"
                            },
                            {
                                "type": "postback",
                                "title": "About",
                                "payload": "pm_about"
                            }
                        ]
                    }
                ]
            }
    bot.set_persistent_menu(pm_menu)
        
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

    
#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

        

init_bot()
if __name__ == "__main__":
    app.run()
