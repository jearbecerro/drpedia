#Libraries to be import START
import random
from flask import Flask, request
from messnger_syntax.bot import Bot
import os
import pymongo
from pymongo import MongoClient
import Mongo#import Mongo.py
#Libraries to be import END

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
MONGO_TOKEN = os.environ['MONGO_DB']

cluster = MongoClient(MONGO_TOKEN)
db = cluster["DrPedia"]
users = db["users"]
patient = db["patient"]


bot = Bot (ACCESS_TOKEN)
image_url = 'https://raw.githubusercontent.com/clvrjc2/drpedia/master/images/'

GREETING_RESPONSES = ["Hi", "Hey", "Hello there", "Hello", "Hi there"]
created_at = ''
last_seen = ''
fname = ''
lname = '' 
ask = '' 
answer = '' 
terms = ''
name = ''
age = ''
weight = ''
relation  = ''

phrase = ''
myself = False
#to be deleted
remedies_adhd = ["eat a healthy, balanced diet", "get at least 60 minutes of physical activity per day", "get plenty of sleep", "limit daily screen time from phones, computers, and TV"]
def get_remedies_adhd():
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
                    if message['message'].get('quick_reply'):
                        received_qr(message)  
                    else: #else if message is just a text
                        received_text(message)
                #if user sends us a GIF, photo,video, or any other non-text item
                elif message['message'].get('attachments'):
                    #TO BE EDIT
                    bot.send_text_message(sender_id,get_message())
            elif message.get("postback"):  # user clicked/tapped "postback" button in earlier message
                received_postback(message)
                    
    return "Message Processed"

#if user send a message in text
def received_text(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["text"]
    global created_at, last_seen, fname, lname, ask, answer, terms
    global name, age, weight, relation , phrase
    user_data = Mongo.get_data_users(users, sender_id)
    patient_data = Mongo.get_data_patient(patient, sender_id)
    if user_data !=None:
        created_at = user_data['created_at']
        last_seen = user_data['last_seen']
        fname = user_data['first_name']
        lname = user_data['last_name']
        ask = user_data['last_message_ask']
        answer = user_data['last_message_answer']
        terms = user_data['accept_disclaimer'] 
    else: 
        pass
    if patient_data !=None:
        name = patient_data['name']
        age = patient_data['age']
        weight = patient_data['weight']
        relation  = patient_data['relation']
    else: 
        pass
    
    '''
    if text.lower() in ("hello", "hi", "greetings", "sup", "what's up", "hey", "yow"):
        greet = random.choice(GREETING_RESPONSES)
        bot.send_text_message(sender_id, "{} {}, I'm DrPedia, your own pediatric concern companion.".format(greet,first_name(sender_id)))
        send_choose_concern(sender_id)
    '''
    #Mental Health{
    if text.lower() in ("attention deficit hyperactivity disorder", "adhd"):#if user send text 'adhd'
        choose_option_mental(sender_id,'send_tips_adhd','check_adhd','ADHD')
        #proceed to payload button if payload=='send_tips_adhd' or if payload=='check_adhd'

    elif text.lower() in ("oppositional defiant disorder", "odd") :
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
    '''else:
        bot.send_text_message(sender_id,'Humans are so complicated Im not trained to understand things well. Sorry :(')'''
    
    if ask == "Whats the name of your child?" or ask == "Whats the name of the child?":
        Mongo.set_patient(patient, sender_id, 'name', text)
        Mongo.set_ask(users, sender_id, "How old are you?")
        bot.send_text_message(sender_id, "May I ask how old is the child? In human years.")
        bot.send_text_message(sender_id, "Just type '18'\nof course human years are not 200 years old. 😉")
    else:
        pass
    if ask == "How old are you?":
        if text != None:
            if int(text) >18 and int(text)<30:
                Mongo.set_patient(patient, sender_id, 'age', text)
                Mongo.set_ask(users,'What is your weight in kg?')
                bot.send_text_message(sender_id,'Oh right, I can only cater children between 0 - 18 years old.\nBut anyway we can still proceed.')
                bot.send_text_message(sender_id,'What is the weight of the child in kg?')
            elif text != None and int(text) <=18:
                Mongo.set_patient(patient, sender_id, 'age', text)
                Mongo.set_ask(users,sender_id,'What is the weight of the child in kg?')
                bot.send_text_message(sender_id,'Perfect!')
                bot.send_text_message(sender_id,'What is the weight of the child in kg?')
            elif int(text) in range(31,100):
                bot.send_text_message(sender_id,'I do apologize, I can only cater 0 - 18 years old.')
            else:
                bot.send_text_message(sender_id,'I told you in human years')
                bot.send_text_message(sender_id,'What is the age again?')
        else:
            pass
    else:
        pass
    if ask == "What is your weight in kg?":
        if text.isdigit():
            if text != None and int(text) > 150 and int(text) < 0:
                bot.send_text_message(sender_id,'I told you in kilogram.')
                bot.send_text_message(sender_id,'What is the weight again?')
            else:
                Mongo.set_patient(patient, sender_id, 'weight', text)
                bot.send_text_message(sender_id,'Oh right {}'.format(first_name(sender_id))) 
                quick_replies = {
                                "content_type":"text",
                                "title":"👌Yes",
                                "payload":'ýes_correct'
                              },{
                                "content_type":"text",
                                "title":"👎No",
                                "payload":'no_correct'
                              }
                if relation == 'myself':
                    bot.send_text_message(sender_id,'You are {} years old and you are {} kg in weight.'.format(age, weight))
                    bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)
                elif relation == 'mychild':
                    bot.send_text_message(sender_id,'Your childs name is {} and he/she is {} years old,\nalso he/she is {} kg in weight.'.format(name, age, weight))
                    bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)
                elif relation == 'someone':
                    bot.send_text_message(sender_id,'The childs name is {} and he/she is {} years old,\nalso he/she is {} kg in weight.'.format(name, age, weight))
                    bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)
        else:
            pass
    else:
        pass
#if user tap a button from a quick reply
def received_qr(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["quick_reply"]["payload"]
    global created_at, last_seen, fname, lname, ask, answer, terms
    global name, age, weight, relation, phrase , myself
    user_data = Mongo.get_data_users(users, sender_id)
    patient_data = Mongo.get_data_patient(patient, sender_id)
    if user_data !=None:
        created_at = user_data['created_at']
        last_seen = user_data['last_seen']
        fname = user_data['first_name']
        lname = user_data['last_name']
        ask = user_data['last_message_ask']
        answer = user_data['last_message_answer']
        terms = user_data['accept_disclaimer'] 
    else: 
        pass
    if patient_data !=None:
        name = patient_data['name']
        age = patient_data['age']
        weight = patient_data['weight']
        relation  = patient_data['relation']
    else: 
        pass
    if relation == 'myself':
        phrase = 'Are you '
        myself = True
    else:
        phrase = 'Is {} '.format(name)
        myself = False
    unique_symptom = {
                            "content_type":"text",
                            "title":"Fever",
                            "payload":"fever"
                          },{
                            "content_type":"text",
                            "title":"Diarrhea",
                            "payload":"diarrhea"
                          },{
                            "content_type":"text",
                            "title":"Pain in swallowing",
                            "payload":"swallowing"
                          },{
                            "content_type":"text",
                            "title":"Pain in urination",
                            "payload":"urination"
                          },{
                            "content_type":"text",
                            "title":"Body pain",
                            "payload":"body"}
    if text == 'yes_correct':
        bot.send_text_message(sender_id, "Great!")
        bot.send_text_message(sender_id, "Now we can proceed to your concern.")
        bot.send_quick_replies_message(sender_id, "{} experiencing one of this symptoms?".format(phrase), unique_symptom)  
    if text == 'no_correct':
        if myself == True:
            Mongo.set_ask(users, sender_id, "How old are you?")
            bot.send_text_message(sender_id, "May I ask how old are you? In human years.")
            bot.send_text_message(sender_id, "Just type '18'\nof course you are not 200 years old. 😉")
        else:
            Mongo.set_ask(users, sender_id, "Whats the name of your child?")
            bot.send_text_message(sender_id, "Whats the name the child {}?".format(first_name(sender_id)))
    if text =='myself':
        Mongo.create_patient(patient, sender_id, first_name(sender_id), '', '', 'myself')
        Mongo.set_ask(users, sender_id, "How old are you?")
        bot.send_text_message(sender_id, "May I ask how old are you? In human years.")
        bot.send_text_message(sender_id, "Just type '18'\nof course you are not 200 years old. 😉")
        #bot.send_quick_replies_message(sender_id, "Are you experiencing one of this symptoms?", unique_symptom)        
    if text =='mychild':
        Mongo.create_patient(patient, sender_id, '', '', '', 'mychild')
        Mongo.set_ask(users, sender_id, "Whats the name of your child?")
        bot.send_text_message(sender_id, "Whats the name of your child {}?".format(first_name(sender_id)))
        #bot.send_quick_replies_message(sender_id, "Is your child experiencing one of this symptoms?", unique_symptom)        
    if text =='someone':
        Mongo.create_patient(patient, sender_id, '', '', '', 'someone')
        Mongo.set_ask(users, sender_id, "Whats the name of the child?")
        bot.send_text_message(sender_id, "Whats the name the child {}?".format(first_name(sender_id)))
        #bot.send_quick_replies_message(sender_id, "Is the child experiencing one of this symptoms?", unique_symptom)
    #2.1
    if text=='physical':
        listofconcern = 'Dengue,\nAcute Gastroenteritis,\nUrinary Tract Infection,\nAcute Tonsilitis,\nFLU\nand minor symptoms simply like soar throat, back pain, cold and so on.'
        concern= 'physical health'
        after_accept_terms(sender_id,concern,listofconcern,'yes_proceed_physical','no_proceed_physical')
        #Sqlite.set_answer(sender_id,'physical')
        Mongo.set_answer(users,sender_id,'physical')
    #2.2    
    if text=='mental':
        listofconcern = 'Attention Deficit Hyperactivity Disorder (ADHD)🤪,\nOppositional Defiant Disorder (ODD)😕,\nAutism Spectrum Disorder (ASD)😔,\nAnxiety Disorder😰,\nDepression😞,\nBipolar Disorder🤗😠,\nLearning Disorders🤔,\nConduct Disorders🤬'
        concern= 'mental health'
        after_accept_terms(sender_id,concern,listofconcern,"yes_proceed_mental","no_proceed_mental")
        #Sqlite.set_answer(sender_id,'mental')
        Mongo.set_answer(users,sender_id,'mental')
    #2.2.1
    if text =="yes_agree":
        Mongo.set_terms(users, sender_id,'Yes')
        bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff")
        send_choose_concern(sender_id)
        
    #2.2.2    
    if text=='see_details':
        bot.send_text_message(sender_id,"Sure here it is..")
        bot.send_text_message(sender_id,"www.tobelink.com/legal")
        readytogo = [
                        {
                        "type": "postback",
                        "title": "🤝Agree and proceed",
                        "payload": "ready_accept"
                        }
                        ]
        bot.send_button_message(sender_id, 'Ready to go?', readytogo)
        #proceed to payload button if payload=='mental_symptom_checker'
   
    if text=='yes_proceed_mental':
        bot.send_text_message(sender_id,"If you have suspected mental health problem listed above.\nSimply type it in⌨️\nFor example: 'adhd'")
        button = [
                        {
                        "type": "postback",
                        "title": "🔍Check Symptom",
                        "payload": "mental_symptom_checker"
                        }
                        ]
        bot.send_button_message(sender_id, "If you don't have any idea🤔. Just tap 'Check Symptom'", button)
        '''Sqlite.set_ask(sender_id, 'type mental')'''
    if text=='no_proceed_mental':     
        bot.send_text_message(sender_id,"I understand, Thank you for using DrPedia.\n")
        send_choose_concern(sender_id)
        
    if text=='yes_proceed_physical':
        bot.send_text_message(sender_id,"If you have suspected physical health problem listed above.\nSimply type it in⌨️\nExample: 'dengue'")
        button = [
                        {
                        "type": "postback",
                        "title": "🔍Check Symptom",
                        "payload": "physical_symptom_checker"
                        }
                        ]
        bot.send_button_message(sender_id, "If you don't have any idea🤔. Just tap 'Check Symptom'", button)
        
    if text=='no_proceed_physical':     
        bot.send_text_message(sender_id,"I understand, Thank you for using DrPedia.\n")
        send_choose_concern(sender_id)
  
#if user tap a button from a regular button
def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    payload = event["postback"]["payload"]
    global created_at, last_seen, fname, lname, ask, answer, terms
    global name, age, weight, relation
    user_data = Mongo.get_data_users(users, sender_id)
    patient_data = Mongo.get_data_patient(patient, sender_id)
    if user_data !=None:
        created_at = user_data['created_at']
        last_seen = user_data['last_seen']
        fname = user_data['first_name']
        lname = user_data['last_name']
        ask = user_data['last_message_ask']
        answer = user_data['last_message_answer']
        terms = user_data['accept_disclaimer'] 
    else: 
        pass
    if patient_data !=None:
        name = patient_data['name']
        age = patient_data['age']
        weight = patient_data['weight']
        relation  = patient_data['relation']
    else: 
        pass
    #2.2.1.1{
    
    if payload=='ready_accept':
        Mongo.set_terms(users, sender_id,'Yes')
        bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff")
        send_choose_concern(sender_id)
        
        
    if payload=='check_adhd':
        bot.send_text_message(sender_id,'Attention deficit hyperactivity disorder (ADHD) is a mental health disorder that can cause above-normal levels of hyperactive and impulsive behaviors.\nPeople with ADHD may also have trouble focusing their attention on a single task or sitting still for long periods of time.')
        bot.send_text_message(sender_id,'I will ask a few questions inorder to identify if the patient had adhd')
    
    if payload=='send_tips_adhd':
        choose_howto_mental(sender_id,'remedies_adhd','medication_adhd','about_adhd','ADHD')
        
    if payload=='about_adhd':
        bot.send_text_message(sender_id,'Attention deficit hyperactivity disorder (ADHD) is a mental health disorder that can cause above-normal levels of hyperactive and impulsive behaviors.\nPeople with ADHD may also have trouble focusing their attention on a single task or sitting still for long periods of time.')
        buttons = [
                        {
                        "type": "postback",
                        "title": "ADHD Symptoms",
                        "payload": "send_symptoms_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of ADHD?", buttons)
        
    if payload=='send_symptoms_adhd':  
        '''having trouble focusing or concentrating on tasks
        being forgetful about completing tasks
        being easily distracted
        having difficulty sitting still
        interrupting people while they’re talking'''                                                                                                                                                                                                                                    
        bot.send_text_message(sender_id,"A wide range of behaviors are associated with ADHD. Some of the more common ones include:\nhaving trouble focusing or concentrating on tasks\nbeing forgetful about completing tasks\nbeing easily distracted\nhaving difficulty sitting still\ninterrupting people while they’re talking")
        buttons = [
                        {
                        "type": "postback",
                        "title": "Types of ADHD",
                        "payload": "send_types_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, "Want to know the types of ADHD?", buttons)
    if payload=='send_types_adhd':
        bot.send_text_message(sender_id,"To make ADHD diagnoses more consistent, the APA(American Psychological Association) has grouped the condition into three categories, or types. These types are predominantly inattentive, predominantly hyperactivity-impulsive, and a combination of both.")
        bot.send_text_message(sender_id,"Predominantly inattentive\n\nAs the name suggests, people with this type of ADHD have extreme difficulty focusing, finishing tasks, and following instructions.\n\nExperts also think that many children with the inattentive type of ADHD may not receive a proper diagnosis because they don’t tend to disrupt the classroom. This type is most common among girls with ADHD.")
        bot.send_text_message(sender_id,"Predominantly hyperactive-impulsive type.\n\nPeople with this type of ADHD show primarily hyperactive and impulsive behavior. This can include fidgeting, interrupting people while they’re talking, and not being able to wait their turn.\n\nAlthough inattention is less of a concern with this type of ADHD, people with predominantly hyperactive-impulsive ADHD may still find it difficult to focus on tasks")
        bot.send_text_message(sender_id,"Combined hyperactive-impulsive and inattentive type\n\nThis is the most common type of ADHD. People with this combined type of ADHD display both inattentive and hyperactive symptoms. These include an inability to pay attention, a tendency toward impulsiveness, and above-normal levels of activity and energy.")
        buttons = [
                        {
                        "type": "postback",
                        "title": "Cause of ADHD",
                        "payload": "send_cause_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, "What causes ADHD?", buttons)
    if payload=='send_cause_adhd':   
        bot.send_text_message(sender_id,"Despite how common ADHD is, doctors and researchers still aren’t sure what causes the condition. It’s believed to have neurological origins. Genetics may also play a role.")
    
    if payload=='remedies_adhd':
        '''eat a healthy, balanced diet
        get at least 60 minutes of physical activity per day
        get plenty of sleep
        limit daily screen time from phones, computers, and TV'''    
        buttons = [
                        {
                        "type": "postback",
                        "title": "📩Send Another",
                        "payload": "send_remedies_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, get_remedies_adhd(), buttons)    
        
    if payload=='send_remedies_adhd':   
        buttons = [
                        {
                        "type": "postback",
                        "title": "📩Send Another",
                        "payload": "send_remedies_adhd"
                        }
                        ]
        bot.send_button_message(sender_id, get_remedies_adhd(), buttons)  
        
    if payload=='mental_symptom_checker':
        bot.send_text_message(sender_id,"How old is the patient?\n Just type 'age:17' for example")
        
    if payload=='physical_symptom_checker':
        quick_replies = {
                            "content_type":"text",
                            "title":"Myself",
                            "payload":"myself"
                          },{
                            "content_type":"text",
                            "title":"My Child",
                            "payload":"mychild"
                          },{
                            "content_type":"text",
                            "title":"Someone else",
                            "payload":"someone"
                          }
        bot.send_quick_replies_message(sender_id, 'Who do you want to check symptoms, {}?'.format(first_name(sender_id)), quick_replies)      
    #2.2.2.1}
    
        
    #Get started button tapped{
    if payload=='start':
        greet = random.choice(GREETING_RESPONSES)
        
        if not Mongo.user_exists(users,sender_id): #Sqlite.user_exists(sender_id):if user_exists == false add user information
            Mongo.set_ask(users,sender_id, "pleased to meet me?")
            bot.send_text_message(sender_id, "Hi I'm DrPedia, your own pediatric companion.")
            bot.send_text_message(sender_id, "My main responsibility is to assist you with catering pediatric concern including physical and mental health problem.")
            #bot.send_text_message(sender_id, "For that you'll have to answer a few questions.")
            #bot.send_text_message(sender_id, "Of course, what ever you tell me will remain carefully between us!.")
            button = [
                            {
                            "type": "postback",
                            "title": "Nice to meet you!",
                            "payload": "pmyou"
                            }
                            ]
            bot.send_button_message(sender_id, 'Are you glad to meet me {}🤗?'.format(first_name(sender_id)), button)    
            #Sqlite.set_ask(sender_id, "pleased to meet me?")
            
        else:
            '''if terms == "Yes":#Sqlite.get_terms(sender_id) == "Yes"
                bot.send_text_message(sender_id,"{} {} welcome back!🤗".format(greet,first_name(sender_id)))
                bot.send_text_message(sender_id,"What seems you trouble today {} ?".format(first_name(sender_id)))
                send_choose_concern(sender_id)
            elif terms == "No":#Sqlite.get_terms(sender_id) == "No"'''
            if terms == 'Yes':
                bot.send_text_message(sender_id, "Hi {} welcome back!".format(first_name(sender_id)))
                send_choose_concern(sender_id)
            else:
              greet_disclaimer(sender_id)
            
    if payload=='pmyou':
        Mongo.set_answer(users,sender_id,'glad to meet you')#Sqlite.set_answer(sender_id,'glad to meet you')
        bot.send_text_message(sender_id,"I'm glad to meet you too {}. 😉".format(first_name(sender_id)))  
        greet_disclaimer(sender_id)
        
    #Persistent Menu Buttons        
    if payload=='start_over':
        if terms == "Yes":
            bot.send_text_message(sender_id,"What seems you trouble today {} ?".format(first_name(sender_id)))
            send_choose_concern(sender_id)
        elif terms == "No":
            greet_disclaimer(sender_id)
    if payload=='pm_dengue_prevention':
        bot.send_text_message(sender_id,'Dengue Prevention Under Construction')
    if payload=='pm_about':
        bot.send_text_message(sender_id,'About Under Construction')
    #}
    
    
def after_accept_terms(sender_id,concern,listofconcern,yes_PorM,no_PorM):
    
    bot.send_text_message(sender_id,'To give you the most precise guidance, these are the following {} concerns I can provide:'.format(concern))
    bot.send_text_message(sender_id,listofconcern)
    bot.send_text_message(sender_id,"If your suspected {} problem is not in the list, Im sorry {} 🙁 I'm not trained to cater other {} concerns.".format(concern,first_name(sender_id),concern))
    quick_replies = {
                            "content_type":"text",
                            "title":"👌Yes",
                            "payload":yes_PorM
                          },{
                            "content_type":"text",
                            "title":"👎No",
                            "payload":no_PorM
                          }
    bot.send_quick_replies_message(sender_id, 'Do you want to proceed?', quick_replies)    
    
def choose_howto_mental(sender_id,payload1,payload2,payload3,name):
    choices = [
                        {
                        "type": "postback",
                        "title": "💁‍♂️Natural Remedies",
                        "payload": payload1
                        },{
                        "type": "postback",
                        "title": "💊Medication",
                        "payload": payload2
                        },{
                        "type": "postback",
                        "title": "📃About",
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
                        "title": "💡How to handle?",
                        "payload": payload1
                        },{
                        "type": "postback",
                        "title": "🔎Check Symptom",
                        "payload": payload2
                        }
                        ]
    bot.send_text_message(sender_id,"Got it!")
    bot.send_text_message(sender_id,"If you already know that the patient had {} and you simply need to realize how to deal with it.\nJust tap 'How to handle?' ".format(name))
    bot.send_text_message(sender_id,"To check if the patient may have  {}.\nTap 'Check Symptom'".format(name))
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
    if user_info is not None: 
        first_name = user_info['first_name']
        #lname = user_info['last_name']
        return first_name
    return ''

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
    
def greet_disclaimer(sender_id):
    quick_replies = {
                            "content_type":"text",
                            "title":"🤝Agree and proceed",
                            "payload":"yes_agree"
                          },{
                            "content_type":"text",
                            "title":"📇See details",
                            "payload":"see_details"
                          }
    bot.send_text_message(sender_id,"Before we proceed onward, it's time for a brief interruption from my good friends, the lawyers. ⚖️")
    bot.send_text_message(sender_id,"Remember that DrPedia is just a robot 🤖, not a doctor 👨‍⚕️.")
    bot.send_text_message(sender_id,"DrPedia is intended for informational purposes only and DrPedia don't attempt to represent a real pediatrician or a doctor in any way.")
    bot.send_quick_replies_message(sender_id, "By tapping 'Agree and proceed' you accept DrPedia's Terms of Use and Privacy Policy", quick_replies)
                
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
