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
phrase2= ''
myself = False

count_yes = 0
total_symptoms = 0
has_fever = False
percentage = 0
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
                user_data = Mongo.get_data_users(users, sender_id)
                patient_data = Mongo.get_data_patient(patient, sender_id)
    
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
    global name, age, weight, relation , phrase, count_yes
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
        if text.isdigit():
            if relation =='myself':
                phrase = 'What is your weight in kg?'
            else:
                phrase = 'What is the weight of the child in kg?'
            if int(text) >18 and int(text)<30:
                Mongo.set_patient(patient, sender_id, 'age', text)
                Mongo.set_ask(users,sender_id,"What is your weight in kg?")
                bot.send_text_message(sender_id,'Oh right, I can only cater children between 0 - 18 years old.\nBut anyway we can still proceed.')
                bot.send_text_message(sender_id,phrase)
            elif text != None and int(text) <=18:
                Mongo.set_patient(patient, sender_id, 'age', text)
                Mongo.set_ask(users,sender_id,"What is your weight in kg?")
                bot.send_text_message(sender_id,'Perfect!')
                bot.send_text_message(sender_id,phrase)
            elif int(text) in range(31,100):
                bot.send_text_message(sender_id,'I do apologize, I can only cater 0 - 18 years old.')
                bot.send_text_message(sender_id,"To simply start again, just tap 'Start Over' in the persistent menu.")
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
                Mongo.set_ask(users,sender_id,"Is it correct?")
                bot.send_text_message(sender_id,'Oh right {}'.format(first_name(sender_id))) 
                quick_replies = {
                                "content_type":"text",
                                "title":"👌Yes",
                                "payload":'yes_correct1'
                              },{
                                "content_type":"text",
                                "title":"👎No",
                                "payload":'no_correct1'
                              }
                if relation == 'myself':
                    bot.send_text_message(sender_id,'You are {} years old'.format(age))
                    #bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)
                elif relation == 'mychild':
                    bot.send_text_message(sender_id,'Your childs name is {} and he/she is {} years old.'.format(name, age))
                    #bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)
                elif relation == 'someone':
                    bot.send_text_message(sender_id,'The childs name is {} and he/she is {} years old.'.format(name, age))
                    
                bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)  
    else:
        pass
def get_average(count_yes, total_symptoms):
    print(count_yes, total_symptoms)
    if count_yes != 0 and total_symptoms !=0:
        div = count_yes / total_symptoms
        percentage =  div * 100
        print(percentale+'%')
        if int(round(percentage)) >=75:
            return True
        else:
            return False
   
#if user tap a button from a quick reply
def received_qr(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["quick_reply"]["payload"]
    global created_at, last_seen, fname, lname, ask, answer, terms
    global name, age, weight, relation, phrase, phrase2, myself, has_fever, percentage, count_yes, total_symptoms

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
        phrase2 = 'you'
        myself = True
    else:
        phrase = 'Is {} '.format(name)
        myself = False
        phrase2 = name
        
    unique_symptom = {"content_type":"text","title":"Rapid Breathing","payload":"breathing" },{"content_type":"text","title":"Diarrhea","payload":"diarrhea"},{"content_type":"text","title":"Pain in swallowing","payload":"swallowing"},{"content_type":"text","title":"Pain in urination","payload":"urination"},{"content_type":"text","title":"Body pain","payload":"body"}
    quick_replies = {"content_type":"text","title":"👌Yes","payload":'yes_correct'},{"content_type":"text","title":"👎No","payload":'no_correct'}
    
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
            
    has_fever = {"content_type":"text","title":"Yes","payload":'yes_fever'},{"content_type":"text","title":"No","payload":'no_fever'}                         
    #Dengue
    if text =='breathing': 
        count_yes += 1
        total_symptoms += 1
        print(count_yes, total_symptoms)
        Mongo.set_answer(users,sender_id,'breathing')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
        
    if text =='yes_fever' and answer == 'breathing':
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        has_fever = True
        print(count_yes, total_symptoms)
        f2days = {"content_type":"text","title":"Yes","payload":'yes_fever2days'},{"content_type":"text","title":"No","payload":'no_fever2days'}                    
        bot.send_quick_replies_message(sender_id, 'Is the fever occurs 2 days or more?', f2days)
        
    fnight  = {"content_type":"text","title":"Yes","payload":'yes_fnight'},{"content_type":"text","title":"No","payload":'no_fnight'}   
    if text == 'yes_fever2days': 
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, 'Is the fever occurs sunset to sunset or in night time?', fnight)
    if text == 'no_fever2days':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'Is the fever occurs sunset to sunset or in night time?', fnight)
        
    ha = {"content_type":"text","title":"Yes","payload":'yes_ha'},{"content_type":"text","title":"No","payload":'no_ha'}     
    if text == 'yes_fnight' and answer =='breathing':
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} experiencing headache?'.format(phrase), ha)
    if text == 'no_fnight' and answer =='breathing':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing headache?'.format(phrase), ha)
    if text =='no_fever' and answer == 'breathing':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing headache?'.format(phrase), ha)
        
    bp = {"content_type":"text","title":"Yes","payload":'yes_bp'},{"content_type":"text","title":"No","payload":'no_bp'}    
    if text == 'yes_ha' and answer =='breathing':
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} experiencing body pain?'.format(phrase), bp)
    if text == 'no_ha' and answer == 'breathing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing body pain?'.format(phrase), bp)
    
    v = {"content_type":"text","title":"Yes","payload":'yes_v'},{"content_type":"text","title":"No","payload":'no_v'}    
    if text == 'yes_bp' and answer == 'breathing':
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} experiencing vomiting?'.format(phrase), v)
    if text == 'no_bp' and answer == 'breathing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing vomiting?'.format(phrase), v)
        
    if text == 'yes_v' and answer == 'breathing':
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        vo3 = {"content_type":"text","title":"Yes","payload":'yes_vo3'},{"content_type":"text","title":"No","payload":'no_vo3'} 
        bot.send_quick_replies_message(sender_id, 'Is vomiting occurs at least 3 times within day?', vo3)      
    
    ap = {"content_type":"text","title":"Yes","payload":'yes_ap'},{"content_type":"text","title":"No","payload":'no_ap'}  
    if text == 'no_v' and answer == 'breathing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing Abdominal Pain ?'.format(phrase), ap )   
           
    vbs = {"content_type":"text","title":"Yes","payload":'yes_vbs'},{"content_type":"text","title":"No","payload":'no_vbs'} 
    if text == 'yes_vo3' and answer == 'breathing':  
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} vomiting blood, or blood in the stool'.format(phrase), vbs)  
    if text == 'no_vo3' and answer == 'breathing':    
        bot.send_quick_replies_message(sender_id, '{} vomiting blood, or blood in the stool'.format(phrase), vbs)  
        total_symptoms += 1
    if text == 'yes_vbs' and answer == 'breathing':   
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} experiencing Abdominal Pain ?'.format(phrase), ap )    
    if text == 'no_vbs' and answer == 'breathing':  
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} experiencing Abdominal Pain ?'.format(phrase), ap )    
    
    pa = {"content_type":"text","title":"Yes","payload":'yes_pa'},{"content_type":"text","title":"No","payload":'no_pa'}   
    if text == 'yes_ap' and answer == 'breathing': 
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having poor appetite?'.format(phrase), pa)      
    if text == 'no_ap' and answer == 'breathing':  
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having poor appetite?'.format(phrase), pa) 
    '''    
    check = {"content_type":"text","title":"Yes","payload":'yes_check'},{"content_type":"text","title":"No","payload":'no_check'}   
    if count_yes not in range(0,3) and answer == 'breathing' and count_yes <=5:
        bot.send_quick_replies_message(sender_id, '{} experiencing one of these symptoms :\n*rashes\n*pain behind the eyes\n*fatigue\n*nausea\n*mild bleeding\n*feeling tired\n*cold'.format(phrase), check) 
    else:
        continue
    if text == 'yes_check':
        pass
    if text == 'no_check':
        pass# tobe edit dapat mo adto siya sa kapareha niyag symptom
    
    if has_fever == True:
        r2f = {"content_type":"text","title":"Yes","payload":'yes_r2f'},{"content_type":"text","title":"No","payload":'no_r2f'}  
        if text == 'yes_pa' and answer == 'breathing':#dapat epangutana rani siya if fever is YES
            count_yes += 1
            bot.send_quick_replies_message(sender_id, '{} having rashes 2 days or more after fever?'.format(phrase), r2f)
            
        if text == 'no_pa' and answer == 'breathing': 
            bot.send_quick_replies_message(sender_id, '{} having rashes 2 days or more after fever?'.format(phrase), r2f) 
    else:
        pass
    '''
    r2f = {"content_type":"text","title":"Yes","payload":'yes_r2f'},{"content_type":"text","title":"No","payload":'no_r2f'}  
    if text == 'yes_pa' and answer == 'breathing':#dapat epangutana rani siya if fever is YES
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having rashes 2 days or more after fever?'.format(phrase), r2f)
            
    if text == 'no_pa' and answer == 'breathing': 
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having rashes 2 days or more after fever?'.format(phrase), r2f) 
    pbe = {"content_type":"text","title":"Yes","payload":'yes_pbe'},{"content_type":"text","title":"No","payload":'no_pbe'}   
    if text == 'yes_r2f' and answer == 'breathing':  
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having pain behind the eyes?'.format(phrase), pbe)   
    if text == 'no_r2f' and answer == 'breathing':  
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having pain behind the eyes?'.format(phrase), pbe)
    
    fat = {"content_type":"text","title":"Yes","payload":'yes_fat'},{"content_type":"text","title":"No","payload":'no_fat'}
    if text == 'yes_pbe' and answer == 'breathing':  
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} fatigue?'.format(phrase), fat)       
    if text == 'no_pbe' and answer == 'breathing':  
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} fatigue?'.format(phrase), fat) 
        
    nas = {"content_type":"text","title":"Yes","payload":'yes_nas'},{"content_type":"text","title":"No","payload":'no_nas'} 
    if text == 'yes_fat' and answer == 'breathing':  
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} feeling nausea ?'.format(phrase), nas) 
    if text == 'no_fat' and answer == 'breathing':  
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} feeling nausea ?'.format(phrase), nas) 
        
    mbn = {"content_type":"text","title":"Yes","payload":'yes_mbn'},{"content_type":"text","title":"No","payload":'no_mbn'}
    if text == 'yes_nas' and answer == 'breathing': 
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having mild bleeding such as nose bleed, bleeding gums, or easy bruising  ?'.format(phrase), mbn) 
    if text == 'no_nas' and answer == 'breathing':
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having mild bleeding such as nose bleed, bleeding gums, or easy brusing ?'.format(phrase), mbn) 
    
    tri = {"content_type":"text","title":"Yes","payload":'yes_tri'},{"content_type":"text","title":"No","payload":'no_tri'}
    if text == 'yes_mbn' and answer == 'breathing': 
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} feeling tired, restless, or irritable ?'.format(phrase), tri) 
    if text == 'no_mbn' and answer == 'breathing':
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} feeling tired, restless, or irritable ?'.format(phrase), tri) 
    
    ccs = {"content_type":"text","title":"Yes","payload":'yes_ccs'},{"content_type":"text","title":"No","payload":'no_ccs'}
    if text == 'yes_tri' and answer == 'breathing': 
        count_yes = count_yes + 1
        total_symptoms = total_symptoms + 1
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} having cold or clammy skin ?'.format(phrase), ccs) 
    if text == 'no_tri' and answer == 'breathing':
        total_symptoms = total_symptoms + 1
        bot.send_quick_replies_message(sender_id, '{} having cold or clammy skin ?'.format(phrase), ccs)
    ''' 
    wbcb = {"content_type":"text","title":"Yes","payload":'yes_wbcb'},{"content_type":"text","title":"No","payload":'no_wbcb'}
    if text == 'yes_ccs' and answer == 'breathing': 
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} WBC below 4.5 ?'.format(phrase), wbcb) 
    if text == 'no_ccs' and answer == 'breathing':
        bot.send_quick_replies_message(sender_id, '{} WBC below 4.5 ?'.format(phrase), wbcb)
    
    platb = {"content_type":"text","title":"Yes","payload":'yes_platb'},{"content_type":"text","title":"No","payload":'no_platb'}
    if text == 'yes_wbcb' and answer == 'breathing': 
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} Platelet below 150 ?'.format(phrase), platb) 
    if text == 'no_wbcb' and answer == 'breathing': 
        bot.send_quick_replies_message(sender_id, '{} Platelet below 150 ?'.format(phrase), platb) 
    '''
    #22
    if text == 'yes_ccs' and answer == 'breathing': 
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == True:
            bot.send_text_message(sender_id, "{} have 75% change you might have dengue.".format(phrase2.capitalize()))
            bot.send_text_message(sender_id, "{} must undergo a laboratory test for blood.".format(phrase2.capitalize()))
            bot.send_text_message(sender_id, "If WBC is below 4.5 and platelet below 150")
            bot.send_text_message(sender_id, "Then {} are currently in dengue.".format(phrase2))
        elif get_average(count_yes, total_symptoms) == False:
            pass
    else:
        pass
    if text == 'no_ccs' and answer == 'breathing': 
        if get_average(count_yes, total_symptoms) == True:
            bot.send_text_message(sender_id, "{} have 75% change you might have dengue.".format(phrase2.capitalize()))
            bot.send_text_message(sender_id, "{} must undergo a laboratory test for blood.".format(phrase2.capitalize()))
            bot.send_text_message(sender_id, "If WBC is below 4.5 and platelet below 150")
            bot.send_text_message(sender_id, "Then {} are currently in dengue.".format(phrase2))
        elif get_average(count_yes, total_symptoms) == False:
            pass
    else:
        pass
    count_yes = 0
    total_symptoms = 0
     #End Dengue
    #Gastroenteritis
    if text =='diarrhea':
        count_yes += 1
        total_symptoms += 1
        Mongo.set_answer(users,sender_id,'diarrhea')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
        
    if text =='yes_fever' and answer == 'diarrhea':
        count_yes += 1
        total_symptoms += 1
        dm3days = {"content_type":"text","title":"Yes","payload":'yes_diarrheamore3days'},{"content_type":"text","title":"No","payload":'no_diarrheamore3days'}                    
        bot.send_quick_replies_message(sender_id, 'Is diarrhea occurs more than 3 times in one day ?', dm3days)
    
    lws  = {"content_type":"text","title":"Yes","payload":'yes_lws'},{"content_type":"text","title":"No","payload":'no_lws'}   
    if text == 'yes_diarrheamore3days':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'having loose stools or watery stools ?', lws)
    if text == 'no_diarrheamore3days':  
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'having loose stools or watery stools ?', lws)
        
    ilbm = {"content_type":"text","title":"Yes","payload":'yes_ilbm'},{"content_type":"text","title":"No","payload":'no_ilbm'}     
    if text == 'yes_lws' and answer =='diarrhea':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing incontinence or loss of control over bowel motions ?'.format(phrase), ilbm)
    if text == 'no_lws' and answer =='diarreha':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing incontinence or loss of control over bowel motions?'.format(phrase), ilbm)
    if text =='no_fever' and answer == 'diarreha':  
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing incontinence or loss of control over bowel motions?'.format(phrase), ilbm)
    
    vocrs = {"content_type":"text","title":"Yes","payload":'yes_vocrs'},{"content_type":"text","title":"No","payload":'no_vorcs'}    
    if text == 'yes_ilbm' and answer =='diarrhea':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} does vomiting occurs ?'.format(phrase), vocrs)
    if text == 'no_ilbm' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} does vomiting occurs ?'.format(phrase), vocrs)
    
    apors = {"content_type":"text","title":"Yes","payload":'yes_apors'},{"content_type":"text","title":"No","payload":'no_apors'} 
    if text == 'yes_vocrs' and answer =='diarrhea':
        total_symptoms += 1
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), apors)
    if text == 'no_vocrs' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), apors)
    
    abc = {"content_type":"text","title":"Yes","payload":'yes_abc'},{"content_type":"text","title":"No","payload":'no_abc'} 
    if text == 'yes_apors' and answer =='diarrhea':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having abdominal cramps ?'.format(phrase), abc) 
    if text == 'no_apors' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having abdominal cramps ?'.format(phrase), abc)
    
    bwo = {"content_type":"text","title":"Yes","payload":'yes_bwo'},{"content_type":"text","title":"No","payload":'no_bwo'}
    if text == 'yes_abc' and answer =='diarrhea':
        total_symptoms += 1    
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having body weakness ?'.format(phrase), bwo) 
    if text == 'no_abc' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having body weakness ?'.format(phrase), bwo) 

    oma = {"content_type":"text","title":"Yes","payload":'yes_oma'},{"content_type":"text","title":"No","payload":'no_oma'}
    if text == 'yes_bwo' and answer =='diarrhea':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having occasional muscle ache ?'.format(phrase), oma) 
    if text == 'no_bwo' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having occasional muscle aches ?'.format(phrase), oma)
    
    hos = {"content_type":"text","title":"Yes","payload":'yes_hos'},{"content_type":"text","title":"No","payload":'no_hos'}
    if text == 'yes_oma' and answer =='diarrhea':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), hos) 
    if text == 'no_oma' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), hos) 
    
    tgb = {"content_type":"text","title":"Yes","payload":'yes_tgb'},{"content_type":"text","title":"No","payload":'no_tgb'}
    if text == 'yes_hos' and answer =='diarrhea':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing tiredness and general body weakness ?'.format(phrase), tgb) 
    if text == 'no_hos' and answer == 'diarrhea':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing tiredness and general body weakness ?'.format(phrase), tgb) 
        
    if get_average(count_yes, total_symptoms) == True:
        bot.send_text_message(sender_id, "{} have 75% change you might have Gastroenteritis.".format(phrase2.capitalize()))
    elif get_average(count_yes, total_symptoms) == False:
        pass
    count_yes = 0    
    total_symptoms = 0
    #End gastro
     #tonsil
    if text =='swallowing':
        count_yes += 1
        total_symptoms += 1
        Mongo.set_answer(users,sender_id,'swallowing')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
    
    if text =='yes_fever' and answer == 'swallowing':
        count_yes += 1
        total_symptoms += 1
        soret = {"content_type":"text","title":"Yes","payload":'yes_sorethroat'},{"content_type":"text","title":"No","payload":'no_sorethroat'}                    
        bot.send_quick_replies_message(sender_id, 'having a sore throat ?', soret)
    
    chls  = {"content_type":"text","title":"Yes","payload":'yes_chls'},{"content_type":"text","title":"No","payload":'no_chls'}   
    if text == 'yes_sorethroat':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'having chills ?', chls)
    if text == 'no_sorethroat':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'having chills ?', chls)
    
    porap = {"content_type":"text","title":"Yes","payload":'yes_porap'},{"content_type":"text","title":"No","payload":'no_porap'}     
    if text == 'yes_chls' and answer =='swallowing':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing poor appetite ?'.format(phrase), porap)
    if text == 'no_chls' and answer =='swallowing':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing poor appetite?'.format(phrase), porap)
    if text =='no_fever' and answer == 'swallowing':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing poor appetite ?'.format(phrase), porap)
    
    rst = {"content_type":"text","title":"Yes","payload":'yes_rst'},{"content_type":"text","title":"No","payload":'no_rst'}    
    if text == 'yes_porap' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having red, swollen tonsils ?'.format(phrase), rst)
    if text == 'no_porap' and answer == 'swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having red swollen tonsils ?'.format(phrase), rst)
    
    wyc = {"content_type":"text","title":"Yes","payload":'yes_wyc'},{"content_type":"text","title":"No","payload":'no_wyc'} 
    if text == 'yes_rst' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing white or yellow coating or patches on the tonsils ?'.format(phrase), wyc)
    if text == 'no_rst' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing white or yellow coating or patches on the tonsils ?'.format(phrase), wyc)
    
    etg = {"content_type":"text","title":"Yes","payload":'yes_etg'},{"content_type":"text","title":"No","payload":'no_etg'} 
    if text == 'yes_wyc' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having enlarged tender glands/lymph nodes in the neck ?'.format(phrase), etg)
    if text == 'no_wyc' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having enlarged tender glands/lymph nodes in the neck ?'.format(phrase), etg)

    smt = {"content_type":"text","title":"Yes","payload":'yes_smt'},{"content_type":"text","title":"No","payload":'no_smt'} 
    if text == 'yes_etg' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having scratchy, muffled or throaty voice ?'.format(phrase), smt)
    if text == 'no_etg' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having scratchy, muffled or throaty voice ?'.format(phrase), smt)
    
    bbo = {"content_type":"text","title":"Yes","payload":'yes_bbo'},{"content_type":"text","title":"No","payload":'no_bbo'} 
    if text == 'yes_smt' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having bad breath occurs ?'.format(phrase), bbo)
    if text == 'no_smt' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having sbad breath occurs ?'.format(phrase), bbo)  
       
    stifn = {"content_type":"text","title":"Yes","payload":'yes_stifn'},{"content_type":"text","title":"No","payload":'no_stifn'} 
    if text == 'yes_bbo' and answer =='swallowing':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having stiff neck ?'.format(phrase), stifn)
    if text == 'no_bbo' and answer =='swallowing':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having stiff neck ?'.format(phrase), stifn)
       
    head = {"content_typne":"text","title":"Yes","payload":'yes_head'},{"content_type":"text","title":"No","payload":'no_head'} 
    if text == 'yes_stifn' and answer =='swallowing': 
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), head)
    if text == 'no_stifn' and answer =='swallowing': 
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), head)
    
    thrp = {"content_typne":"text","title":"Yes","payload":'yes_thrp'},{"content_type":"text","title":"No","payload":'no_thrp'} 
    if text == 'yes_head' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having throat pain or tenderness ?'.format(phrase), thrp)
    if text == 'no_head' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having throat pain or tenderness ?'.format(phrase), thrp)
    
    dbt = {"content_typne":"text","title":"Yes","payload":'yes_dbt'},{"content_type":"text","title":"No","payload":'no_dbt'} 
    if text == 'yes_thrp' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having difficulty breathing through the mouth ?'.format(phrase), dbt)
    if text == 'no_thrp' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having difficulty breathing through the mouth ?'.format(phrase), dbt)
    
    sgn = {"content_typne":"text","title":"Yes","payload":'yes_sgn'},{"content_type":"text","title":"No","payload":'no_sgn'}
    if text == 'yes_dbt' and answer =='swallowing':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having swollen glands in the neck or jaw area ?'.format(phrase), sgn)
    if text == 'no_dbt' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having swollen glands in the neck or jaw area ?'.format(phrase), sgn)
    
    pin = {"content_typne":"text","title":"Yes","payload":'yes_pin'},{"content_type":"text","title":"No","payload":'no_pin'}
    if text == 'yes_sgn' and answer =='swallowing': 
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having pain in the neck ?'.format(phrase), pin)
    if text == 'no_sgn' and answer =='swallowing': 
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having pain in the neck ?'.format(phrase), pin)

    cgrs = {"content_typne":"text","title":"Yes","payload":'yes_cgrs'},{"content_type":"text","title":"No","payload":'no_cgrs'}
    if text == 'yes_pin' and answer =='swallowing':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cgrs)
    if text == 'no_pin' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cgrs)

    furt = {"content_typne":"text","title":"Yes","payload":'yes_furt'},{"content_type":"text","title":"No","payload":'no_furt'}
    if text == 'yes_cgrs' and answer =='swallowing':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} furry tounge ?'.format(phrase), furt)
    if text == 'no_cgrs' and answer =='swallowing':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} furry tounge ?'.format(phrase), furt)
        
    if get_average(count_yes, total_symptoms) == True:
        bot.send_text_message(sender_id, "{} have 75% change you might have Tonsillitis.".format(phrase2.capitalize()))
    elif get_average(count_yes, total_symptoms) == False:
        pass
    count_yes = 0    
    total_symptoms = 0
    #End tonsil
     #UTI
    if text =='urination':
        count_yes += 1
        total_symptoms += 1
        Mongo.set_answer(users,sender_id,'urination')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
        
    if text =='yes_fever' and answer == 'urination':
        count_yes += 1
        total_symptoms += 1
        stoma = {"content_type":"text","title":"Yes","payload":'yes_stomachace'},{"content_type":"text","title":"No","payload":'no_stomachache'}                    
        bot.send_quick_replies_message(sender_id, 'having a stomachache ?', stoma)
    
    vomit  = {"content_type":"text","title":"Yes","payload":'yes_vomit'},{"content_type":"text","title":"No","payload":'no_vomit'}   
    if text == 'yes_stomachache':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'experiencing vomiting ?', vomit)
    if text == 'no_stomachache':  
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'experiencing vomiting ?', vomit)
    
    piu = {"content_type":"text","title":"Yes","payload":'yes_piu'},{"content_type":"text","title":"No","payload":'no_pui'}     
    if text == 'yes_vomit' and answer =='urination':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing pain in urethra ?'.format(phrase), piu)
    if text == 'no_vomit' and answer =='urination':   
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing pain in urethra ?'.format(phrase), piu)
    if text =='no_fever' and answer == 'urination':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing pain in urethra ?'.format(phrase), piu)
    
    fru = {"content_type":"text","title":"Yes","payload":'yes_fru'},{"content_type":"text","title":"No","payload":'no_fru'}    
    if text == 'yes_piu' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having frequent urination ?'.format(phrase), fru)
    if text == 'no_piu' and answer == 'urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having frequent urination ?'.format(phrase), fru)
        
    abpc = {"content_type":"text","title":"Yes","payload":'yes_abpc'},{"content_type":"text","title":"No","payload":'no_abpc'}      
    if text == 'yes_fru' and answer =='urination': 
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), abpc)
    if text == 'no_fru' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), abpc)
      
    dysur = {"content_type":"text","title":"Yes","payload":'yes_dysur'},{"content_type":"text","title":"No","payload":'no_dysur'}
    if text == 'yes_abpc' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having Dysuria  or discomfort when urinating ?'.format(phrase), dysur)
    if text == 'no_abpc' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having Dysuria  or discomfort when urinating ?'.format(phrase), dysur)
    
    flank = {"content_type":"text","title":"Yes","payload":'yes_flank'},{"content_type":"text","title":"No","payload":'no_flank'}
    if text == 'yes_dysur' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having flank pain ?'.format(phrase), flank)
    if text == 'no_dysur' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having flank pain ?'.format(phrase), flank)
    
    dyu = {"content_type":"text","title":"Yes","payload":'yes_dyu'},{"content_type":"text","title":"No","payload":'no_dyu'}
    if text == 'yes_flank' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having dark yellow urine ?'.format(phrase), dyu)
    if text == 'no_flank' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having dark yellow urine ?'.format(phrase), dyu)

    burn = {"content_type":"text","title":"Yes","payload":'yes_burn'},{"content_type":"text","title":"No","payload":'no_burn'}
    if text == 'yes_dyu' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having burning feeling when urinating ?'.format(phrase), burn)
    if text == 'no_dyu' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having burning feeling when urinating ?'.format(phrase), burn)

    foi = {"content_type":"text","title":"Yes","payload":'yes_foi'},{"content_type":"text","title":"No","payload":'no_foi'}
    if text == 'yes_burn' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having frequent or intense urge to urinate, even though little comes out when you do ?'.format(phrase), foi)
    if text == 'no_burn' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having frequent or intense urge to urinate, even though little comes out when you do ?'.format(phrase), foi)
        
    pop = {"content_type":"text","title":"Yes","payload":'yes_pop'},{"content_type":"text","title":"No","payload":'no_pop'}
    if text == 'yes_foi' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having fain or pressure in your back or lower abdomen ?'.format(phrase), pop)
    if text == 'no_foi' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having fain or pressure in your back or lower abdomen ?'.format(phrase), pop)
        
    cdb = {"content_type":"text","title":"Yes","payload":'yes_cdb'},{"content_type":"text","title":"No","payload":'no_cdb'}   
    if text == 'yes_pop' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cloudy, dark, bloody, or strange-smelling urine ?'.format(phrase), cdb)
    if text == 'no_pop' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cloudy, dark, bloody, or strange-smelling urine ?'.format(phrase), cdb)
        
    fts = {"content_type":"text","title":"Yes","payload":'yes_fts'},{"content_type":"text","title":"No","payload":'no_fts'}   
    if text == 'yes_cdb' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having feeling tired or shaky ?'.format(phrase), fts)
    if text == 'no_cdb' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having feeling tired or shaky ?'.format(phrase), fts)
        
    uar = {"content_type":"text","title":"Yes","payload":'yes_uar'},{"content_type":"text","title":"No","payload":'no_uar'}
    if text == 'yes_fts' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having urine appears red, bright pink or cola-colored which is a sign of blood in the urine ?'.format(phrase), uar)
    if text == 'no_fts' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having urine appears red, bright pink or cola-colored which is a sign of blood in the urine ?'.format(phrase), uar)
        
    naus = {"content_type":"text","title":"Yes","payload":'yes_naus'},{"content_type":"text","title":"No","payload":'no_naus'}
    if text == 'yes_uar' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having nausea ?'.format(phrase), naus)
    if text == 'no_uar' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having nausea ?'.format(phrase), naus)
    
    wbnc = {"content_type":"text","title":"Yes","payload":'yes_wbnc'},{"content_type":"text","title":"No","payload":'no_wbnc'}
    if text == 'yes_naus' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), wbnc)
    if text == 'no_naus' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), wbnc)
        
    pro = {"content_type":"text","title":"Yes","payload":'yes_pro'},{"content_type":"text","title":"No","payload":'no_pro'}
    if text == 'yes_wbnc' and answer =='urination':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), pro)
    if text == 'no_wbnc' and answer =='urination':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), pro)
        
    if get_average(count_yes, total_symptoms) == True:
        bot.send_text_message(sender_id, "{} have 75% change you might have UTI.".format(phrase2.capitalize()))
    elif get_average(count_yes, total_symptoms) == False:
        pass
    count_yes = 0    
    total_symptoms = 0
    #End UTI
        
     #Flu
    if text =='body':
        count_yes += 1
        total_symptoms += 1
        Mongo.set_answer(users,sender_id,'body') 
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
    
    if text =='yes_fever' and answer == 'body':
        count_yes += 1
        total_symptoms += 1
        nas = {"content_type":"text","title":"Yes","payload":'yes_nasaldischarge'},{"content_type":"text","title":"No","payload":'no_nasaldischarge'}                    
        bot.send_quick_replies_message(sender_id, 'having a nasal discharge ?', nas)
        
    fvo  = {"content_type":"text","title":"Yes","payload":'yes_fvo'},{"content_type":"text","title":"No","payload":'no_fvo'}   
    if text == 'yes_nasaldischarge': 
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'fever is over 38 degress ?', fvo)
    if text == 'no_nasaldischarge':   
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, 'fever is over 38 degress ?', fvo)
    
    musc = {"content_type":"text","title":"Yes","payload":'yes_musc'},{"content_type":"text","title":"No","payload":'no_musc'}     
    if text == 'yes_fvo' and answer =='body':  
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing muscle pain ?'.format(phrase), musc)
    if text == 'no_fvo' and answer =='body':   
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing muscle pain ?'.format(phrase), musc)
    if text =='no_fever' and answer == 'body':    
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} experiencing muscle pain ?'.format(phrase), musc)
    
    cough = {"content_type":"text","title":"Yes","payload":'yes_cough'},{"content_type":"text","title":"No","payload":'no_cough'}    
    if text == 'yes_musc' and answer =='body':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cough)
    if text == 'no_musc' and answer == 'body':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cough)
        
    dpc = {"content_type":"text","title":"Yes","payload":'yes_dpc'},{"content_type":"text","title":"No","payload":'no_dpc'}
    if text == 'yes_cough' and answer =='body':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having dry, persistent cough ?'.format(phrase), dpc)
    if text == 'no_cough' and answer =='body':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having dry, persistent cough ?'.format(phrase), dpc)
        
    cold = {"content_type":"text","title":"Yes","payload":'yes_cold'},{"content_type":"text","title":"No","payload":'no_cold'}   
    if text == 'yes_dpc' and answer =='body':
        count_yes += 1
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cold ?'.format(phrase), cold)
    if text == 'no_dpc' and answer =='body':
        total_symptoms += 1
        bot.send_quick_replies_message(sender_id, '{} having cold ?'.format(phrase), cold)
        #dre tiwasa
    rn = {"content_type":"text","title":"Yes","payload":'yes_rn'},{"content_type":"text","title":"No","payload":'no_rn'}
    if text == 'yes_cold' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having runny nose ?'.format(phrase), rn)
    if text == 'no_cold' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having runny nose ?'.format(phrase), rn)
            
    nac = {"content_type":"text","title":"Yes","payload":'yes_nac'},{"content_type":"text","title":"No","payload":'no_nac'}
    if text == 'yes_rn' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having nasal congestion ?'.format(phrase), nac)
    if text == 'no_rn' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having nasal congestion ?'.format(phrase), nac)
        
    pora = {"content_type":"text","title":"Yes","payload":'yes_pora'},{"content_type":"text","title":"No","payload":'no_pora'}
    if text == 'yes_nac' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having poor appetite ?'.format(phrase), pora)
    if text == 'no_nac' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having poor appetite ?'.format(phrase), pora)
    
    headach = {"content_type":"text","title":"Yes","payload":'yes_headach'},{"content_type":"text","title":"No","payload":'no_headach'}
    if text == 'yes_pora' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), headach)
    if text == 'no_pora' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), headach)
        
    cas = {"content_type":"text","title":"Yes","payload":'yes_cas'},{"content_type":"text","title":"No","payload":'no_cas'}
    if text == 'yes_headach' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having chills and sweats ?'.format(phrase), cas)
    if text == 'no_headach' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having chills and sweats ?'.format(phrase), cas)
   
    fati = {"content_type":"text","title":"Yes","payload":'yes_fati'},{"content_type":"text","title":"No","payload":'no_fati'}
    if text == 'yes_cas' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having fatigue ?'.format(phrase), fati)
    if text == 'no_cas' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having fatigue ?'.format(phrase), fati)

    fw = {"content_type":"text","title":"Yes","payload":'yes_fw'},{"content_type":"text","title":"No","payload":'no_fw'}
    if text == 'yes_fati' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} feels weak ?'.format(phrase), fw)
    if text == 'no_fati' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} feels weak ?'.format(phrase), fw)
     
    sthroat = {"content_type":"text","title":"Yes","payload":'yes_sthroat'},{"content_type":"text","title":"No","payload":'no_sthroat'}
    if text == 'yes_fw' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having sore throat ?'.format(phrase), sthroat)
    if text == 'no_fw' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having sore throat ?'.format(phrase), sthroat)
        
    pte = {"content_type":"text","title":"Yes","payload":'yes_pte'},{"content_type":"text","title":"No","payload":'no_pte'}
    if text == 'yes_sthroat' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having pain and tiredness around the eyes ?'.format(phrase), pte)
    if text == 'no_sthroat' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having pain and tiredness around the eyes ?'.format(phrase), pte)
        
    tbs = {"content_type":"text","title":"Yes","payload":'yes_tbs'},{"content_type":"text","title":"No","payload":'no_tbs'}
    if text == 'yes_pte' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having trouble breathing or shortness of breathing ?'.format(phrase), tbs)
    if text == 'no_pte' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having trouble breathing or shortness of breathing ?'.format(phrase), tbs)
            
    ppc = {"content_type":"text","title":"Yes","payload":'yes_ppc'},{"content_type":"text","title":"No","payload":'no_ppc'}  
    if text == 'yes_tbs' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having pain or pressure in your chest or belly ?'.format(phrase), ppc)
    if text == 'no_tbs' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having pain or pressure in your chest or belly ?'.format(phrase), ppc)
        
    sdiz = {"content_type":"text","title":"Yes","payload":'yes_sdiz'},{"content_type":"text","title":"No","payload":'no_sdiz'}
    if text == 'yes_ppc' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having sudden dizziness ?'.format(phrase), sdiz)
    if text == 'no_ppc' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having sudden dizziness ?'.format(phrase), sdiz)
    
    css = {"content_type":"text","title":"Yes","payload":'yes_sdiz'},{"content_type":"text","title":"No","payload":'no_sdiz'}
    if text == 'yes_sdiz' and answer =='body':
        count_yes += 1
        bot.send_quick_replies_message(sender_id, '{} having cold sweats and shivers ?'.format(phrase), css)
    if text == 'no_sdiz' and answer =='body':
        bot.send_quick_replies_message(sender_id, '{} having cold sweats and shivers ?'.format(phrase), css)
        #end flu
        
    percentage = count_yes / 20 * 100
    if int(percentage) >=75:
        bot.send_text_message(sender_id, "You have 75% change you might have FLU.")
    else:
        pass
    count_yes = 0 
    if text == 'yes_correct1':
        if relation == 'myself':
           bot.send_text_message(sender_id,'And you are {} kg in weight'.format(weight))
        elif relation == 'mychild':
           bot.send_text_message(sender_id,"And your child is {} kg in weight".format(age))
        elif relation == 'someone':
           bot.send_text_message(sender_id,"And the child's weight is {} kg.".format(name, age))
        bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)  
            
    if text == 'no_correct1':
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
    if text =='mychild':
        Mongo.create_patient(patient, sender_id, '', '', '', 'mychild')
        Mongo.set_ask(users, sender_id, "Whats the name of your child?")
        bot.send_text_message(sender_id, "Whats the name of your child {}?".format(first_name(sender_id)))    
    if text =='someone':
        Mongo.create_patient(patient, sender_id, '', '', '', 'someone')
        Mongo.set_ask(users, sender_id, "Whats the name of the child?")
        bot.send_text_message(sender_id, "Whats the name the child {}?".format(first_name(sender_id)))
    #2.1
    if text=='physical':
        listofconcern = 'Dengue,\nGastroenteritis,\nUrinary Tract Infection,\nTonsilitis,\nFLU\nand minor symptoms simply like soar throat, back pain, cold and so on.'
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
            elif terms == 'No':
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
