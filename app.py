#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from messnger_syntax.bot import Bot
import os
from emoji import emojize as emj

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
image_url = 'https://raw.githubusercontent.com/clvrjc2/drpedia/master/images/'
bot = Bot (ACCESS_TOKEN)
#client = Messager(ACCESS_TOKEN)
app = Flask(__name__)

remedies_adhd = ["eat a healthy, balanced diet", "get at least 60 minutes of physical activity per day", "get plenty of sleep", "limit daily screen time from phones, computers, and TV"]
behavioral_age = 0;

def get_remedies_adhd():
    #remedies_adhd = ["eat a healthy, balanced diet", "get at least 60 minutes of physical activity per day", "get plenty of sleep", "limit daily screen time from phones, computers, and TV"]
    # return selected item to the user
    return random.choice(remedies_adhd)


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

def greet_disclaimer(sender_id):
    quick_replies = {
                            "content_type":"text",
                            "title":"Agree and proceed",
                            "payload":"yes_agree"
                          },{
                            "content_type":"text",
                            "title":"See details",
                            "payload":"see_details"
                          }
    bot.send_text_message(sender_id,"I'm glad to meet you too. :)")  
    #bot.send_text_message(sender_id,"By using Drpedia, you must be aware that any information and suggestions for medication and remedies is base from an expert's knowledge. (Pediatrician)")
    bot.send_text_message(sender_id,"Before we proceed onward, it's time for a brief interruption from my good friends, the lawyers.")
    bot.send_text_message(sender_id,"Remember that DrPedia is just a robot, not a doctor.")
    bot.send_text_message(sender_id,"DrPedia is intended for informational purposes only and DrPedia don't attempt to represent a real pediatrician or a doctor in any way.")
    bot.send_quick_replies_message(sender_id, "By tapping 'Agree and proceed' you accept DrPedia's Terms of Use and Privacy Policy", quick_replies)
        
#if user tap a button from a quick reply
def received_qr(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["quick_reply"]["payload"]

    #2.1
    if text=='physical':
        quick_replies = {
                            "content_type":"text",
                            "title":"Yes",
                            "payload":yes_PorM
                          },{
                            "content_type":"text",
                            "title":"No",
                            "payload":no_PorM
                          }
        bot.send_quick_replies_message(sender_id, 'It is useful to know, based on your symptoms, what do you think you should do?', quick_replies)
        listofconcern = 'To be written'
        concern= 'physical health'
        after_accept_terms(sender_id,concern,listofconcern,yes_proceed_physical,no_proceed_physical)
    #2.2    
    if text=='mental':
        listofconcern = 'Attention Deficit Hyperactivity Disorder (ADHD),\nOppositional Defiant Disorder (ODD),\nAutism Spectrum Disorder (ASD),\nAnxiety Disorder,\nDepression,\nBipolar Disorder,\nLearning Disorders,\nConduct Disorders'
        concern= 'mental health'
        after_accept_terms(sender_id,concern,listofconcern,"yes_proceed_mental","no_proceed_mental")
    #2.2.1
    if text =="yes_agree":
        bot.send_text_message(sender_id,"Exellent!, Now that we got that secured, we can proceed onward to the significant stuff") 
        send_choose_concern(sender_id)
    #2.2.2    
    if text=='see_details':
        bot.send_text_message(sender_id,"Sure here it is..")
        bot.send_text_message(sender_id,"www.tobelink.com/legal")
        readytogo = [
                        {
                        "type": "postback",
                        "title": "Agree and proceed",
                        "payload": "ready_accept"
                        }
                        ]
        bot.send_button_message(sender_id, 'Ready to go?', readytogo)
        #proceed to payload button if payload=='mental_symptom_checker'
   
    if text=='yes_proceed_mental':
        bot.send_text_message(sender_id,"Just type the suspected mental health problems listed above to proceed.\nExample: 'adhd'")
        yes_diagnosed_mental = [
                        {
                        "type": "postback",
                        "title": "Symptom Checker",
                        "payload": "mental_symptom_checker"
                        }
                        ]
        bot.send_button_message(sender_id, "If you don't have any idea. Just tap 'Symptom Checker'", yes_diagnosed_mental)
    if text=='no_proceed_mental':     
        bot.send_text_message(sender_id,"I understand, Thank you for using DrPedia.\n")
        send_choose_concern(sender_id)
        
#if user send a message in text
def received_text(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["text"]
    
    if text.lower() in ("hello", "hi", "greetings", "sup", "what's up", "hey", "yow"):
        GREETING_RESPONSES = ["Hi", "Hey", "Hello there", "Hello", "Hi there", "I am glad! You are talking to me", "What's up"]
        greet = random.choice(GREETING_RESPONSES)
        bot.send_text_message(sender_id, "{} {}, I'm DrPedia, your own pediatric concern companion.".format(greet,first_name(sender_id)))
        send_choose_concern(sender_id)
    
    #2.2.1.1..{
    elif text.lower() in ("attention deficit hyperactivity disorder", "adhd"):#if user send text 'adhd'
        choose_option_mental(sender_id,'send_tips_adhd','check_adhd','ADHD')
        #proceed to payload button if payload=='send_tips_adhd' or if payload=='check_adhd'

    elif text.lower() in ("oppositional defiant disorder", "odd"):
        choose_option_mental(sender_id,'send_tips_odd','check_odd','ODD')
        #proceed to payload button if payload=='send_tips_odd' or if payload=='check_odd'
        
    elif text.lower() in ("autism spectrum disorder", "asd", "autism"):
        choose_option_mental(sender_id,'send_tips_asd','check_asd','Autism Spectrum Disorder')
        #proceed to payload button if payload=='send_tips_asd' or if payload=='check_asd'
        
    elif text.lower() in ("anxiety disorder", "anxiety","ad"):
        choose_option_mental(sender_id,'send_tips_ad','check_ad','Anxiety Disorder')
        #proceed to payload button if payload=='send_tips_ad' or if payload=='check_ad'
        
    elif text.lower() in ("depression", "depression disorder","depress"):
        choose_option_mental(sender_id,'send_tips_d','check_d','Depression')
        #proceed to payload button if payload=='send_tips_d' or if payload=='check_d'
        
    elif text.lower() in ("bipolar disorder", "bipolar","bd"):
        choose_option_mental(sender_id,'send_tips_bd','check_bd','Bipolar Disorder')
        #proceed to payload button if payload=='send_tips_bd' or if payload=='check_bd' 
        
    elif text.lower() in ("learning disorders", "learning","ld"):
        choose_option_mental(sender_id,'send_tips_ld','check_ld','Learning Disorder')
        #proceed to payload button if payload=='send_tips_ld' or if payload=='check_ld' 
        
    elif text.lower() in ("conduct disorders", "conduct","cd"):
        choose_option_mental(sender_id,'send_tips_cd','check_cd', 'Conduct Disorder')
        #proceed to payload button if payload=='send_tips_cd' or if payload=='check_cd' 
    #2.2.1.1..}   
        
    elif text.lower()=='about':
        bot.send_text_message(sender_id,'Intruction on how to user this chatbot under development')
   
    else:
        bot.send_text_message(sender_id,'Humans are so complicated Im not train to understain stupid things')
        bot.send_text_message(sender_id, '👍')

#if user tap a button from a regular button
def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    payload = event["postback"]["payload"]
    
    #2.2.1.1{
    
    if payload=='ready_accept':
        bot.send_text_message(sender_id,"Exellent!, Now that we got that secured, we can proceed onward to the significant stuff") 
        send_choose_concern(sender_id)
        
    if payload=='check_adhd':
        bot.send_text_message(sender_id,'Attention deficit hyperactivity disorder (ADHD) is a mental health disorder that can cause above-normal levels of hyperactive and impulsive behaviors.\nPeople with ADHD may also have trouble focusing their attention on a single task or sitting still for long periods of time.')
        bot.send_text_message(sender_id,'I will ask a few questions inorder to identify if the patient had adhd')
    
    if payload=='send_tips_adhd':
        choose_howto_mental(sender_id,'remedies_adhd','medication_adhd','about_adhd','ADHD')
        
    if payload=='about_adhd':
        bot.send_text_message(sender_id,'Attention deficit hyperactivity disorder (ADHD) is a mental health disorder that can cause above-normal levels of hyperactive and impulsive behaviors.\nPeople with ADHD may also have trouble focusing their attention on a single task or sitting still for long periods of time.')
        sendanother = [
                        {
                        "type": "postback",
                        "title": "ADHD Symptoms",
                        "payload": "send_symptoms_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of ADHD?", sendanother)
        
    if payload=='send_symptoms_adhd':  
        '''having trouble focusing or concentrating on tasks
        being forgetful about completing tasks
        being easily distracted
        having difficulty sitting still
        interrupting people while they’re talking'''                                                                                                                                                                                                                                    
        bot.send_text_message(sender_id,"A wide range of behaviors are associated with ADHD. Some of the more common ones include:\nhaving trouble focusing or concentrating on tasks\nbeing forgetful about completing tasks\nbeing easily distracted\nhaving difficulty sitting still\ninterrupting people while they’re talking")
        sendanother = [
                        {
                        "type": "postback",
                        "title": "Types of ADHD",
                        "payload": "send_types_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, "Want to know the types of ADHD?", sendanother)
    if payload=='send_types_adhd':
        bot.send_text_message(sender_id,"To make ADHD diagnoses more consistent, the APA(American Psychological Association) has grouped the condition into three categories, or types. These types are predominantly inattentive, predominantly hyperactivity-impulsive, and a combination of both.")
        bot.send_text_message(sender_id,"Predominantly inattentive\n\nAs the name suggests, people with this type of ADHD have extreme difficulty focusing, finishing tasks, and following instructions.\n\nExperts also think that many children with the inattentive type of ADHD may not receive a proper diagnosis because they don’t tend to disrupt the classroom. This type is most common among girls with ADHD.")
        bot.send_text_message(sender_id,"Predominantly hyperactive-impulsive type.\n\nPeople with this type of ADHD show primarily hyperactive and impulsive behavior. This can include fidgeting, interrupting people while they’re talking, and not being able to wait their turn.\n\nAlthough inattention is less of a concern with this type of ADHD, people with predominantly hyperactive-impulsive ADHD may still find it difficult to focus on tasks")
        bot.send_text_message(sender_id,"Combined hyperactive-impulsive and inattentive type\n\nThis is the most common type of ADHD. People with this combined type of ADHD display both inattentive and hyperactive symptoms. These include an inability to pay attention, a tendency toward impulsiveness, and above-normal levels of activity and energy.")
        sendanother = [
                        {
                        "type": "postback",
                        "title": "Cause of ADHD",
                        "payload": "send_cause_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, "What causes ADHD?", sendanother)
    if payload=='send_cause_adhd':   
        bot.send_text_message(sender_id,"Despite how common ADHD is, doctors and researchers still aren’t sure what causes the condition. It’s believed to have neurological origins. Genetics may also play a role.")
    
    if payload=='remedies_adhd':
        '''eat a healthy, balanced diet
        get at least 60 minutes of physical activity per day
        get plenty of sleep
        limit daily screen time from phones, computers, and TV'''    
        sendanother = [
                        {
                        "type": "postback",
                        "title": "send another",
                        "payload": "send_remedies_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, get_remedies_adhd(), sendanother)    
        
    if payload=='send_remedies_adhd':   
        sendanother = [
                        {
                        "type": "postback",
                        "title": "send another",
                        "payload": "send_remedies_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, get_remedies_adhd(), sendanother)    
    if payload=='mental_symptom_checker':
        bot.send_text_message(sender_id,"How old is the patient?\n Just type 'age:17' for example")
    #2.2.2.1}
    
        
    #Get started button tapped{
    if payload=='start':
        GREETING_RESPONSES = ["Hi", "Hey", "Hello there", "Hello", "Hi there", "I am glad! You are talking to me"]
        greet = random.choice(GREETING_RESPONSES)
        bot.send_text_message(sender_id, "{} {}, I'm DrPedia, your own pediatric concern companion.".format(greet,first_name(sender_id)))
        bot.send_text_message(sender_id, "My main responsibility is to assist you with catering pediatric concern including physical and mental health problem.")
        #bot.send_text_message(sender_id, "For that you'll have to answer a few questions.")
        #bot.send_text_message(sender_id, "Of course, what ever you tell me will remain carefully between us!.")
        button = [
                        {
                        "type": "postback",
                        "title": "Pleased to meet you!",
                        "payload": "pmyou"
                        }
                        ]
        bot.send_button_message(sender_id, 'Thanks for using DrPedia :)', button)    
        #send_choose_concern(sender_id)
    if payload=='pmyou':
        greet_disclaimer(sender_id)
    #Persistent Menu Buttons        
    if payload=='start_over':
        send_choose_concern(sender_id)
    if payload=='pm_dengue_prevention':
        bot.send_text_message(sender_id,'Dengue Prevention Under Construction')
    if payload=='pm_about':
        bot.send_text_message(sender_id,'About Under Construction')
    #}

def after_accept_terms(sender_id,concern,listofconcern,yes_PorM,no_PorM):
    
    bot.send_text_message(sender_id,'To give you the most precise guidance, these are the following {} concerns I can provide:'.format(concern))
    bot.send_text_message(sender_id,listofconcern)
    bot.send_text_message(sender_id,'If your suspected {} is not in the list, Im sorry I cannot cater your concern.'.format(concern))
    quick_replies = {
                            "content_type":"text",
                            "title":"Yes",
                            "payload":yes_PorM
                          },{
                            "content_type":"text",
                            "title":"No",
                            "payload":no_PorM
                          }
    bot.send_quick_replies_message(sender_id, 'Do you want to proceed?', quick_replies)    
    
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
                        "title": "About",
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
    bot.send_text_message(sender_id,"Got it!")
    bot.send_text_message(sender_id,"With tapping 'How to handle?'\nThe patient is already diagnosed by a real Pediatrician and you already know that the patient had a {}".format(name))
    bot.send_text_message(sender_id,"To check if the patient may have  {}.\nTap 'Check'".format(name))
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

def first_name(sender_id):
    user_info = bot.get_user_info(sender_id)
    name = user_info['first_name']
    return name

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
                                "title": "Start Over",
                                "payload": "start_over"
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
