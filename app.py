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
                    else:
                        received_text(message)
                #if user sends us a GIF, photo,video, or any other non-text item
                elif message['message'].get('attachments'):
                    #TO BE EDIT
                    bot.send_text_message(sender_id,get_message())
            elif message.get("postback"):  # user clicked/tapped "postback" button in earlier message
                received_postback(message)
                    
    return "Message Processed"

#if user tap a button from a quick reply
def received_qr(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["quick_reply"]["payload"]
    #2.1
    if text=='physical':
        bot.send_text_message(sender_id,'Physical Infection Quick reply tapped.')
    
    #2.2    
    if text=='mental':
        quick_replies = {
                            "content_type":"text",
                            "title":"Yes",
                            "payload":"yes_proceed_mental"
                          },{
                            "content_type":"text",
                            "title":"No",
                            "payload":"no_proceed_mental"
                          }
        bot.send_text_message(sender_id,"By using this Drpedia, you must be aware that any suggestions and recommendations for medication and remedies is base from the expert's knowledge.")
        bot.send_text_message(sender_id,"Disclaimer: DrPedia is a chatbot that uses expert system to cater pediatric concern.\nDrPedia do not attempt to represent a real Pediatrician in any way.")
        bot.send_quick_replies_message(sender_id, 'Do you want to proceed?', quick_replies)
    #2.2.1
    if text=='yes_proceed_mental':
        '''attention deficit hyperactivity disorder (ADHD)
        oppositional defiant disorder (ODD)
        autism spectrum disorder (ASD)
        anxiety disorder
        depression
        bipolar disorder
        learning disorders
        conduct disorders'''
        bot.send_text_message(sender_id,'These are the following mental health concerns I can cater:')
        bot.send_text_message(sender_id,'Attention Deficit Hyperactivity Disorder (ADHD),\nOppositional Defiant Disorder (ODD),\nAutism Spectrum Disorder (ASD),\nAnxiety Disorder,\nDepression,\nBipolar Disorder,\nLearning Disorders,\nConduct Disorders')
        bot.send_text_message(sender_id,'If your mental concern is not in the list, I cannot cater your concern.')
        quick_replies = {
                            "content_type":"text",
                            "title":"Yes",
                            "payload":"yes_proceed"
                          },{
                            "content_type":"text",
                            "title":"No",
                            "payload":"no_proceed"
                          }
        bot.send_quick_replies_message(sender_id, 'Do you want to proceed?', quick_replies)
    #2.2.2    
    if text=='no_proceed_mental':
        bot.send_text_message(sender_id,"Thank you for using DrPedia.")
        send_choose_concern(sender_id)
        #proceed to payload button if payload=='mental_symptom_checker'
        
    if text=='yes_proceed':
        bot.send_text_message(sender_id,"Just type the suspected mental health problems listed above to proceed.\nExample: 'adhd'")
        yes_diagnosed_mental = [
                        {
                        "type": "postback",
                        "title": "Symptom Checker",
                        "payload": "mental_symptom_checker"
                        }
                        ]
        bot.send_button_message(sender_id, "If you don't have any idea. Just tap 'Symptom Checker'", yes_diagnosed_mental)
    if text=='no_proceed':     
        bot.send_text_message(sender_id,"Thank you for using DrPedia.")
        send_choose_concern(sender_id)
        
#if user send a message in text
def received_text(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["text"]
    #2.2.1.1..{
    if text.lower() in ("attention deficit hyperactivity disorder", "adhd"):#if user send text 'adhd'
        choose_option_mental(sender_id,'send_tips_adhd','check_adhd','ADHD')
        #proceed to payload button if payload=='send_tips_adhd' or if payload=='check_adhd'
    
    if text.lower() in ("oppositional defiant disorder", "odd"):
        choose_option_mental(sender_id,'send_tips_odd','check_odd','ODD')
        #proceed to payload button if payload=='send_tips_odd' or if payload=='check_odd'
        
    if text.lower() in ("autism spectrum disorder", "asd", "autism"):
        choose_option_mental(sender_id,'send_tips_asd','check_asd','Autism Spectrum Disorder')
        #proceed to payload button if payload=='send_tips_asd' or if payload=='check_asd'
        
    if text.lower() in ("anxiety disorder", "anxiety","ad"):
        choose_option_mental(sender_id,'send_tips_ad','check_ad','Anxiety Disorder')
        #proceed to payload button if payload=='send_tips_ad' or if payload=='check_ad'
        
    if text.lower() in ("depression", "depression disorder","depress"):
        choose_option_mental(sender_id,'send_tips_d','check_d','Depression')
        #proceed to payload button if payload=='send_tips_d' or if payload=='check_d'
        
    if text.lower() in ("bipolar disorder", "bipolar","bd"):
        choose_option_mental(sender_id,'send_tips_bd','check_bd','Bipolar Disorder')
        #proceed to payload button if payload=='send_tips_bd' or if payload=='check_bd' 
        
    if text.lower() in ("learning disorders", "learning","ld"):
        choose_option_mental(sender_id,'send_tips_ld','check_ld','Learning Disorder')
        #proceed to payload button if payload=='send_tips_ld' or if payload=='check_ld' 
        
    if text.lower() in ("conduct disorders", "conduct","cd"):
        choose_option_mental(sender_id,'send_tips_cd','check_cd', 'Conduct Disorder')
        #proceed to payload button if payload=='send_tips_cd' or if payload=='check_cd' 
    #2.2.1.1..}   
        
    if text.lower()=='about':
        bot.send_text_message(sender_id,'Intruction on how to user this chatbot under development')

#if user tap a button from a regular button
def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    payload = event["postback"]["payload"]
    
    #2.2.1.1{
    

    if payload=='check_adhd':
        bot.send_text_message(sender_id,'Attention deficit hyperactivity disorder (ADHD) is a mental health disorder that can cause above-normal levels of hyperactive and impulsive behaviors.\nPeople with ADHD may also have trouble focusing their attention on a single task or sitting still for long periods of time.')
        choose_howto_mental(sender_id,'remedies_adhd','medication_adhd','coaching_adhd','ADHD')
        
    if payload=='mental_symptom_checker':
        bot.send_text_message(sender_id,"How old is the patient?\n Just type 'age:17' for example")
    #2.2.2.1}
    
        
        
    #Get started button tapped{
    if payload=='start':
        bot.send_text_message(sender_id, "Hi I'm DrPedia.\nI'm here to cater your pediatric concern.")
        bot.send_text_message(sender_id, "For that you'll have to answer a few questions about your concern.")
        send_choose_concern(sender_id)
    #Persistent Menu Buttons        
    if payload=='pm_get_pediatrician':
        bot.send_text_message(sender_id,'Get a pediatrician Geo Mapping ToBeDevelop/not')
    if payload=='pm_dengue_prevention':
        bot.send_text_message(sender_id,'Dengue Prevention Under Construction')
    if payload=='pm_about':
        bot.send_text_message(sender_id,'About Under Construction')
    if payload=='adhd':
        bot.send_text_message(sender_id,'About Under Construction')
    #}
    
def choose_howto_mental(sender_id,payload1,payload2,payload3,name):
    choices = [
                        {
                        "type": "postback",
                        "title": "Remedies",
                        "payload": payload1
                        },{
                        "type": "postback",
                        "title": "Medication",
                        "payload": payload2
                        },{
                        "type": "postback",
                        "title": "Coaching",
                        "payload": payload3
                        }
                        ]
    bot.send_text_message(sender_id,"What do you want to know about {}.".format(name))
    bot.send_button_message(sender_id, "Choose:", choices)
    
#2.2.1.1 use multipe times
def choose_option_mental(sender_id,payload1,payload2,name):
    confirm = [
                        {
                        "type": "postback",
                        "title": "How to handle?",
                        "payload": payload1
                        },{
                        "type": "postback",
                        "title": "Check",
                        "payload": payload2
                        }
                        ]
    bot.send_text_message(sender_id,"With tapping 'How to handle?'\nYou already know that the patient had a {}".format(name))
    bot.send_text_message(sender_id,"To check if the patient has {}.\nTap 'Check'".format(name))
    bot.send_button_message(sender_id, "Choose:", confirm)
#1   
def send_choose_concern(sender_id):
    quick_replies = {
                            "content_type":"text",
                            "title":"Physical Health",
                            "payload":"physical",
                            "image_url":image_url+"physical.png"
                          },{
                            "content_type":"text",
                            "title":"Mental Health",
                            "payload":"mental",
                            "image_url":image_url+"behavioral.png"
                          }
    bot.send_quick_replies_message(sender_id, 'What is your concern?', quick_replies)
    return "success"

def init_bot():
    #Greetings 
    greetings =  {"greeting":[
          {
              "locale":"default",
              "text":"Hi {{user_full_name}}!, Thank you for your interest in DrPedia. Disclaimer: This chatbot do not attempt to represent a real Pediatrician in any way."
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

        
#Greetings, persisten menu, get started button
init_bot()
if __name__ == "__main__":
    app.run()
