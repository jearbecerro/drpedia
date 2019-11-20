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
average = 0
count_yes = 0
total_symptoms = 0
has_fever = False
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
    global name, age, weight, relation , phrase, count_yes, total_symptoms
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
        count_yes = patient_data['count_yes']
        total_symptoms = patient_data['total_symptoms']
    else: 
        pass
    #Mental Health{
    if text.lower() in ("attention deficit hyperactivity disorder", "adhd") and answer == 'mental':#if user send text 'adhd'
        choose_howto(sender_id,'remedies_adhd','medication_adhd','about_adhd','ADHD')
    elif text.lower() in ("oppositional defiant disorder", "odd")  and answer == 'mental':
        choose_howto(sender_id,'remedies_odd','medication_odd','about_odd','ODD')   
    elif text.lower() in ("autism spectrum disorder", "asd", "autism") and answer == 'mental':
        choose_howto(sender_id,'remedies_autism','medication_autism','about_autism','Autism')   
    elif text.lower() in ("anxiety disorder", "anxiety","ad") and answer == 'mental':
        choose_howto(sender_id,'remedies_anxiety','medication_anxiety','about_anxiety','Anxiety')
    elif text.lower() in ("depression", "depression disorder","depress") and answer == 'mental':
        choose_howto(sender_id,'remedies_depression','medication_depression','about_depression','Depression')
    elif text.lower() in ("bipolar disorder", "bipolar","bd") and answer == 'mental':
        choose_howto(sender_id,'remedies_bipolar','medication_bipolar','about_bipolar','Bipolar')
    elif text.lower() in ("learning disorders", "learning","ld") and answer == 'mental':
        choose_howto(sender_id,'remedies_learning','medication_learning','about_learning','Learning Disorder')
    else:
        bot.send_text_message(sender_id,'Just only type your suspected mental health listed above {}.'.format(first_name))
        
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
        print(percentage,'%')
        return int(round(percentage))
        
   
#if user tap a button from a quick reply
def received_qr(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    text = event["message"]["quick_reply"]["payload"]
    global created_at, last_seen, fname, lname, ask, answer, terms
    global name, age, weight, relation, phrase, phrase2, myself, has_fever, count_yes, total_symptoms, average
    
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
        count_yes = int(patient_data['count_yes'])
        total_symptoms = int(patient_data['total_symptoms'])
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
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        Mongo.set_answer(users,sender_id,'breathing')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
        
    if text =='yes_fever' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        has_fever = True
        print(count_yes, total_symptoms)
        f2days = {"content_type":"text","title":"Yes","payload":'yes_fever2days'},{"content_type":"text","title":"No","payload":'no_fever2days'}                    
        bot.send_quick_replies_message(sender_id, 'Is the fever occurs 2 days or more?', f2days)
        
    fnight  = {"content_type":"text","title":"Yes","payload":'yes_fnight'},{"content_type":"text","title":"No","payload":'no_fnight'}   
    if text == 'yes_fever2days': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, 'Is the fever occurs sunset to sunset or in night time?', fnight)
    if text == 'no_fever2days':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is the fever occurs sunset to sunset or in night time?', fnight)
        
    ha = {"content_type":"text","title":"Yes","payload":'yes_ha'},{"content_type":"text","title":"No","payload":'no_ha'}     
    if text == 'yes_fnight' and answer =='breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} experiencing headache?'.format(phrase), ha)
    if text == 'no_fnight' and answer =='breathing':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing headache?'.format(phrase), ha)
    if text =='no_fever' and answer == 'breathing':    
        total = total_symptoms + 1
        Mongo.set_patient(patient, sender_id, 'total_symptoms', str(total))
        bot.send_quick_replies_message(sender_id, '{} experiencing headache?'.format(phrase), ha)
        
    bp = {"content_type":"text","title":"Yes","payload":'yes_bp'},{"content_type":"text","title":"No","payload":'no_bp'}    
    if text == 'yes_ha' and answer =='breathing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} experiencing body pain?'.format(phrase), bp)
    if text == 'no_ha' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing body pain?'.format(phrase), bp)
    
    v = {"content_type":"text","title":"Yes","payload":'yes_v'},{"content_type":"text","title":"No","payload":'no_v'}    
    if text == 'yes_bp' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} experiencing vomiting?'.format(phrase), v)
    if text == 'no_bp' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing vomiting?'.format(phrase), v)
        
    if text == 'yes_v' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        vo3 = {"content_type":"text","title":"Yes","payload":'yes_vo3'},{"content_type":"text","title":"No","payload":'no_vo3'} 
        bot.send_quick_replies_message(sender_id, 'Is vomiting occurs at least 3 times within day?', vo3)      
    
    ap = {"content_type":"text","title":"Yes","payload":'yes_ap'},{"content_type":"text","title":"No","payload":'no_ap'}  
    if text == 'no_v' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing Abdominal Pain ?'.format(phrase), ap )   
           
    vbs = {"content_type":"text","title":"Yes","payload":'yes_vbs'},{"content_type":"text","title":"No","payload":'no_vbs'} 
    if text == 'yes_vo3' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} vomiting blood, or blood in the stool'.format(phrase), vbs)  
    if text == 'no_vo3' and answer == 'breathing':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} vomiting blood, or blood in the stool'.format(phrase), vbs)  
        
    if text == 'yes_vbs' and answer == 'breathing':   
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing Abdominal Pain ?'.format(phrase), ap )    
    if text == 'no_vbs' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing Abdominal Pain ?'.format(phrase), ap )    
    
    pa = {"content_type":"text","title":"Yes","payload":'yes_pa'},{"content_type":"text","title":"No","payload":'no_pa'}   
    if text == 'yes_ap' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having poor appetite?'.format(phrase), pa)      
    if text == 'no_ap' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
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
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having rashes 2 days or more after fever?'.format(phrase), r2f)
            
    if text == 'no_pa' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having rashes 2 days or more after fever?'.format(phrase), r2f) 
    pbe = {"content_type":"text","title":"Yes","payload":'yes_pbe'},{"content_type":"text","title":"No","payload":'no_pbe'}   
    if text == 'yes_r2f' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain behind the eyes?'.format(phrase), pbe)   
    if text == 'no_r2f' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain behind the eyes?'.format(phrase), pbe)
    
    fat = {"content_type":"text","title":"Yes","payload":'yes_fat'},{"content_type":"text","title":"No","payload":'no_fat'}
    if text == 'yes_pbe' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} fatigue?'.format(phrase), fat)       
    if text == 'no_pbe' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} fatigue?'.format(phrase), fat) 
        
    nas = {"content_type":"text","title":"Yes","payload":'yes_nas'},{"content_type":"text","title":"No","payload":'no_nas'} 
    if text == 'yes_fat' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} feeling nausea ?'.format(phrase), nas) 
    if text == 'no_fat' and answer == 'breathing':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} feeling nausea ?'.format(phrase), nas) 
        
    mbn = {"content_type":"text","title":"Yes","payload":'yes_mbn'},{"content_type":"text","title":"No","payload":'no_mbn'}
    if text == 'yes_nas' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having mild bleeding such as nose bleed, bleeding gums, or easy bruising  ?'.format(phrase), mbn) 
    if text == 'no_nas' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having mild bleeding such as nose bleed, bleeding gums, or easy brusing ?'.format(phrase), mbn) 
    
    tri = {"content_type":"text","title":"Yes","payload":'yes_tri'},{"content_type":"text","title":"No","payload":'no_tri'}
    if text == 'yes_mbn' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} feeling tired, restless, or irritable ?'.format(phrase), tri) 
    if text == 'no_mbn' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} feeling tired, restless, or irritable ?'.format(phrase), tri) 
    
    ccs = {"content_type":"text","title":"Yes","payload":'yes_ccs'},{"content_type":"text","title":"No","payload":'no_ccs'}
    if text == 'yes_tri' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        print(count_yes, total_symptoms)
        bot.send_quick_replies_message(sender_id, '{} having cold or clammy skin ?'.format(phrase), ccs) 
    if text == 'no_tri' and answer == 'breathing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
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
    take = {"content_type":"text","title":"Yes","payload":'yes_inc'},{"content_type":"text","title":"No","payload":'no_inc'}
    if text == 'yes_ccs' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
        
    if text == 'no_ccs' and answer == 'breathing': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
    right = {"content_type":"text","title":"Yes","payload":'yes_ri'},{"content_type":"text","title":"No","payload":'no_ri'}
    if text == 'no_inc' and answer == 'breathing':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Dengue.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "{} must undergo a laboratory test for blood.".format(phrase2.capitalize()))
            bot.send_text_message(sender_id, "After the lab test,\nif the white blood cell is below 4.5 and the platelet is below 150.")
            bot.send_text_message(sender_id, "Then I can determine that {} currently having dengue.".format(phrase2))
            choose_howto(sender_id,'remedies_dengue','medication_dengue','about_dengue','Dengue')
        elif get_average(count_yes, total_symptoms) <80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Dengue.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 80% or higher percentage rate base on symptoms that {} current have before I can determine that {} have dengue.".format(phrase2,phrase2))
            bot.send_text_message(sender_id, "So {},\nthese are the symptoms, that {} currently suffering: ".format(first_name(sender_id),phrase2))
            bot.send_quick_replies_message(sender_id, 'Right?'.format(phrase2), right) 
    if text == 'yes_ri' or 'no_ri' and answer == 'breathing':
        pass #give medication/ remedies for those symptoms 
    if text == 'yes_inc' and answer == 'breathing':       
        pass#NLU

     #End Dengue
    #Gastroenteritis
    if text =='diarrhea':
        Mongo.set_answer(users,sender_id,'diarrhea')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
        
    if text =='yes_fever' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        dm3days = {"content_type":"text","title":"Yes","payload":'yes_diarrheamore3days'},{"content_type":"text","title":"No","payload":'no_diarrheamore3days'}                    
        bot.send_quick_replies_message(sender_id, 'Is diarrhea occurs more than 3 times in one day ?', dm3days)
    
    lws  = {"content_type":"text","title":"Yes","payload":'yes_lws'},{"content_type":"text","title":"No","payload":'no_lws'}   
    if text == 'yes_diarrheamore3days':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having loose stools or watery stools ?'.format(phrase), lws)
    if text == 'no_diarrheamore3days':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'having loose stools or watery stools ?', lws)
        
    ilbm = {"content_type":"text","title":"Yes","payload":'yes_ilbm'},{"content_type":"text","title":"No","payload":'no_ilbm'}     
    if text == 'yes_lws' and answer =='diarrhea':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing incontinence or loss of control over bowel motions ?'.format(phrase), ilbm)
    if text == 'no_lws' and answer =='diarreha':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing incontinence or loss of control over bowel motions?'.format(phrase), ilbm)
    if text =='no_fever' and answer == 'diarreha':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing incontinence or loss of control over bowel motions?'.format(phrase), ilbm)
    
    vocrs = {"content_type":"text","title":"Yes","payload":'yes_vocrs'},{"content_type":"text","title":"No","payload":'no_vorcs'}    
    if text == 'yes_ilbm' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing vomitting ?'.format(phrase), vocrs)
    if text == 'no_ilbm' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing vomitting ?'.format(phrase), vocrs)
    
    apors = {"content_type":"text","title":"Yes","payload":'yes_apors'},{"content_type":"text","title":"No","payload":'no_apors'} 
    if text == 'yes_vocrs' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), apors)
    if text == 'no_vocrs' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), apors)
    
    abc = {"content_type":"text","title":"Yes","payload":'yes_abc'},{"content_type":"text","title":"No","payload":'no_abc'} 
    if text == 'yes_apors' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1) 
        bot.send_quick_replies_message(sender_id, '{} having abdominal cramps ?'.format(phrase), abc) 
    if text == 'no_apors' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having abdominal cramps ?'.format(phrase), abc)
    
    bwo = {"content_type":"text","title":"Yes","payload":'yes_bwo'},{"content_type":"text","title":"No","payload":'no_bwo'}
    if text == 'yes_abc' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having body weakness ?'.format(phrase), bwo) 
    if text == 'no_abc' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having body weakness ?'.format(phrase), bwo) 

    oma = {"content_type":"text","title":"Yes","payload":'yes_oma'},{"content_type":"text","title":"No","payload":'no_oma'}
    if text == 'yes_bwo' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having occasional muscle ache ?'.format(phrase), oma) 
    if text == 'no_bwo' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having occasional muscle aches ?'.format(phrase), oma)
    
    hos = {"content_type":"text","title":"Yes","payload":'yes_hos'},{"content_type":"text","title":"No","payload":'no_hos'}
    if text == 'yes_oma' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), hos) 
    if text == 'no_oma' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), hos) 
    
    tgb = {"content_type":"text","title":"Yes","payload":'yes_tgb'},{"content_type":"text","title":"No","payload":'no_tgb'}
    if text == 'yes_hos' and answer =='diarrhea':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing tiredness and general body weakness ?'.format(phrase), tgb) 
    if text == 'no_hos' and answer == 'diarrhea':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing tiredness and general body weakness ?'.format(phrase), tgb) 
        
    if text == 'yes_tgb' and answer == 'diarrhea': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
        
    if text == 'no_tgb' and answer == 'diarrhea': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
    
    if text == 'no_inc' and answer == 'diarrhea':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} have Gastroenteritis.".format(phrase2,average,phrase2))
            choose_howto(sender_id,'remedies_gastro','medication_gastro','about_gastro','Gastroenteritis')
        elif get_average(count_yes, total_symptoms) <80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Gastroenteritis.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 80% or higher percentage rate base on symptoms that {} current have.\nBefore I can determine that {} have Gastroenteritis.".format(phrase2,phrase2))
            bot.send_text_message(sender_id, "So {},\nthese are the symptoms, that {} currently suffering: ".format(first_name(sender_id),phrase2))
            bot.send_quick_replies_message(sender_id, 'Right?'.format(phrase2), right) 
    if text == 'yes_ri' or 'no_ri' and answer == 'diarrhea' :
        pass #give medication/ remedies for those symptoms 
    if text == 'yes_inc' and answer == 'diarrhea':       
        pass#NLU     
   
    #End gastro
     #tonsil
    if text =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        Mongo.set_answer(users,sender_id,'swallowing')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
    
    if text =='yes_fever' and answer == 'swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        soret = {"content_type":"text","title":"Yes","payload":'yes_sorethroat'},{"content_type":"text","title":"No","payload":'no_sorethroat'}                    
        bot.send_quick_replies_message(sender_id, 'having a sore throat ?', soret)
    
    chls  = {"content_type":"text","title":"Yes","payload":'yes_chls'},{"content_type":"text","title":"No","payload":'no_chls'}   
    if text == 'yes_sorethroat':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'having chills ?', chls)
    if text == 'no_sorethroat':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'having chills ?', chls)
    
    porap = {"content_type":"text","title":"Yes","payload":'yes_porap'},{"content_type":"text","title":"No","payload":'no_porap'}     
    if text == 'yes_chls' and answer =='swallowing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing poor appetite ?'.format(phrase), porap)
    if text == 'no_chls' and answer =='swallowing':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing poor appetite?'.format(phrase), porap)
    if text =='no_fever' and answer == 'swallowing':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing poor appetite ?'.format(phrase), porap)
    
    rst = {"content_type":"text","title":"Yes","payload":'yes_rst'},{"content_type":"text","title":"No","payload":'no_rst'}    
    if text == 'yes_porap' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having red, swollen tonsils ?'.format(phrase), rst)
    if text == 'no_porap' and answer == 'swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having red swollen tonsils ?'.format(phrase), rst)
    
    wyc = {"content_type":"text","title":"Yes","payload":'yes_wyc'},{"content_type":"text","title":"No","payload":'no_wyc'} 
    if text == 'yes_rst' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing white or yellow coating or patches on the tonsils ?'.format(phrase), wyc)
    if text == 'no_rst' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing white or yellow coating or patches on the tonsils ?'.format(phrase), wyc)
    
    etg = {"content_type":"text","title":"Yes","payload":'yes_etg'},{"content_type":"text","title":"No","payload":'no_etg'} 
    if text == 'yes_wyc' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having enlarged tender glands/lymph nodes in the neck ?'.format(phrase), etg)
    if text == 'no_wyc' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having enlarged tender glands/lymph nodes in the neck ?'.format(phrase), etg)

    smt = {"content_type":"text","title":"Yes","payload":'yes_smt'},{"content_type":"text","title":"No","payload":'no_smt'} 
    if text == 'yes_etg' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having scratchy, muffled or throaty voice ?'.format(phrase), smt)
    if text == 'no_etg' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having scratchy, muffled or throaty voice ?'.format(phrase), smt)
    
    bbo = {"content_type":"text","title":"Yes","payload":'yes_bbo'},{"content_type":"text","title":"No","payload":'no_bbo'} 
    if text == 'yes_smt' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having bad breath occurs ?'.format(phrase), bbo)
    if text == 'no_smt' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having sbad breath occurs ?'.format(phrase), bbo)  
       
    stifn = {"content_type":"text","title":"Yes","payload":'yes_stifn'},{"content_type":"text","title":"No","payload":'no_stifn'} 
    if text == 'yes_bbo' and answer =='swallowing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having stiff neck ?'.format(phrase), stifn)
    if text == 'no_bbo' and answer =='swallowing':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having stiff neck ?'.format(phrase), stifn)
       
    head = {"content_typne":"text","title":"Yes","payload":'yes_head'},{"content_type":"text","title":"No","payload":'no_head'} 
    if text == 'yes_stifn' and answer =='swallowing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), head)
    if text == 'no_stifn' and answer =='swallowing': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having headache ?'.format(phrase), head)
    
    thrp = {"content_typne":"text","title":"Yes","payload":'yes_thrp'},{"content_type":"text","title":"No","payload":'no_thrp'} 
    if text == 'yes_head' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having throat pain or tenderness ?'.format(phrase), thrp)
    if text == 'no_head' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having throat pain or tenderness ?'.format(phrase), thrp)
    
    dbt = {"content_typne":"text","title":"Yes","payload":'yes_dbt'},{"content_type":"text","title":"No","payload":'no_dbt'} 
    if text == 'yes_thrp' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having difficulty breathing through the mouth ?'.format(phrase), dbt)
    if text == 'no_thrp' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having difficulty breathing through the mouth ?'.format(phrase), dbt)
    
    sgn = {"content_typne":"text","title":"Yes","payload":'yes_sgn'},{"content_type":"text","title":"No","payload":'no_sgn'}
    if text == 'yes_dbt' and answer =='swallowing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having swollen glands in the neck or jaw area ?'.format(phrase), sgn)
    if text == 'no_dbt' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having swollen glands in the neck or jaw area ?'.format(phrase), sgn)
    
    pin = {"content_typne":"text","title":"Yes","payload":'yes_pin'},{"content_type":"text","title":"No","payload":'no_pin'}
    if text == 'yes_sgn' and answer =='swallowing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain in the neck ?'.format(phrase), pin)
    if text == 'no_sgn' and answer =='swallowing': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain in the neck ?'.format(phrase), pin)

    cgrs = {"content_typne":"text","title":"Yes","payload":'yes_cgrs'},{"content_type":"text","title":"No","payload":'no_cgrs'}
    if text == 'yes_pin' and answer =='swallowing':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cgrs)
    if text == 'no_pin' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cgrs)

    furt = {"content_typne":"text","title":"Yes","payload":'yes_furt'},{"content_type":"text","title":"No","payload":'no_furt'}
    if text == 'yes_cgrs' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} furry tounge ?'.format(phrase), furt)
    if text == 'no_cgrs' and answer =='swallowing':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} furry tounge ?'.format(phrase), furt)
        
    if text == 'yes_furt' and answer == 'swallowing': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
        
    if text == 'no_furt' and answer == 'swallowing': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
    
    if text == 'no_inc' and answer == 'swallowing':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} have Tonsillitis.".format(phrase2,average,phrase2))
            choose_howto(sender_id,'remedies_tonsil','medication_tonsil','about_tonsil','Tonsillitis')
        elif get_average(count_yes, total_symptoms) <80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Tonsillitis.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 80% or higher percentage rate base on symptoms that {} current have.\nBefore I can determine that {} have Tonsillitis.".format(phrase2,phrase2))
            bot.send_text_message(sender_id, "So {},\nthese are the symptoms, that {} currently suffering: ".format(first_name(sender_id),phrase2))
            bot.send_quick_replies_message(sender_id, 'Right?'.format(phrase2), right) 
    if text == 'yes_ri' or 'no_ri' and answer == 'swallowing':
        pass #give medication/ remedies for those symptoms 
    if text == 'yes_inc' and answer == 'swallowing':       
        pass#NLU         
    #End tonsil
    #UTI
    if text =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        Mongo.set_answer(users,sender_id,'urination')
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
        
    if text =='yes_fever' and answer == 'urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        stoma = {"content_type":"text","title":"Yes","payload":'yes_stomachace'},{"content_type":"text","title":"No","payload":'no_stomachache'}                    
        bot.send_quick_replies_message(sender_id, 'having a stomachache ?', stoma)
    
    vomit  = {"content_type":"text","title":"Yes","payload":'yes_vomit'},{"content_type":"text","title":"No","payload":'no_vomit'}   
    if text == 'yes_stomachache':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'experiencing vomiting ?', vomit)
    if text == 'no_stomachache':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'experiencing vomiting ?', vomit)
    
    piu = {"content_type":"text","title":"Yes","payload":'yes_piu'},{"content_type":"text","title":"No","payload":'no_pui'}     
    if text == 'yes_vomit' and answer =='urination':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing pain in urethra ?'.format(phrase), piu)
    if text == 'no_vomit' and answer =='urination':   
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing pain in urethra ?'.format(phrase), piu)
    if text =='no_fever' and answer == 'urination':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing pain in urethra ?'.format(phrase), piu)
    
    fru = {"content_type":"text","title":"Yes","payload":'yes_fru'},{"content_type":"text","title":"No","payload":'no_fru'}    
    if text == 'yes_piu' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having frequent urination ?'.format(phrase), fru)
    if text == 'no_piu' and answer == 'urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having frequent urination ?'.format(phrase), fru)
        
    abpc = {"content_type":"text","title":"Yes","payload":'yes_abpc'},{"content_type":"text","title":"No","payload":'no_abpc'}      
    if text == 'yes_fru' and answer =='urination': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), abpc)
    if text == 'no_fru' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having abdominal pain ?'.format(phrase), abpc)
      
    dysur = {"content_type":"text","title":"Yes","payload":'yes_dysur'},{"content_type":"text","title":"No","payload":'no_dysur'}
    if text == 'yes_abpc' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having Dysuria  or discomfort when urinating ?'.format(phrase), dysur)
    if text == 'no_abpc' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having Dysuria  or discomfort when urinating ?'.format(phrase), dysur)
    
    flank = {"content_type":"text","title":"Yes","payload":'yes_flank'},{"content_type":"text","title":"No","payload":'no_flank'}
    if text == 'yes_dysur' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having flank pain ?'.format(phrase), flank)
    if text == 'no_dysur' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having flank pain ?'.format(phrase), flank)
    
    dyu = {"content_type":"text","title":"Yes","payload":'yes_dyu'},{"content_type":"text","title":"No","payload":'no_dyu'}
    if text == 'yes_flank' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having dark yellow urine ?'.format(phrase), dyu)
    if text == 'no_flank' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having dark yellow urine ?'.format(phrase), dyu)

    burn = {"content_type":"text","title":"Yes","payload":'yes_burn'},{"content_type":"text","title":"No","payload":'no_burn'}
    if text == 'yes_dyu' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having burning feeling when urinating ?'.format(phrase), burn)
    if text == 'no_dyu' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having burning feeling when urinating ?'.format(phrase), burn)

    foi = {"content_type":"text","title":"Yes","payload":'yes_foi'},{"content_type":"text","title":"No","payload":'no_foi'}
    if text == 'yes_burn' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having frequent or intense urge to urinate, even though little comes out when you do ?'.format(phrase), foi)
    if text == 'no_burn' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having frequent or intense urge to urinate, even though little comes out when you do ?'.format(phrase), foi)
        
    pop = {"content_type":"text","title":"Yes","payload":'yes_pop'},{"content_type":"text","title":"No","payload":'no_pop'}
    if text == 'yes_foi' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having fain or pressure in your back or lower abdomen ?'.format(phrase), pop)
    if text == 'no_foi' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having fain or pressure in your back or lower abdomen ?'.format(phrase), pop)
        
    cdb = {"content_type":"text","title":"Yes","payload":'yes_cdb'},{"content_type":"text","title":"No","payload":'no_cdb'}   
    if text == 'yes_pop' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cloudy, dark, bloody, or strange-smelling urine ?'.format(phrase), cdb)
    if text == 'no_pop' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cloudy, dark, bloody, or strange-smelling urine ?'.format(phrase), cdb)
        
    fts = {"content_type":"text","title":"Yes","payload":'yes_fts'},{"content_type":"text","title":"No","payload":'no_fts'}   
    if text == 'yes_cdb' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having feeling tired or shaky ?'.format(phrase), fts)
    if text == 'no_cdb' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having feeling tired or shaky ?'.format(phrase), fts)
        
    uar = {"content_type":"text","title":"Yes","payload":'yes_uar'},{"content_type":"text","title":"No","payload":'no_uar'}
    if text == 'yes_fts' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having urine appears red, bright pink or cola-colored which is a sign of blood in the urine ?'.format(phrase), uar)
    if text == 'no_fts' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having urine appears red, bright pink or cola-colored which is a sign of blood in the urine ?'.format(phrase), uar)
        
    naus = {"content_type":"text","title":"Yes","payload":'yes_naus'},{"content_type":"text","title":"No","payload":'no_naus'}
    if text == 'yes_uar' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having nausea ?'.format(phrase), naus)
    if text == 'no_uar' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having nausea ?'.format(phrase), naus)
    
    wbnc = {"content_type":"text","title":"Yes","payload":'yes_wbnc'},{"content_type":"text","title":"No","payload":'no_wbnc'}
    if text == 'yes_naus' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), wbnc)
    if text == 'no_naus' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), wbnc)
        
    pro = {"content_type":"text","title":"Yes","payload":'yes_pro'},{"content_type":"text","title":"No","payload":'no_pro'}
    if text == 'yes_wbnc' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), pro)
    if text == 'no_wbnc' and answer =='urination':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having WBC is to numeros to count ?'.format(phrase), pro)

    if text == 'yes_pro' and answer == 'urination': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
        
    if text == 'no_pro' and answer == 'urination': 
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask'.format(phrase2), take) 
    
    if text == 'no_inc' and answer == 'urination':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} have UTI.".format(phrase2,average,phrase2))
            choose_howto(sender_id,'remedies_uti','medication_uti','about_uti','Urinary Tract Infection')
        elif get_average(count_yes, total_symptoms) <80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have UTI.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 80% or higher percentage rate base on symptoms that {} current have.\nBefore I can determine that {} have UTI.".format(phrase2,phrase2))
            bot.send_text_message(sender_id, "So {},\nthese are the symptoms, that {} currently suffering: ".format(first_name(sender_id),phrase2))
            bot.send_quick_replies_message(sender_id, 'Right?'.format(phrase2), right) 
    if text == 'yes_ri' or 'no_ri' and answer == 'urination':
        pass #give medication/ remedies for those symptoms 
    if text == 'yes_inc' and answer == 'urination':       
        pass#NLU         

    #End UTI
        
     #Flu
    if text =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        Mongo.set_answer(users,sender_id,'body') 
        bot.send_text_message(sender_id, "Well that doesn't sound healthy")
        bot.send_quick_replies_message(sender_id, "{} having fever?".format(phrase), has_fever)
    
    if text =='yes_fever' and answer == 'body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        nas = {"content_type":"text","title":"Yes","payload":'yes_nasaldischarge'},{"content_type":"text","title":"No","payload":'no_nasaldischarge'}                    
        bot.send_quick_replies_message(sender_id, '{} having a nasal discharge ?'.format(phrase), nas)
        
    fvo  = {"content_type":"text","title":"Yes","payload":'yes_fvo'},{"content_type":"text","title":"No","payload":'no_fvo'}   
    if text == 'yes_nasaldischarge': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} currently in fever?'.format(phrase), fvo)
    if text == 'no_nasaldischarge':   
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} currently in fever?'.format(phrase), fvo)
    
    musc = {"content_type":"text","title":"Yes","payload":'yes_musc'},{"content_type":"text","title":"No","payload":'no_musc'}     
    if text == 'yes_fvo' and answer =='body':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing muscle pain ?'.format(phrase), musc)
    if text == 'no_fvo' and answer =='body':   
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing muscle pain ?'.format(phrase), musc)
    if text =='no_fever' and answer == 'body':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing muscle pain ?'.format(phrase), musc)
    
    cough = {"content_type":"text","title":"Yes","payload":'yes_cough'},{"content_type":"text","title":"No","payload":'no_cough'}    
    if text == 'yes_musc' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cough)
    if text == 'no_musc' and answer == 'body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cough ?'.format(phrase), cough)
        
    dpc = {"content_type":"text","title":"Yes","payload":'yes_dpc'},{"content_type":"text","title":"No","payload":'no_dpc'}
    if text == 'yes_cough' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having dry, persistent cough ?'.format(phrase), dpc)
    if text == 'no_cough' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having dry, persistent cough ?'.format(phrase), dpc)
        
    cold = {"content_type":"text","title":"Yes","payload":'yes_cold'},{"content_type":"text","title":"No","payload":'no_cold'}   
    if text == 'yes_dpc' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cold ?'.format(phrase), cold)
    if text == 'no_dpc' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cold ?'.format(phrase), cold)
        #dre tiwasa
    rn = {"content_type":"text","title":"Yes","payload":'yes_rn'},{"content_type":"text","title":"No","payload":'no_rn'}
    if text == 'yes_cold' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing runny nose ?'.format(phrase), rn)
    if text == 'no_cold' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing runny nose ?'.format(phrase), rn)
            
    nac = {"content_type":"text","title":"Yes","payload":'yes_nac'},{"content_type":"text","title":"No","payload":'no_nac'}
    if text == 'yes_rn' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having nasal congestion ?'.format(phrase), nac)
    if text == 'no_rn' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having nasal congestion ?'.format(phrase), nac)
        
    pora = {"content_type":"text","title":"Yes","payload":'yes_pora'},{"content_type":"text","title":"No","payload":'no_pora'}
    if text == 'yes_nac' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having poor appetite ?'.format(phrase), pora)
    if text == 'no_nac' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having poor appetite ?'.format(phrase), pora)
    
    headach = {"content_type":"text","title":"Yes","payload":'yes_headach'},{"content_type":"text","title":"No","payload":'no_headach'}
    if text == 'yes_pora' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing headache ?'.format(phrase), headach)
    if text == 'no_pora' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} experiencing headache ?'.format(phrase), headach)
        
    cas = {"content_type":"text","title":"Yes","payload":'yes_cas'},{"content_type":"text","title":"No","payload":'no_cas'}
    if text == 'yes_headach' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having chills and sweats ?'.format(phrase), cas)
    if text == 'no_headach' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having chills and sweats ?'.format(phrase), cas)
   
    fati = {"content_type":"text","title":"Yes","payload":'yes_fati'},{"content_type":"text","title":"No","payload":'no_fati'}
    if text == 'yes_cas' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} fatigue ?'.format(phrase), fati)
    if text == 'no_cas' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} fatigue ?'.format(phrase), fati)

    fw = {"content_type":"text","title":"Yes","payload":'yes_fw'},{"content_type":"text","title":"No","payload":'no_fw'}
    if text == 'yes_fati' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} feeling weak ?'.format(phrase), fw)
    if text == 'no_fati' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} feeling weak ?'.format(phrase), fw)
     
    sthroat = {"content_type":"text","title":"Yes","payload":'yes_sthroat'},{"content_type":"text","title":"No","payload":'no_sthroat'}
    if text == 'yes_fw' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having sore throat ?'.format(phrase), sthroat)
    if text == 'no_fw' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having sore throat ?'.format(phrase), sthroat)
        
    pte = {"content_type":"text","title":"Yes","payload":'yes_pte'},{"content_type":"text","title":"No","payload":'no_pte'}
    if text == 'yes_sthroat' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain and tiredness around the eyes ?'.format(phrase), pte)
    if text == 'no_sthroat' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain and tiredness around the eyes ?'.format(phrase), pte)
        
    tbs = {"content_type":"text","title":"Yes","payload":'yes_tbs'},{"content_type":"text","title":"No","payload":'no_tbs'}
    if text == 'yes_pte' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having trouble breathing or shortness of breathing ?'.format(phrase), tbs)
    if text == 'no_pte' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having trouble breathing or shortness of breathing ?'.format(phrase), tbs)
            
    ppc = {"content_type":"text","title":"Yes","payload":'yes_ppc'},{"content_type":"text","title":"No","payload":'no_ppc'}  
    if text == 'yes_tbs' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain or pressure in your chest or belly ?'.format(phrase), ppc)
    if text == 'no_tbs' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having pain or pressure in your chest or belly ?'.format(phrase), ppc)
        
    sdiz = {"content_type":"text","title":"Yes","payload":'yes_sdiz'},{"content_type":"text","title":"No","payload":'no_sdiz'}
    if text == 'yes_ppc' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having sudden dizziness ?'.format(phrase), sdiz)
    if text == 'no_ppc' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having sudden dizziness ?'.format(phrase), sdiz)
    
    css = {"content_type":"text","title":"Yes","payload":'yes_css'},{"content_type":"text","title":"No","payload":'no_css'}
    if text == 'yes_sdiz' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cold sweats and shivers ?'.format(phrase), css)
    if text == 'no_sdiz' and answer =='body':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, '{} having cold sweats and shivers ?'.format(phrase), css)
        
    if text == 'yes_css' and answer == 'body': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
        
    if text == 'no_css' and answer == 'body':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do {} have symptoms that we did not ask?'.format(phrase2), take) 
    
    if text == 'no_inc' and answer == 'body':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} have FLU.".format(phrase2,average,phrase2))
            choose_howto(sender_id,'remedies_flu','medication_flu','about_flu','Flu')
        elif get_average(count_yes, total_symptoms) <80:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have flu.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 80% or higher percentage rate base on symptoms that {} current have.\nBefore I can determine that {} have flu.".format(phrase2,phrase2))
            bot.send_text_message(sender_id, "So {},\nthese are the symptoms, that {} currently suffering: ".format(first_name(sender_id),phrase2))
            bot.send_quick_replies_message(sender_id, 'Right?'.format(phrase2), right) 
    if text == 'yes_ri' or 'no_ri' and answer == 'body':
        pass #give medication/ remedies for those symptoms 
    if text == 'yes_inc' and answer == 'body':       
        pass#NLU             
    #END FLU
        
    #ADHD
    interferes  = {"content_type":"text","title":"Yes","payload":'yes_interferes'},{"content_type":"text","title":"No","payload":'no_interferes'}   
    if text =='ADHD': 
        Mongo.set_answer(users,sender_id,'ADHD')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "Does your child interferes in the classroom because she/he has difficulty engaging in quiet activities without disturbing others?", interferes)
    if text =='yes_interferes' and answer == 'ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        dif = {"content_type":"text","title":"Yes","payload":'yes_difficulty'},{"content_type":"text","title":"No","payload":'no_difficulty'}                    
        bot.send_quick_replies_message(sender_id, 'Does your child has a difficulty stay focused on homework or other tasks?', dif)

    disorg  = {"content_type":"text","title":"Yes","payload":'yes_disorg'},{"content_type":"text","title":"No","payload":'no_disorg'}   
    if text == 'yes_difficulty':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Does your child is disorganized and, even with youry help, can't seem to learn how to become organized?", disorg)
    if text == 'no_difficulty':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Does your child is disorganized and, even with youry help, can't seem to learn how to become organized?", disorg)

    los = {"content_type":"text","title":"Yes","payload":'yes_los'},{"content_type":"text","title":"No","payload":'no_los'}     
    if text == 'yes_disorg' and answer =='ADHD': 
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child loses things like homework and personal belongings?', los)
    if text == 'no_disorg' and answer =='ADHD':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child loses things like homework and personal belongings?', los)
    if text =='no_interferes' and answer == 'ADHD':             
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child loses things like homework and personal belongings?', los)

    disc = {"content_type":"text","title":"Yes","payload":'yes_disc'},{"content_type":"text","title":"No","payload":'no_disc'}    
    if text == 'yes_los' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child gets disctracted even the smallest distractions can throw him/her off task?', disc)
    if text == 'no_los' and answer == 'ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child gets disctracted even the smallest distractions can throw him/her off task?', disc)

    cons = {"content_type":"text","title":"Yes","payload":'yes_cons'},{"content_type":"text","title":"No","payload":'no_cons'}
    if text == 'yes_disc' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child constantly seems to be fidgeting?', cons)
    if text == 'no_disc' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child constantly seems to be fidgeting?', cons)

    trs = {"content_type":"text","title":"Yes","payload":'yes_trs'},{"content_type":"text","title":"No","payload":'no_trs'}
    if text == 'yes_cons' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child tries to avoid activities that require sustained concentration and a lot of mental effort?', trs)
    if text == 'no_cons' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child tries to avoid activities that require sustained concentration and a lot of mental effort?', trs)

    care = {"content_type":"text","title":"Yes","payload":'yes_care'},{"content_type":"text","title":"No","payload":'no_care'}
    if text == 'yes_trs' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child makes careless mistakes?', care)
    if text == 'no_trs' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child makes careless mistakes?', care)

    wait = {"content_type":"text","title":"Yes","payload":'yes_wait'},{"content_type":"text","title":"No","payload":'no_wait'}
    if text == 'yes_care' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child has difficulty waiting patiently to take turns, and butts ahead in lines or grabs toys from playmates?', wait)
    if text == 'no_care' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child has difficulty waiting patiently to take turns, and butts ahead in lines or grabs toys from playmates?', wait)

    prob = {"content_type":"text","title":"Yes","payload":'yes_prob'},{"content_type":"text","title":"No","payload":'no_prob'}
    if text == 'yes_wait' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child has problems remaining seated even when she/he is supposed to?', prob)
    if text == 'no_wait' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child has problems remaining seated even when she/he is supposed to?', prob)

    fail = {"content_type":"text","title":"Yes","payload":'yes_fail'},{"content_type":"text","title":"No","payload":'no_fail'}
    if text == 'yes_prob' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child fails to complete an activity before moving to the next activity?', fail)
    if text == 'no_prob' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child fails to complete an activity before moving to the next activity?', fail)

    itp = {"content_type":"text","title":"Yes","payload":'yes_itp'},{"content_type":"text","title":"No","payload":'no_itp'}
    if text == 'yes_fail' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Does your child interrupts other peoples' activities and conversations?", itp)
    if text == 'no_fail' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Does your child interrupts other peoples' activities and conversations?", itp)
    checkm = [{"content_type":"text","title":"Send Result","payload":'yes_checkm'}]
    if text == 'yes_itp' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'no_itp' and answer =='ADHD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'ADHD':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has ADHD.".format(average))
            choose_howto(sender_id,'remedies_adhd','medication_adhd','about_adhd','ADHD')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have ADHD.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has ADHD.")
    #end adhd
    #anxiety
    if text =='Anxiety': 
        Mongo.set_answer(users,sender_id,'Anxiety')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "When you are all at home for the day, does your child follow you around the house wherever you go?", all)

    if text =='yes_all' and answer == 'Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        oft = {"content_type":"text","title":"Yes","payload":'yes_often'},{"content_type":"text","title":"No","payload":'no_often'}                    
        bot.send_quick_replies_message(sender_id, 'Does your child often come home sick from school with a stomachache or headache?', oft)

    eas  = {"content_type":"text","title":"Yes","payload":'yes_eas'},{"content_type":"text","title":"No","payload":'no_eas'}   
    if text == 'yes_often':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, ' Is your child easily fatigued and/or complain of sore muscles?', eas)
    if text == 'no_often':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, ' Is your child easily fatigued and/or complain of sore muscles?', eas)

    eve = {"content_type":"text","title":"Yes","payload":'yes_eve'},{"content_type":"text","title":"No","payload":'no_eve'}     
    if text == 'yes_eas' and answer =='Anxiety':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Has your child ever gotten so scared that she says it’s hard to breathe?', eve)
    if text == 'no_eas' and answer =='Anxiety':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Has your child ever gotten so scared that she says it’s hard to breathe?', eve)
    if text =='no_all' and answer == 'Anxiety':           
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Has your child ever gotten so scared that she says it’s hard to breathe?', eve)

    at = {"content_type":"text","title":"Yes","payload":'yes_at'},{"content_type":"text","title":"No","payload":'no_at'}     
    if text == 'yes_eve' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'At birthday parties, does your child feel nervous if left with people she doesn’t know very well?', at)
    if text == 'no_eve' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'At birthday parties, does your child feel nervous if left with people she doesn’t know very well?', at)

    are = {"content_type":"text","title":"Yes","payload":'yes_are'},{"content_type":"text","title":"No","payload":'no_are'}
    if text == 'yes_at' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Are you woken frequently in the night because your child had another nightmare about something bad happening to you?', are)
    if text == 'no_at' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Are you woken frequently in the night because your child had another nightmare about something bad happening to you?', are)

    chan = {"content_type":"text","title":"Yes","payload":'yes_chan'},{"content_type":"text","title":"No","payload":'no_chan'}
    if text == 'yes_are' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child change clothes several times a day because she sweats a lot when she is nervous?', chan)
    if text == 'no_are' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child change clothes several times a day because she sweats a lot when she is nervous?', chan)

    scar = {"content_type":"text","title":"Yes","payload":'yes_scar'},{"content_type":"text","title":"No","payload":'no_scar'}
    if text == 'yes_chan' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child scared to get on the bus and go to school every day?', scar)
    if text == 'no_chan' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child scared to get on the bus and go to school every day?', scar)

    exp = {"content_type":"text","title":"Yes","payload":'yes_exp'},{"content_type":"text","title":"No","payload":'no_exp'}
    if text == 'yes_scar' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child expect the worst, even when there is no justification for worry?', exp)
    if text == 'no_scar' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child expect the worst, even when there is no justification for worry?', exp)

    whe = {"content_type":"text","title":"Yes","payload":'yes_whe'},{"content_type":"text","title":"No","payload":'no_whe'}
    if text == 'yes_exp' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Even when you are upstairs and your child is in the basement, does he get scared about being alone in the house?', whe)
    if text == 'no_exp' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Even when you are upstairs and your child is in the basement, does he get scared about being alone in the house?', whe)

    fill = {"content_type":"text","title":"Yes","payload":'yes_fill'},{"content_type":"text","title":"No","payload":'no_fill'}
    if text == 'yes_whe' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child fill her bed with stuffed animals and the family pet because she is too nervous to sleep alone?', fill)
    if text == 'no_whe' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child fill her bed with stuffed animals and the family pet because she is too nervous to sleep alone?', fill)

    slu = {"content_type":"text","title":"Yes","payload":'yes_slu'},{"content_type":"text","title":"No","payload":'no_slu'}
    if text == 'yes_fill' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Has your child come home from a slumber party because she’s too scared to sleep away from home?', slu)
    if text == 'no_fill' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Has your child come home from a slumber party because she’s too scared to sleep away from home?', slu)

    tea = {"content_type":"text","title":"Yes","payload":'yes_tea'},{"content_type":"text","title":"No","payload":'no_tea'}
    if text == 'yes_slu' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Have teachers mentioned that your child seems nervous working in groups or speaking in class?', tea)
    if text == 'no_slu' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Have teachers mentioned that your child seems nervous working in groups or speaking in class?', tea)

    spen = {"content_type":"text","title":"Yes","payload":'yes_spen'},{"content_type":"text","title":"No","payload":'no_spen'}
    if text == 'yes_tea' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'After school, does your child spend an excessive amount of time doing and redoing homework worksheets because he doesn’t want anything to be less than perfect?', spen)
    if text == 'no_tea' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'After school, does your child spend an excessive amount of time doing and redoing homework worksheets because he doesn’t want anything to be less than perfect?', spen)

    irr = {"content_type":"text","title":"Yes","payload":'yes_irr'},{"content_type":"text","title":"No","payload":'no_irr'}
    if text == 'yes_spen' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child irrationally afraid of flying in an airplane, or of a certain animal?', irr)
    if text == 'no_spen' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child irrationally afraid of flying in an airplane, or of a certain animal?', irr)

    trem = {"content_type":"text","title":"Yes","payload":'yes_trem'},{"content_type":"text","title":"No","payload":'no_trem'}
    if text == 'yes_irr' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child tremble when she’s in crowded places like the shopping mall or a busy playground?', trem)
    if text == 'no_irr' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child tremble when she’s in crowded places like the shopping mall or a busy playground?', trem)

    req = {"content_type":"text","title":"Yes","payload":'yes_req'},{"content_type":"text","title":"No","payload":'no_req'}
    if text == 'yes_trem' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child require constant approval and reassurance that she’s done a good job?', req)
    if text == 'no_trem' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child require constant approval and reassurance that she’s done a good job?', req)
    
    if text == 'yes_req' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'no_req' and answer =='Anxiety':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'ADHD':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has Anxiety Disorder.".format(average))
            choose_howto(sender_id,'remedies_anxiety','medication_anxiety','about_anxiety','Anxiety Disorder')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Anxiety Disorder.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has Anxiety Disorder.")
    #end anxiety
    #autism
    if text =='Autism': 
        Mongo.set_answer(users,sender_id,'Autism')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "If you point at something across the room, does your child look at it?", point)

    if text =='yes_point' and answer == 'Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        dea = {"content_type":"text","title":"Yes","payload":'yes_deaf'},{"content_type":"text","title":"No","payload":'no_deaf'}                    
        bot.send_quick_replies_message(sender_id, 'Have you ever wondered if your child might be deaf?', dea)

    unu  = {"content_type":"text","title":"Yes","payload":'yes_unu'},{"content_type":"text","title":"No","payload":'no_unu'}   
    if text == 'yes_deaf':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
         bot.send_quick_replies_message(sender_id, ' Does your child make unusual finger movements near his or her eyes? (FOR EXAMPLE, does your child wiggle his/her fingers close to his/her eyes?', unu)
    if text == 'no_deaf':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, ' Does your child make unusual finger movements near his or her eyes? (FOR EXAMPLE, does your child wiggle his/her fingers close to his/her eyes?', unu)

    ups = {"content_type":"text","title":"Yes","payload":'yes_ups'},{"content_type":"text","title":"No","payload":'no_ups'}     
    if text == 'yes_unu' and answer =='Autism':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get upset by everyday noises?', ups)
    if text == 'no_unu' and answer =='Autism':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get upset by everyday noises?', ups)
    if text =='no_point' and answer == 'Autism':           
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get upset by everyday noises?', ups)

    notx = {"content_type":"text","title":"Yes","payload":'yes_not'},{"content_type":"text","title":"No","payload":'no_not'}     
    if text == 'yes_ups' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child appear to notice unusual details that others miss?', notx)
    if text == 'no_ups' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child appear to notice unusual details that others miss?', notx)

    thn = {"content_type":"text","title":"Yes","payload":'yes_thn'},{"content_type":"text","title":"No","payload":'no_thn'}  
    if text == 'yes_not' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child like to do things over and over again, in the same way all the time?', thn)
    if text == 'no_not' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child like to do things over and over again, in the same way all the time?', thn)

    tak = {"content_type":"text","title":"Yes","payload":'yes_tak'},{"content_type":"text","title":"No","payload":'no_tak'}
    if text == 'yes_thn' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have an interest that takes up so much time that he or she does little else?', tak)
    if text == 'no_thn' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have an interest that takes up so much time that he or she does little else?', tak)

    und = {"content_type":"text","title":"Yes","payload":'yes_und'},{"content_type":"text","title":"No","payload":'no_und'}
    if text == 'yes_tak' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have difficulty understanding the rules for polite behavior?', und)
    if text == 'no_tak' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have difficulty understanding the rules for polite behavior?'., und)

    app = {"content_type":"text","title":"Yes","payload":'yes_app'},{"content_type":"text","title":"No","payload":'no_app'}
    if text == 'yes_und' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child appear to have an unusual memory for details?', app)
    if text == 'no_und' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child appear to have an unusual memory for details?', app)

    new = {"content_type":"text","title":"Yes","payload":'yes_new'},{"content_type":"text","title":"No","payload":'no_new'}
    if text == 'yes_app' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'If something new happens, does your child look at your face to see how you feel about it? (FOR EXAMPLE, if he or she hears a strange or funny noise, or sees a new toy, will he or she look at your face?', new)
    if text == 'no_app' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'If something new happens, does your child look at your face to see how you feel about it? (FOR EXAMPLE, if he or she hears a strange or funny noise, or sees a new toy, will he or she look at your face?', new)

    some = {"content_type":"text","title":"Yes","payload":'yes_some'},{"content_type":"text","title":"No","payload":'no_some'}
    if text == 'yes_new' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child understand when you tell him or her to do something?', some)
    if text == 'no_new' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child understand when you tell him or her to do something?', some)

    watch = {"content_type":"text","title":"Yes","payload":'yes_watch'},{"content_type":"text","title":"No","payload":'no_watch'}
    if text == 'yes_some' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child try to get you to watch him or her?', watch)
    if text == 'no_some' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child try to get you to watch him or her?', watch)

    turn = {"content_type":"text","title":"Yes","payload":'yes_turn'},{"content_type":"text","title":"No","payload":'no_turn'}
    if text == 'yes_watch' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'If you turn your head to look at something, does your child look around to see what you are looking at?', turn)
    if text == 'no_watch' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'If you turn your head to look at something, does your child look around to see what you are looking at?', turn)

    copy = {"content_type":"text","title":"Yes","payload":'yes_copy'},{"content_type":"text","title":"No","payload":'no_copy'}
    if text == 'yes_turn' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child try to copy what you do?', copy)
    if text == 'no_turn' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child try to copy what you do?', copy)

    eye = {"content_type":"text","title":"Yes","payload":'yes_eye'},{"content_type":"text","title":"No","payload":'no_eye'}
    if text == 'yes_copy' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child look you in the eye when you are talking to him or her, playing with him or her, or dressing him or her?', eye)
    if text == 'no_copy' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child look you in the eye when you are talking to him or her, playing with him or her, or dressing him or her?', eye)

    smile = {"content_type":"text","title":"Yes","payload":'yes_smile'},{"content_type":"text","title":"No","payload":'no_smile'}
    if text == 'yes_eye' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you smile at your child, does he or she smile back at you?', smile)
    if text == 'no_eye' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you smile at your child, does he or she smile back at you?', smile)

    resp = {"content_type":"text","title":"Yes","payload":'yes_resp'},{"content_type":"text","title":"No","payload":'no_resp'}
    if text == 'yes_smile' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child respond when you call his or her name?', resp)
    if text == 'no_smile' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child respond when you call his or her name?', resp)

    things = {"content_type":"text","title":"Yes","payload":'yes_things'},{"content_type":"text","title":"No","payload":'no_things'}
    if text == 'yes_smile' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child show you things by bringing them to you or holding them up for you to see—not to get help, but just to share?', things)
    if text == 'no_smile' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child show you things by bringing them to you or holding them up for you to see—not to get help, but just to share?', things)

    inter = {"content_type":"text","title":"Yes","payload":'yes_inter'},{"content_type":"text","title":"No","payload":'no_inter'}
    if text == 'yes_things' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child interested in other children?', inter)
    if text == 'no_things' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child interested in other children?', inter)

    fing = {"content_type":"text","title":"Yes","payload":'yes_fing'},{"content_type":"text","title":"No","payload":'no_fing'}
    if text == 'yes_inter' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child point with one finger to show you something interesting?', fing)
    if text == 'no_inter' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child point with one finger to show you something interesting?'., fing)

    one = {"content_type":"text","title":"Yes","payload":'yes_one'},{"content_type":"text","title":"No","payload":'no_one'}
    if text == 'yes_fing' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child point with one finger to ask for something or to get help?', one)
    if text == 'no_fing' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child point with one finger to ask for something or to get help?', one)

    climb = {"content_type":"text","title":"Yes","payload":'yes_climb'},{"content_type":"text","title":"No","payload":'no_climb'}
    if text == 'yes_one' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child like climbing on things?', climb)
    if text == 'no_one' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child like climbing on things?', climb)

    bel = {"content_type":"text","title":"Yes","payload":'yes_bel'},{"content_type":"text","title":"No","payload":'no_bel'}
    if text == 'yes_climb' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child play pretend or make-believe?', bel)
    if text == 'no_climb' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child play pretend or make-believe?', bel)

    move = {"content_type":"text","title":"Yes","payload":'yes_move'},{"content_type":"text","title":"No","payload":'no_move'}
    if text == 'yes_bel' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child like movement activities?', move)
    if text == 'no_bel' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child like movement activities?', move)

    gam = {"content_type":"text","title":"Yes","payload":'yes_gam'},{"content_type":"text","title":"No","payload":'no_gam'}
    if text == 'yes_move' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child join in playing games with other children easily?', gam)
    if text == 'no_move' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child join in playing games with other children easily?', gam)

    spont = {"content_type":"text","title":"Yes","payload":'yes_spont'},{"content_type":"text","title":"No","payload":'no_spont'}
    if text == 'yes_gam' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child come up to you spontaneously for a chat?', spont)
    if text == 'no_gam' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child come up to you spontaneously for a chat?', spont)

    was = {"content_type":"text","title":"Yes","payload":'yes_was'},{"content_type":"text","title":"No","payload":'no_was'}
    if text == 'yes_spont' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Was your child speaking by 2 years old?', was)
    if text == 'no_spont' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Was your child speaking by 2 years old?', was)

    spor = {"content_type":"text","title":"Yes","payload":'yes_spor'},{"content_type":"text","title":"No","payload":'no_spor'}
    if text == 'yes_was' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child enjoy playing sports?', spor)
    if text == 'no_was' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child enjoy playing sports?', spor)

    fit = {"content_type":"text","title":"Yes","payload":'yes_fit'},{"content_type":"text","title":"No","payload":'no_fit'}
    if text == 'yes_spor' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is it important to your child to fit in with his or her peer group?', fit)
    if text == 'no_spor' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is it important to your child to fit in with his or her peer group?', fit)

    tway = {"content_type":"text","title":"Yes","payload":'yes_tway'},{"content_type":"text","title":"No","payload":'no_tway'}
    if text == 'yes_fit' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Can your child keep a two-way conversation going?', tway)
    if text == 'no_fit' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Can your child keep a two-way conversation going?', tway)
        
    if text == 'yes_tway' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'no_tway' and answer =='Autism':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'Autism':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has Autism Spectrum Disorder.".format(average))
            choose_howto(sender_id,'remedies_autism','medication_autism','about_autism','Autism Spectrum Disorder')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Autism Spectrum Disorder.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has Autism Spectrum Disorder.")
    #end autism
    
    #Bipolar
    if text =='Bipolar': 
        Mongo.set_answer(users,sender_id,'Bipolar')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "Does your child inconsistently have periods where he has an unfocused, limitless energy that feels out of control, even to him?", inconsistently)

    if text =='yes_inconsistently' and answer == 'Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        moo = {"content_type":"text","title":"Yes","payload":'yes_mood'},{"content_type":"text","title":"No","payload":'no_mood'}                    
        bot.send_quick_replies_message(sender_id, 'Does your child’s mood change from happy to sad instantaneously — almost like flicking a light switch?', moo)

    mast  = {"content_type":"text","title":"Yes","payload":'yes_mast'},{"content_type":"text","title":"No","payload":'no_mast'}   
    if text == 'yes_mood':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child masterfully lie to either avoid consequences or manipulate a situation?', mast)
    if text == 'no_mood':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child masterfully lie to either avoid consequences or manipulate a situation?', mast)

    setx = {"content_type":"text","title":"Yes","payload":'yes_set'},{"content_type":"text","title":"No","payload":'no_set'}     
    if text == 'yes_mast' and answer =='Bipolar':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you try to set limits on your child — asking him to shut off his video game and join you at the dinner table — does he react in an extreme or violent way?', setx)
    if text == 'no_mast' and answer =='Bipolar':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you try to set limits on your child — asking him to shut off his video game and join you at the dinner table — does he react in an extreme or violent way?', setx)
    if text =='no_inconsistently' and answer == 'Bipolar':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you try to set limits on your child — asking him to shut off his video game and join you at the dinner table — does he react in an extreme or violent way?', setx)

    prec = {"content_type":"text","title":"Yes","payload":'yes_prec'},{"content_type":"text","title":"No","payload":'no_prec'}     
    if text == 'yes_set' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child sometimes precocious — charming adults with his intelligent and mature speaking style — and then at other times does he regress to baby-like, primitive behaviors, like crawling up in a fetal position when stressed or engaging in baby talk?', prec)
    if text == 'no_set' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child sometimes precocious — charming adults with his intelligent and mature speaking style — and then at other times does he regress to baby-like, primitive behaviors, like crawling up in a fetal position when stressed or engaging in baby talk?', prec)

    muc = {"content_type":"text","title":"Yes","payload":'yes_muc'},{"content_type":"text","title":"No","payload":'no_muc'}
    if text == 'yes_prec' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child much more curious about sex than other children her age? Does she bring up sex inappropriately in conversation, or has she engaged in inappropriate or risky sexual behaviors?', muc)
    if text == 'no_prec' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child much more curious about sex than other children her age? Does she bring up sex inappropriately in conversation, or has she engaged in inappropriate or risky sexual behaviors?', muc)

    alto = {"content_type":"text","title":"Yes","payload":'yes_alto'},{"content_type":"text","title":"No","payload":'no_alto'}
    if text == 'yes_muc' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does it seem like your child has given up sleeping altogether — but often doesn’t seem tired the day after a sleepless night?', alto)
    if text == 'no_muc' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does it seem like your child has given up sleeping altogether — but often doesn’t seem tired the day after a sleepless night?', alto)

    conv = {"content_type":"text","title":"Yes","payload":'yes_conv'},{"content_type":"text","title":"No","payload":'no_conv'}
    if text == 'yes_alto' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'All of a sudden, is your child convinced she can be a famous singer, president of the United States, an international spy, and a millionaire — all at once?', conv)
    if text == 'no_alto' and answer =='Bipolar':=
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'All of a sudden, is your child convinced she can be a famous singer, president of the United States, an international spy, and a millionaire — all at once?', conv)

    dan = {"content_type":"text","title":"Yes","payload":'yes_dan'},{"content_type":"text","title":"No","payload":'no_dan'}
    if text == 'yes_conv' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child engage in dangerous activities — like jumping out of trees or rollerblading while hanging on to the back of a car — and later say that he knew it could be dangerous, for others but that he felt immune to that danger? Does he report that he may even welcome any injury?', dan)
    if text == 'no_conv' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child engage in dangerous activities — like jumping out of trees or rollerblading while hanging on to the back of a car — and later say that he knew it could be dangerous, for others but that he felt immune to that danger? Does he report that he may even welcome any injury?', dan)

    seem = {"content_type":"text","title":"Yes","payload":'yes_seem'},{"content_type":"text","title":"No","payload":'no_seem'}
    if text == 'yes_dan' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child’s brain seem powered by a motor? Does she talk a mile a minute, or says she can’t seem to slow down her thoughts?', seem)
    if text == 'no_dan' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child’s brain seem powered by a motor? Does she talk a mile a minute, or says she can’t seem to slow down her thoughts?', seem)

    rag = {"content_type":"text","title":"Yes","payload":'yes_rag'},{"content_type":"text","title":"No","payload":'no_rag'}
    if text == 'yes_seem' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have long, explosive rage attacks — sometimes complete with foul language that’s inappropriate for his age?', rag)
    if text == 'no_seem' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have long, explosive rage attacks — sometimes complete with foul language that’s inappropriate for his age?', rag)

    trou = {"content_type":"text","title":"Yes","payload":'yes_trou'},{"content_type":"text","title":"No","payload":'no_trou'}
    if text == 'yes_rag' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When your child gets in trouble at school or at home, does she blame others for causing the mistake?', trou)
    if text == 'no_rag' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When your child gets in trouble at school or at home, does she blame others for causing the mistake?', trou)

    gor = {"content_type":"text","title":"Yes","payload":'yes_gor'},{"content_type":"text","title":"No","payload":'no_gor'}
    if text == 'yes_trou' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child seek out gory films and violent, bloody games?', gor)
    if text == 'no_trou' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child seek out gory films and violent, bloody games?', gor)

    panic = {"content_type":"text","title":"Yes","payload":'yes_panic'},{"content_type":"text","title":"No","payload":'no_panic'}
    if text == 'yes_gor' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child expect the worst at every turn? Does he panic over small, seemingly insignificant events — like a minor scrape or a crime-related news story?', panic)
    if text == 'no_gor' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child expect the worst at every turn? Does he panic over small, seemingly insignificant events — like a minor scrape or a crime-related news story?', panic)

    rej = {"content_type":"text","title":"Yes","payload":'yes_rej'},{"content_type":"text","title":"No","payload":'no_rej'}
    if text == 'yes_panic' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child suddenly reject taking part in her favorite activities?', rej)
    if text == 'no_panic' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child suddenly reject taking part in her favorite activities?', rej)
    
    if text == 'yes_rej' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'yes_rej' and answer =='Bipolar':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'Bipolar':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has Bipolar Disorder.".format(average))
            choose_howto(sender_id,'remedies_bipolar','medication_bipolar','about_bipolar','Bipolar Disorder')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Bipolar Disorder.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has Bipolar Disorder.")
    #end bipolar
    #depression
    if text =='Depression': 
        Mongo.set_answer(users,sender_id,'Depression')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "You made your child’s favorite after-school snack, but she said she wasn’t hungry, and then only picked at her dinner?", favorite)

    if text =='yes_favorite' and answer == 'Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        ters = {"content_type":"text","title":"Yes","payload":'yes_tears'},{"content_type":"text","title":"No","payload":'no_tears'}                    
        bot.send_quick_replies_message(sender_id, 'When the movie you wanted to see was sold out, your child burst into tears?', ters)

    dum  = {"content_type":"text","title":"Yes","payload":'yes_dum'},{"content_type":"text","title":"No","payload":'no_dum'}   
    if text == 'yes_tears':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Even though you have gone out of your way to cheer him up, your child still seems down in the dumps?', dum)
    if text == 'no_tears':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Even though you have gone out of your way to cheer him up, your child still seems down in the dumps?', dum)

    inca = {"content_type":"text","title":"Yes","payload":'yes_inca'},{"content_type":"text","title":"No","payload":'no_inca'}     
    if text == 'yes_dum' and answer =='Depression':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Homework is always a struggle, but sometimes it seems like your child is incapable of even sitting down and getting started?', inca)
    if text == 'no_dum' and answer =='Depression':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Homework is always a struggle, but sometimes it seems like your child is incapable of even sitting down and getting started?', inca)
    if text =='no_favorite' and answer == 'Depression':       
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Homework is always a struggle, but sometimes it seems like your child is incapable of even sitting down and getting started?', inca)

    chatt = {"content_type":"text","title":"Yes","payload":'yes_chatt'},{"content_type":"text","title":"No","payload":'no_chatt'}     
    if text == 'yes_inca' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'She’s regularly a chatty Kathy at home after school, but can be eerily quiet for days or weeks on end?', chatt)
    if text == 'no_inca' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'She’s regularly a chatty Kathy at home after school, but can be eerily quiet for days or weeks on end?', chatt)

    bedt = {"content_type":"text","title":"Yes","payload":'yes_bedt'},{"content_type":"text","title":"No","payload":'no_bedt'}
    if text == 'yes_chatt' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Even after a bedtime story, your child can’t seem to fall asleep, and wakes up in the middle of the night more often than not?', bedt)
    if text == 'no_chatt' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Even after a bedtime story, your child can’t seem to fall asleep, and wakes up in the middle of the night more often than not?', bedt)

    confi = {"content_type":"text","title":"Yes","payload":'yes_confi'},{"content_type":"text","title":"No","payload":'no_confi'}
    if text == 'yes_bedt' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'He’s always been full of confidence, but lately has been saying things like, “All the other kids in class are smarter than me.”?', confi)
    if text == 'no_bedt' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'He’s always been full of confidence, but lately has been saying things like, “All the other kids in class are smarter than me.”?', confi)

    easi = {"content_type":"text","title":"Yes","payload":'yes_easi'},{"content_type":"text","title":"No","payload":'no_easi'}
    if text == 'yes_confi' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your child is easily distracted, even when doing things she likes, such as making cookies with Mom?', easi)
    if text == 'no_confi' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your child is easily distracted, even when doing things she likes, such as making cookies with Mom?', easi)

    rece = {"content_type":"text","title":"Yes","payload":'yes_rece'},{"content_type":"text","title":"No","payload":'no_rece'}
    if text == 'yes_easi' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you ask how recess was, your child says, “No one wanted to play with me.”?', rece)
    if text == 'no_easi' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'When you ask how recess was, your child says, “No one wanted to play with me.”?', rece)

    raci = {"content_type":"text","title":"Yes","payload":'yes_raci'},{"content_type":"text","title":"No","payload":'no_raci'}
    if text == 'yes_rece' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Usually, he’s racing around the house after dinner asking everyone to come outside and play catch. Lately, he’s been a bump on a log even when you try to get him moving?', raci)
    if text == 'no_rece' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Usually, he’s racing around the house after dinner asking everyone to come outside and play catch. Lately, he’s been a bump on a log even when you try to get him moving?', raci)

    birth = {"content_type":"text","title":"Yes","payload":'yes_birth'},{"content_type":"text","title":"No","payload":'no_birth'}
    if text == 'yes_raci' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your child said she doesn’t want to have a birthday party this year because she doesn’t have any friends she would want to invite?'., birth)
    if text == 'no_raci' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your child said she doesn’t want to have a birthday party this year because she doesn’t have any friends she would want to invite?', birth)

    extr = {"content_type":"text","title":"Yes","payload":'yes_extr'},{"content_type":"text","title":"No","payload":'no_extr'}
    if text == 'yes_birth' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Simple decisions, like what to wear in the morning, are lately extremely difficult to make?', extr)
    if text == 'no_birth' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Simple decisions, like what to wear in the morning, are lately extremely difficult to make?', extr)

    dward = {"content_type":"text","title":"Yes","payload":'yes_dward'},{"content_type":"text","title":"No","payload":'no_dward'}
    if text == 'yes_extr' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'The teacher called, and lately his grades have been on a downward spiral?'.f, dward)
    if text == 'no_extr' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'The teacher called, and lately his grades have been on a downward spiral?', dward)

    mons = {"content_type":"text","title":"Yes","payload":'yes_mons'},{"content_type":"text","title":"No","payload":'no_mons'}
    if text == 'yes_dward' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your child is suddenly scared of monsters under the bed, and very jumpy at the slightest sounds?', mons)
    if text == 'no_dward' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your child is suddenly scared of monsters under the bed, and very jumpy at the slightest sounds?', mons)

    bio = {"content_type":"text","title":"Yes","payload":'yes_bio'},{"content_type":"text","title":"No","payload":'no_bio'}
    if text == 'yes_mons' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'One or both of the child’s biological parents has a history of depression?', bio)
    if text == 'no_mons' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'One or both of the child’s biological parents has a history of depression?', bio)

    unto = {"content_type":"text","title":"Yes","payload":'yes_unto'},{"content_type":"text","title":"No","payload":'no_unto'}
    if text == 'yes_bio' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'His favorite video game has sat untouched for weeks, even when you offered to have friends over to play with?', unto)
    if text == 'no_bio' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'His favorite video game has sat untouched for weeks, even when you offered to have friends over to play with?', unto)

    ride = {"content_type":"text","title":"Yes","payload":'yes_ride'},{"content_type":"text","title":"No","payload":'no_ride'}
    if text == 'yes_unto' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'She usually loves to ride her bike up and down the block, but when the neighbor stops by for a ride, she says she is too tired?', ride)
    if text == 'no_unto' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'She usually loves to ride her bike up and down the block, but when the neighbor stops by for a ride, she says she is too tired?', ride)

    soccr = {"content_type":"text","title":"Yes","payload":'yes_soccr'},{"content_type":"text","title":"No","payload":'no_soccr'}
    if text == 'yes_ride' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'He doesn’t want to join the soccer team this year because he says, “I was never any good at it anyways. Why bother?"?', soccr)
    if text == 'no_ride' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'He doesn’t want to join the soccer team this year because he says, “I was never any good at it anyways. Why bother?"?', soccr)

    agree = {"content_type":"text","title":"Yes","payload":'yes_ag'},{"content_type":"text","title":"No","payload":'no_ag'}
    if text == 'yes_soccr' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your usually agreeable child is now a constant grump?', agree)
    if text == 'no_soccr' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Your usually agreeable child is now a constant grump?', agree)
    
    if text == 'yes_ag' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'no_ag' and answer =='Depression':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'Depression':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has Depression.".format(average))
            choose_howto(sender_id,'remedies_depression','medication_depression','about_depression','Depression')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Depression.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has Depression.")
    #end depression
    #learning disorder
    if text =='Learning disorder': 
        Mongo.set_answer(users,sender_id,'Learning disorder')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "Does your child have trouble learning the alphabet, rhyming words, or connecting letters to their sounds?", alphabet)

    if text =='yes_alphabet' and answer == 'Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        awk= {"content_type":"text","title":"Yes","payload":'yes_awkward'},{"content_type":"text","title":"No","payload":'no_awkward'}                    
        bot.send_quick_replies_message(sender_id, 'Does your child appear awkward or clumsy, dropping, spilling, or knocking things over a lot?', awk)

    alou  = {"content_type":"text","title":"Yes","payload":'yes_alou'},{"content_type":"text","title":"No","payload":'no_alou'}   
    if text == 'yes_awkward':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child often make mistakes when reading aloud, and/or repeat and pause often?', alou)
    if text == 'no_awkward':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child often make mistakes when reading aloud, and/or repeat and pause often?', alou)

    retell = {"content_type":"text","title":"Yes","payload":'yes_retell'},{"content_type":"text","title":"No","payload":'no_retell'}     
    if text == 'yes_alou' and answer =='Learning disorder':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble retelling a story in order (what happened first, second, third)?', retell)
    if text == 'no_alou' and answer =='Learning disoder':  
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble retelling a story in order (what happened first, second, third)?', retell)
    if text =='no_alphabet' and answer == 'Learning disorder':       
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble retelling a story in order (what happened first, second, third)?', retell)

    reads = {"content_type":"text","title":"Yes","payload":'yes_reads'},{"content_type":"text","title":"No","payload":'no_reads'}     
    if text == 'yes_retell' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have a hard time undestanding what he or she reads?', reads)
    if text == 'no_retell' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have a hard time undestanding what he or she reads?', reads)

    buttns = {"content_type":"text","title":"Yes","payload":'yes_buttns'},{"content_type":"text","title":"No","payload":'no_buttns'}
    if text == 'yes_reads' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble with buttons, hooks, snaps, and zippers? Or with learning to tie his or her shoes?', buttns)
    if text == 'no_reads' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble with buttons, hooks, snaps, and zippers? Or with learning to tie his or her shoes?', buttns)

    langg = {"content_type":"text","title":"Yes","payload":'yes_lang'},{"content_type":"text","title":"No","payload":'no_lang'}
    if text == 'yes_buttns' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Did your child learn language late and/or have a limited vocabulary?', langg)
    if text == 'yes_buttns' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Did your child learn language late and/or have a limited vocabulary?', langg)

    spell = {"content_type":"text","title":"Yes","payload":'yes_spell'},{"content_type":"text","title":"No","payload":'no_spell'}
    if text == 'yes_langg' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have real trouble with spelling, trouble remembering the sounds that letters make, or trouble hearing slight differences between words?', spell)
    if text == 'no_langg' and answer =='Learning disorder':=
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have real trouble with spelling, trouble remembering the sounds that letters make, or trouble hearing slight differences between words?', spell)

    hum = {"content_type":"text","title":"Yes","payload":'yes_hum'},{"content_type":"text","title":"No","payload":'no_hum'}
    if text == 'yes_spell' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble understanding humor, puns, comic strips, idioms, and sarcasm?', hum)
    if text == 'no_spell' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble understanding humor, puns, comic strips, idioms, and sarcasm?', hum)

    writt = {"content_type":"text","title":"Yes","payload":'yes_writt'},{"content_type":"text","title":"No","payload":'no_writt'}
    if text == 'yes_hum' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child struggle to express ideas in writing?', writt)
    if text == 'no_hum' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child struggle to express ideas in writing?', writt)

    dire = {"content_type":"text","title":"Yes","payload":'yes_dire'},{"content_type":"text","title":"No","payload":'no_dire'}
    if text == 'yes_writt' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have difficulty understanding instructions or following directions?', dire)
    if text == 'no_writt' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have difficulty understanding instructions or following directions?', dire)

    conc = {"content_type":"text","title":"Yes","payload":'yes_conc'},{"content_type":"text","title":"No","payload":'no_conc'}
    if text == 'yes_dire' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble telling time or conceptualizing the passage of time?', conc)
    if text == 'no_dire' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble telling time or conceptualizing the passage of time?', conc)

    math = {"content_type":"text","title":"Yes","payload":'yes_math'},{"content_type":"text","title":"No","payload":'no_math'}
    if text == 'yes_conc' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child confuse math symbols and misread numbers?'., math)
    if text == 'no_conc' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child confuse math symbols and misread numbers?'., math)

    misp = {"content_type":"text","title":"Yes","payload":'yes_misp'},{"content_type":"text","title":"No","payload":'no_misp'}
    if text == 'yes_math' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child mispronounce words or use an incorrect word that sounds similar?', misp)
    if text == 'no_math' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child mispronounce words or use an incorrect word that sounds similar?', misp)

    orgz = {"content_type":"text","title":"Yes","payload":'yes_orgz'},{"content_type":"text","title":"No","payload":'no_orgz'}
    if text == 'yes_misp' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble organizing what he or she wants to say or thinking of the word he or she needs when writing or in conversation?', orgz)
    if text == 'no_misp' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have trouble organizing what he or she wants to say or thinking of the word he or she needs when writing or in conversation?', orgz)

    soci = {"content_type":"text","title":"Yes","payload":'yes_soci'},{"content_type":"text","title":"No","payload":'no_soci'}
    if text == 'yes_orgz' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child ignore the social rules of conversations, such as not taking turns or standing too close to his or her conversation partner?', soci)
    if text == 'no_orgz' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child ignore the social rules of conversations, such as not taking turns or standing too close to his or her conversation partner ?', soci)

    tsk = {"content_type":"text","title":"Yes","payload":'yes_tsk'},{"content_type":"text","title":"No","payload":'no_tsk'}
    if text == 'yes_soci' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have difficulty knowing where to begin a task or how to go on from there?', tsk)
    if text == 'no_soci' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have difficulty knowing where to begin a task or how to go on from there?', tsk)

    handw = {"content_type":"text","title":"Yes","payload":'yes_handw'},{"content_type":"text","title":"No","payload":'no_handw'}
    if text == 'yes_tsk' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have very messy handwriting or does he hold a pencil awkwardly?', handw)
    if text == 'no_tsk' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child have very messy handwriting or does he hold a pencil awkwardly?', handw)
    
    if text == 'yes_handw' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'no_handw' and answer =='Learning disorder':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'Learning disorder':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has Learning disorder.".format(average))
            choose_howto(sender_id,'remedies_learning','medication_learning','about_learning','Learning disorder')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Learning disorder.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has Learning disorder.")
    #end learning disorder
    #ODD
    if text =='ODD': 
        Mongo.set_answer(users,sender_id,'ODD')
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_text_message(sender_id, "{} please think about your child’s behaviors in the past 6 months".format(first_name(sender_id)))
        bot.send_quick_replies_message(sender_id, "Is your child unwilling or unable to compromise, give in, or negotiate with adults or peers?", unwilling)

    if text =='yes_unwilling' and answer == 'ODD':   
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        tchy = {"content_type":"text","title":"Yes","payload":'yes_touchy'},{"content_type":"text","title":"No","payload":'no_touchy'}                    
        bot.send_quick_replies_message(sender_id, 'Is your child touchy, prickly, or easily offended?', tchy)

    ignr  = {"content_type":"text","title":"Yes","payload":'yes_ignr'},{"content_type":"text","title":"No","payload":'no_ignr'}   
    if text == 'yes_touchy':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child test limits by ignoring rules or arguing?', ignr)
    if text == 'no_touchy':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child test limits by ignoring rules or arguing?', ignr)

    dfy = {"content_type":"text","title":"Yes","payload":'yes_dfy'},{"content_type":"text","title":"No","payload":'no_dfy'}     
    if text == 'yes_ignr' and answer =='ODD':  
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child actively defy or refuse to comply with requests and rules at home or at school?', dfy)
    if text == 'no_ignr' and answer =='ODD':    
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child actively defy or refuse to comply with requests and rules at home or at school?', dfy)
    if text =='no_unwilling' and answer == 'ODD':        
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child actively defy or refuse to comply with requests and rules at home or at school?', dfy)

    csq = {"content_type":"text","title":"Yes","payload":'yes_csq'},{"content_type":"text","title":"No","payload":'no_csq'}     
    if text == 'yes_dfy' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do you find that consequences dont work, nor do they have any impact on behavior? That your child just doesnt take rules seriously?', csq)
    if text == 'no_dfy' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do you find that consequences dont work, nor do they have any impact on behavior? That your child just doesnt take rules seriously?', csq)

    obrst = {"content_type":"text","title":"Yes","payload":'yes_obrst'},{"content_type":"text","title":"No","payload":'no_obrst'} 
    if text == 'yes_csq' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child unleash outbursts of anger and resentment?', obrst)
    if text == 'no_csq' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child unleash outbursts of anger and resentment?', obrst)

    justfy = {"content_type":"text","title":"Yes","payload":'yes_justfy'},{"content_type":"text","title":"No","payload":'no_justfy'} 
    if text == 'yes_obrst' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child try to justify their behavior as a response to unreasonable demands?', justfy)
    if text == 'no_obrst' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child try to justify their behavior as a response to unreasonable demands)?', justfy)

    bait = {"content_type":"text","title":"Yes","payload":'yes_bait'},{"content_type":"text","title":"No","payload":'no_bait'}
    if text == 'yes_justfy' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child bait classmates and pick fights with them by purposely doing things that annoy them?', bait)
    if text == 'no_justfy' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child bait classmates and pick fights with them by purposely doing things that annoy them?', bait)

    vind = {"content_type":"text","title":"Yes","payload":'yes_vind'},{"content_type":"text","title":"No","payload":'no_vind'}
    if text == 'yes_bait' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child spiteful, vindictive, or revenge seeking?', vind)
    if text == 'no_bait' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Is your child spiteful, vindictive, or revenge seeking?', vind)

    aggr = {"content_type":"text","title":"Yes","payload":'yes_aggr'},{"content_type":"text","title":"No","payload":'no_aggr'}
    if text == 'yes_vind' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get in trouble for being physically aggressive (i.e. shoving or hitting) other children?', aggr)
    if text == 'no_vind' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get in trouble for being physically aggressive (i.e. shoving or hitting) other children?', aggr)

    thrwng = {"content_type":"text","title":"Yes","payload":'yes_thrwng'},{"content_type":"text","title":"No","payload":'no_thrwng'}
    if text == 'yes_aggr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get in trouble at school for throwing things in class?', thrwng)
    if text == 'no_aggr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child get in trouble at school for throwing things in class?', thrwng)

    igni = {"content_type":"text","title":"Yes","payload":'yes_igni'},{"content_type":"text","title":"No","payload":'no_igni'}
    if text == 'yes_thrwng' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do you feel like your child is purposely trying to ignite your anger?', igni)
    if text == 'no_thrwng' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Do you feel like your child is purposely trying to ignite your anger?', igni)

    tempr = {"content_type":"text","title":"Yes","payload":'yes_tempr'},{"content_type":"text","title":"No","payload":'no_tempr'}
    if text == 'yes_igni' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child throw huge temper tantrums when getting home from school, and do the consequences for acting out make your child more agitated?', tempr)
    if text == 'no_igni' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child throw huge temper tantrums when getting home from school, and do the consequences for acting out make your child more agitated?', tempr)

    blme = {"content_type":"text","title":"Yes","payload":'yes_blme'},{"content_type":"text","title":"No","payload":'no_blme'}
    if text == 'yes_tempr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child blame others for their mistakes or misbehavior?', blme)
    if text == 'no_tempr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child blame others for their mistakes or misbehavior?', blme)

    excly = {"content_type":"text","title":"Yes","payload":'yes_excly'},{"content_type":"text","title":"No","payload":'no_excly'}
    if text == 'yes_blme' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child blame others for their mistakes or misbehavior?', excly)
    if text == 'no_blme' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child blame others for their mistakes or misbehavior?', excly)

    swr = {"content_type":"text","title":"Yes","payload":'yes_swr'},{"content_type":"text","title":"No","payload":'no_swr'}
    if text == 'yes_excly' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child blame others for their mistakes or misbehavior?' swr)
    if text == 'no_excly' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child blame others for their mistakes or misbehavior?', swr)

    trggr = {"content_type":"text","title":"Yes","payload":'yes_trggr'},{"content_type":"text","title":"No","payload":'no_trggr'} 
    if text == 'yes_swr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Can simple reminders, like to put socks in the hamper and not on the floor, trigger aggression or meltdowns?', trggr)
    if text == 'no_swr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Can simple reminders, like to put socks in the hamper and not on the floor, trigger aggression or meltdowns?', trggr)

    cruel = {"content_type":"text","title":"Yes","payload":'yes_cruel'},{"content_type":"text","title":"No","payload":'no_cruel'} 
    if text == 'yes_trggr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child say cruel, mean, or hateful things when upset?', cruel)
    if text == 'no_trggr' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, 'Does your child say cruel, mean, or hateful things when upset?', cruel)
    
    if text == 'yes_cruel' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'count_yes', count_yes + 1)
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    if text == 'no_cruel' and answer =='ODD':
        Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms + 1)
        bot.send_quick_replies_message(sender_id, "Oh right {} I already done checking symptoms.\nWant to know the result?".format(first_name(sender_id)), checkm)
    
    if text == 'yes_checkm' and answer == 'ODD':  
        print(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) == 100:
            average = get_average(count_yes, total_symptoms) - 1
        else:
            average = get_average(count_yes, total_symptoms)
        if get_average(count_yes, total_symptoms) >= 70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            bot.send_text_message(sender_id, "Base on my symptom checker the child have {}% chance that he/she has Oppositional Defiant Disorder.".format(average))
            choose_howto(sender_id,'remedies_odd','medication_odd','about_odd','Oppositional Defiant Disorder')
        elif get_average(count_yes, total_symptoms) <70:
            Mongo.set_patient(patient, sender_id, 'count_yes', 0)
            Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
            if get_average(count_yes, total_symptoms) == 100:
                average = get_average(count_yes, total_symptoms) - 1
            bot.send_text_message(sender_id, "Base on my symptom checker {} have {}% chance that {} might have Oppositional Defiant Disorder.".format(phrase2,average,phrase2))
            bot.send_text_message(sender_id, "It must have 70% or higher percentage rate base on symptoms that the child currently having before I can determine that he/she has Oppositional Defiant Disorder.")
    #end odd

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
        Mongo.create_patient(patient, sender_id, first_name(sender_id), '', '', 'myself',0,0)
        Mongo.set_ask(users, sender_id, "How old are you?")
        bot.send_text_message(sender_id, "May I ask how old are you? In human years.")
        bot.send_text_message(sender_id, "Just type '18'\nof course you are not 200 years old. 😉")   
    if text =='mychild':
        Mongo.create_patient(patient, sender_id, '', '', '', 'mychild',0,0)
        Mongo.set_ask(users, sender_id, "Whats the name of your child?")
        bot.send_text_message(sender_id, "Whats the name of your child {}?".format(first_name(sender_id)))    
    if text =='someone':
        Mongo.create_patient(patient, sender_id, '', '', '', 'someone',0,0)
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
        listofconcern = 'Attention Deficit Hyperactivity Disorder (ADHD)🤪,\nOppositional Defiant Disorder (ODD)😕,\nAutism Spectrum Disorder (ASD)😔,\nAnxiety Disorder😰,\nDepression😞,\nBipolar Disorder🤗😠,\nLearning Disorders🤔,'
        concern= 'mental health'
        after_accept_terms(sender_id,concern,listofconcern,"yes_proceed_mental","no_proceed_mental")
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
        bot.send_text_message(sender_id,"If you already know that the child had mental health problem and you simply need to realize how to deal with it.\nJust simply type it in⌨️\nFor example: 'adhd'")                                   
        listmental = {"content_type":"text","title":"ADHD","payload":"ADHD"},{"content_type":"text","title":"Anxiety","payload":"Anxiety"},{"content_type":"text","title":"Autism","payload":"Autism"},{"content_type":"text","title":"Bipolar","payload":"Bipolar"},{"content_type":"text","title":"Depression","payload":"Depression"},{"content_type":"text","title":"ODD","payload":"ODD"},{"content_type":"text","title":"Learning disorder","payload":"Learning_disorder"}                                             
        bot.send_quick_replies_message(sender_id, 'If you want to check the suspected mental health issue with your kid.\nJust tap your suspected meantal health concern {}.'.format(first_name(sender_id)), listmental)
    if text=='no_proceed_mental':     
        bot.send_text_message(sender_id,"I understand, Thank you for using DrPedia.\n")
        send_choose_concern(sender_id)
        
    if text=='yes_proceed_physical':
        bot.send_text_message(sender_id,"If you find that your concern needs immidiate action by a real doctor.\nI recommend you go to the nearest emergency clinic.")
        quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
        bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(first_name(sender_id)), quick_replies)
        '''button = [
                        {
                        "type": "postback",
                        "title": "🔍Check Symptom",
                        "payload": "physical_symptom_checker"
                        }
                        ]
        bot.send_button_message(sender_id, "If you don't have any idea🤔. Just tap 'Check Symptom'", button)'''
        
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
    #Dengue Remedies, Medication, About
    remedies_dengue = ["Take medicines that keep your fever under control", "Get plenty of rest and drink fluids to prevent dehydration", "In first week of infection, do not let a mosquito bite you for it will become infected and can infect other person", "In first week of infection, do not let a mosquito bite you for it will become infected and can infect other person", "Try to be in an air-conditioned room or under a bed net while you have fever", "Apply mosquito repellents regularly and wear clothes that cover your skin", "Take preventive measures at home by using screens on windows and doors", "You can repair holes in screens in order to keep mosquitoes outside", "Sleep under a mosquito bed net", "Regularly clean items that hold water such buckets, tires, planters, flowerpots, birdbaths, trash containers, etc", "Keep your indoors clean and wash floors with disinfectants regularly", "Giloy juice improves metabolism and builds immunity and helps in dengue fever effectively and helps to increase platelet counts", "Papaya leaf juice improves immunity which also helps in treating dengue and increases platelet counts", "Guava juice is rich in vitamin C that helps in building immunity and helps on treating dengue", "Fenugreek seeds are also rich in multiple nutrients which help in controlling dengue fever", "Fenugreek water provides health benefits as it is rich in vitamin C, K and fibre. Fenugreek water will bring down fever and boost immunity", "You must add immunity-boosting foods to your diet like citrus foods, garlic, almonds, turmeric and many more", "Chewing 5-6 basil leaves boosts your immunity and has been recommended as an effective Ayurvedic treatment for dengue fever", "Steep neem leaves and drink the brew to increase platelet and white blood cell count", "Oranges are rich in antioxidants and vitamins which help in treating the secondary symptoms of dengue", "Orange juice also repairs your body cells as it has Vitamin C which is crucial in creating collagen"]
    if payload=='remedies_dengue':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_dengue"}]
        bot.send_button_message(sender_id, random.choice(remedies_dengue), buttons) 
    if payload=='send_remedies_dengue':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_dengue"}]
        bot.send_button_message(sender_id, random.choice(remedies_dengue), buttons) 
    #End Dengue
    #Gastro Remedies, Medication, About
    remedies_gastro = ["Fluids: Diarrhea and vomiting can be dehydrating. Make sure you take in plenty of water, sports drinks, or other clear liquids.", "Ice cubes: If you are having trouble keeping fluids down, try sucking on ice chips to help rehydrate.", "BRAT diet: BRAT stands for Bananas, Rice, Applesauce, and Toast which can make your stools more firm.", "Bananas also contain potassium which can help replace nutrients lost from vomiting and diarrhea.", "Tea: Caffeine-free teas can help replenish lost fluids, and some varieties, such as peppermint, may calm the stomach, and ginger, may help ease nausea.", "Apple cider vinegar: Some people report this helps ease nausea and stomach upset.", "Rest: Most people need to rest for a few days to let the illness work its course.", "Heating pad: A heating pad may help relieve abdominal cramping.", "Choose low fat or fat free yogurt, if you can tolerate dairy products.", "Acupressure: Finger pressure is used to stimulate trigger points on the body that may help relieve nausea and vomiting.", "Let your stomach settle. Stop eating solid foods for a few hours.", "Try drinking clear soda, clear broths or noncaffeinated sports drinks.", "Drink plenty of liquid every day, taking small, frequent sips.", "Avoid certain foods and substances until you feel better. These include dairy products, caffeine, alcohol, nicotine, and fatty or highly seasoned foods."]
    if payload=='remedies_gastro':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_gastro"}]
        bot.send_button_message(sender_id, random.choice(remedies_gastro), buttons) 
    if payload=='send_remedies_gastro':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_gastro"}]
        bot.send_button_message(sender_id, random.choice(remedies_gastro), buttons) 
    #End Gastro
    #Tonsil Remedies, Medication, About
    remedies_tonsil = ["Drinking warm liquids, including soups, broths, and teas, can help soothe a sore throat.", "Herbal teas containing ingredients such as honey, pectin, or glycerine may help, as these ingredients form a protective film over the mucous membranes in the mouth and throat.", "Eating cold, soft foods, such as frozen yogurt or ice cream, can numb the throat, offering temporary pain relief.", "Try eating softer foods that are easier to swallow or stick to soups, broths, or chilled smoothies until their symptoms subside.", "Gargling with salt water may temporarily soothe pain or tickling in the back of the throat.", "People with tonsillitis may benefit from using a cool mist humidifier. These devices release moisture back into the air, helping alleviate throat discomfort.", "If speaking is painful, a person should try to rest the voice as much as possible. ", "Get as much rest as possible. Resting will allow the body to fight off the viral or bacterial infection.", "Throat sprays and gargles are another way to deliver anesthetic, anti-inflammatory, and antiseptic medications directly to the throat."]
    if payload=='remedies_tonsil':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_tonsil"}]
        bot.send_button_message(sender_id, random.choice(remedies_tonsil), buttons) 
    if payload=='send_remedies_tonsil':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_tonsil"}]
        bot.send_button_message(sender_id, random.choice(remedies_tonsil), buttons) 
    #End Tonsil
    #UTI Remedies, Medication, About
    remedies_uti = ["Drinking lots of water, and emptying your bladder when you need to, will help you flush harmful bacteria from your system.", "Try Unsweetened Cranberry Juice. Studies have shown that cranberries actually make it harder for the bacteria that causes UTIs to stick to the urinary tract walls.", "-Don’t “Hold It”, holding off going to the bathroom gives any bacteria that may already be in your bladder the chance to grow and multiply, potentially resulting in an infection.", "Eat garlic. A recent study showed that garlic extract may be effective in reducing the bacteria that causes UTIs.", "Some evidence shows that increasing your intake of vitamin C could protect against urinary tract infections.", "Red peppers, oranges, grapefruit and kiwifruit all contain the full recommended amount of vitamin C in just one serving .", "Probiotics are beneficial microorganisms that are consumed through food or supplements and promotes healthy balance of bacteria in your gut.", "When you have a UTI, caffeine, alcohol, spicy food, nicotine, carbonated drinks, and artificial sweeteners can irritate your bladder.", "Focus on healthy foods, such as high-fiber carbohydrates (such as oatmeal or lentil soup), that are good for your digestive health."]
    if payload=='remedies_uti':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_uti"}]
        bot.send_button_message(sender_id, random.choice(remedies_uti), buttons) 
    if payload=='send_remedies_uti':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_uti"}]
        bot.send_button_message(sender_id,  generated_remedies, buttons) 
    #End UTI
    #Flu Remedies, Medication, About
    remedies_flu = ["Drinking water and other fluids is even more important when you have the flu.", "Water helps to keep your nose, mouth, and throat moist. This helps your body get rid of built-up mucous and phlegm.", "It’s important to rest and get more sleep when you have the flu. Sleeping can help boost your immune system.", "Drinking warm chicken or beef bone broth is a good way to help you stay hydrated. It helps to loosen and break up nose and sinus congestion.", "-Drinking broth is a good way to replenish these nutrients while you have the flu. Plus, protein is important for rebuilding immune cells.", "The mineral zinc is important for your immune system. This nutrient helps your body make germ-fighting white blood cells.", "Several herbs have natural antiviral and antibacterial properties. Star anise is a star-shaped spice from which oseltamivir was traditionally extracted.", "Sweeten herbal teas with pure honey. Honey, royal jelly, and other bee products have been found to have natural antiviral and antibacterial properties.", "According to the study, tea tree oil works best when it’s used within two hours of infection. This shows that it may help to block the flu virus from multiplying.", "In practice, you might add a few drops of tea tree oil to liquid hand soap when you wash your hands or mixed into lotion you use.", "-Using a humidifier to add humidity in your home and workplace might help reduce flu viruses in the air.", "Breathing in steam from a warm pot of water can help soothe your nose, sinuses, throat, and lungs. Steam inhalation might help to soothe a dry cough, irritated nose, and chest tightness."]
    if payload=='remedies_flu':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_flu"}]
        bot.send_button_message(sender_id, random.choice(remedies_flu), buttons) 
    if payload=='send_remedies_flu':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_flu"}]
        bot.send_button_message(sender_id, random.choice(remedies_flu), buttons) 
    #End flu
    if payload=='ready_accept':
        Mongo.set_terms(users, sender_id,'Yes')
        bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff")
        send_choose_concern(sender_id)
        
    #ADHD
    remedies_adhd = ["Forgo food colorings and preservatives", "Avoid potential allergens, Diets that restrict possible allergens may help improve behavior in some children with ADHD.", "Consider a yoga or tai chi class, Some small studies indicate that yoga may be helpful for people with ADHD.", "Spending time outside may benefit children with ADHD. There is strong evidence that spending even 20 minutes outside can benefit them by improving their concentration.", "Omega-3 Fatty Acids for ADHD, The omega-3 fatty acids found in fish oil are important in brain and nerve cell function.", "Protein for ADHD, Protein also prevents surges in blood sugar that may increase hyperactivity.", "Vitamin C is a building block of neurotransmitters, while iron and vitamin B6 increase dopamine levels. Zinc regulates dopamine, and may help treat ADHD symptoms in some children when used with conventional medication and treatments.", "Exercise helps the ADHD brain function more effectively and efficiently. One well-known benefit of exercise is an increase in endorphins, which can improve mood. ", "Studies have shown that 20 minutes a day spent in nature may improve ADHD symptoms. Green time is especially effective in helping kids recover from attention fatigue, which occurs after a long school day.", "Clinical trials have found that a number of herbal treatments may show promise for treating ADHD such as French Maritime pine bark extract, Ginseng, Ningdong, Bacopa.", "Creating systems for regular activities, such as getting ready for school, can help children with ADHD learn how to recognize and feel comfortable with routines."]
    if payload=='remedies_adhd':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_adhd"}]
        bot.send_button_message(sender_id, random.choice(remedies_adhd), buttons)   
    if payload=='send_remedies_adhd':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_adhd"}]
        bot.send_button_message(sender_id, random.choice(remedies_adhd), buttons)                                         
    #About                                       
    if payload=='about_adhd':
        bot.send_text_message(sender_id,'Attention deficit hyperactivity disorder (ADHD) is a mental health disorder that can cause above-normal levels of hyperactive and impulsive behaviors.\nPeople with ADHD may also have trouble focusing their attention on a single task or sitting still for long periods of time.')
        buttons = [{"type": "postback","title": "ADHD Symptoms", "payload": "send_symptoms_adhd" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of ADHD?", buttons)
    if payload=='send_symptoms_adhd':                                                                                                                                                                                                                                   
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
        buttons = [{"type": "postback","title": "Cause of ADHD","payload": "send_cause_adhd"}]
        bot.send_button_message(sender_id, "What causes ADHD?", buttons)
    if payload=='send_cause_adhd':   
        bot.send_text_message(sender_id,"Despite how common ADHD is, doctors and researchers still aren’t sure what causes the condition. It’s believed to have neurological origins. Genetics may also play a role.")
     #ADHD END  
    #Anxiety
    remedies_Anxiety = ["Drink chamomile tea, Chamomile’s compounds may ease general anxiety disorder symptoms, according to a small study published in 2016 in the journal Phytomedicine.", "Get your daily dose of omega-3s." "Try putting a few drops of lavender essential oil on your pillow or in your bath, or add a few drops to a cup of boiling water and inhale for a quick calm-me-down.", "Add L-lysine to your diet, It found that a combination of L-lysine and L-arginine was “a potentially useful dietary intervention in otherwise healthy humans with high subjective levels of mental stress and anxiety.", "Get some sunlight, Head outdoors to naturally increase your vitamin D levels and decrease anxiety.", "Exercise to combat stress, Get moving to help reduce your anxiety. After all, the Anxiety and Depression Association of America states that even just brief walks lasting about 10 minutes may boost mood.", "Take a hot bath with epsom salts, First, a hot bath is always calming. Second, adding some epsom salts to the water may help boost your mood. These salts contain magnesium sulfate, which may have anxiety-fighting benefits.", "Cut out (or down) caffeine, You probably head for your coffee maker or local cafe every morning. However, if you’re struggling with anxiety, you might want to re-evaluate your caffeine habit.", "Avoid these foods such as Caffeine, alcohol, and added sugars. The Mayo Clinic states that alcohol and caffeine, for example, can worsen anxiety.", "Eat these foods such as Blueberries and peaches contain nutrients that relieve stress and have a calming effect, Whole grains are rich in magnesium and tryptophan, an amino acid that your body converts to serotonin. Serotonin is known to calm and improve your mood, Oats also increase serotonin production and are high in fiber, which helps prevent blood sugar spikes that affect mood, Avocados, eggs, milk, and meat are all packed with B vitamins that can help prevent anxiety, Foods that help regulate and lower the stress hormone cortisol include foods rich in vitamin C, like oranges, omega-3 fatty acids, and magnesium-rich, foods like spinach and other dark leafy greens. Indulge every once in a while in dark chocolate, which also helps lower cortisol."]
    if payload=='remedies_anxiety':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_anxiety"}]
        bot.send_button_message(sender_id, random.choice(remedies_Anxiety), buttons)   
    if payload=='send_remedies_anxiety':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_anxiety"}]
        bot.send_button_message(sender_id, random.choice(remedies_Anxiety), buttons)                                         
    #medication
    #About   
    #Anxiety END  
    #Autism
    remedies_ASD = ["Creative therapies, Some parents choose to supplement educational and medical intervention with art therapy or music therapy, which focuses on reducing a child's sensitivity to touch or sound.", "Sensory-based therapies, These therapies are based on the unproven theory that people with autism spectrum disorder have a sensory processing disorder that causes problems tolerating or processing sensory information, such as touch, balance and hearing.", "Pet or horse therapy, Pets can provide companionship and recreation, but more research is needed to determine whether interaction with animals improves symptoms of autism spectrum disorder.", "Acupuncture, This therapy has been used with the goal of improving autism spectrum disorder symptoms, but the effectiveness of acupuncture is not supported by research."]
    if payload=='remedies_autism':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_autism"}]
        bot.send_button_message(sender_id, random.choice(remedies_ASD), buttons)   
    if payload=='send_remedies_autism':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_autism"}]
        bot.send_button_message(sender_id, random.choice(remedies_ASD), buttons)                                         
    #medication
    #About   
    #Autsim END  
    #Bipolar
    remedies_Bipolar = ["Rhodiola, Officially known as rhodiola rosea, this herb has been used for years to help manage stress and has also demonstrated positive effects on people struggling with depression.", "Meditation, People who meditate using a supervised mindfulness-based cognitive therapy approach may see a reduction in depression that directly correlates to how many days they meditate.", "Omega-3 Fatty Acids, That's because the anti-inflammatory effects of omega-3 fatty acids could help regulate mood.", "Avoiding the "Western" style diet that's rich in red meats, saturated fats and trans fats, and simple carbohydrates", "Eating less saturated fats and simple carbohydrates can help overall health but does not directly affect the symptoms of bipolar disorder.", "Eating a balance of protective, nutrient-dense foods. These foods include fresh fruits, vegetables, legumes, whole grains, lean meats, cold-water fish, eggs, low-fat dairy, soy products, and nuts and seeds.", "Watching caloric intake and exercising regularly to maintain a healthy weight", "Getting only moderate amounts of caffeine and not stopping caffeine use abruptly", "Avoiding high-fat meals to lower the risk for obesity", "Calming techniques such as massage therapy, yoga, acupuncture, meditation", "Adequate sleep can help stabilize your mood and reduce irritability. Tips to improve sleep include establishing a routine and creating a calm bedroom environment.", "Many people with bipolar disorder find if they stick to a daily schedule, it helps them control their mood.", "Tame stress, So take time to relax.Lying on the couch watching TV or checking your social media accounts isn't the best way to go. Instead, try something more focused, like yoga or other types of exercise. Meditation is another good choice."]
    if payload=='remedies_bipolar':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_bipolar"}]
        bot.send_button_message(sender_id, random.choice(remedies_Bipolar), buttons)   
    if payload=='send_remedies_bipolar':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_bipolar"}]
        bot.send_button_message(sender_id, random.choice(remedies_Bipolar), buttons)                                         
    #medication
    #About   
    #Bipolar END  
    #Depression
    remedies_Depression = ["Omega-3 Fatty Acids, That's because the anti-inflammatory effects of omega-3 fatty acids could help regulate mood.", "According to a study in Alternative Medicine ReviewTrusted Source, taking saffron stigma has been shown to be effective in treating mild to moderate depression.", "Taking 500 micrograms of folic acid has been linked with improving the effectiveness of other antidepressant medications.", "According to Nutrition NeuroscienceTrusted Source, taking a 25-milligram zinc supplement daily for 12 weeks can help reduce depression symptoms.", "Get in a routine, Setting a gentle daily schedule can help you get back on track.", "When you're depressed, you may feel like you can't accomplish anything. That makes you feel worse about yourself. To push back, set daily goals for yourself.", "Exercise, It temporarily boosts feel-good chemicals called endorphins. It may also have long-term benefits for people with depression.", "Eat healthy, If depression tends to make you overeat, getting in control of your eating will help you feel better.", "Get enough sleep, Go to bed and get up at the same time every day. Take all the distractions out of your bedroom no computer and no TV.", "Staying involved and having daily responsibilities can help you maintain a lifestyle that can help counter depression.", "Challenge negative thoughts, The next time you're feeling terrible about yourself, use logic as a natural depression treatment.", "Do something new, When you’re depressed, you’re in a rut. Push yourself to do something different.", "If you’re depressed, make time for things you enjoy. Plan things you used to enjoy, even if they feel like a chore.", "Get some sunlight, You might find that getting some sun can put you in a better mood.", "Set aside time to do things that you used to enjoy doing. Make a plan to go out to dinner or a movie with friends or return to a hobby that you used to pursue. Try expressing yourself creatively." "Avoid alcohol and drugs, Alcohol and many illicit drugs can contribute to depression and make it worse.", "Get out with your family or friends or take up a hobby that used to give you pleasure. Staying active and connected with the people in your life may help you feel better.", "Take ‘TIME OUT” for yourself regularly, even as little as 15 minutes per day, may be very helpful. Use that time for relaxation, to meet personal needs, or anything that will “re-charge your mental battery”.",]
    if payload=='remedies_depression':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_depression"}]
        bot.send_button_message(sender_id, random.choice(remedies_Depression), buttons)   
    if payload=='send_remedies_depression':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_depression"}]
        bot.send_button_message(sender_id, random.choice(remedies_Depression), buttons)                                         
    #medication
    #About   
    #Depression END   
    #Learning
    remedies_LearningDisorder = ["Ask your child to list their strengths and weaknesses and talk about your own strengths and weaknesses with your child.", "Encourage your child to talk to adults with learning disabilities and to ask about their challenges, as well as their strengths.", "Work with your child on activities that are within their capabilities. This will help build feelings of success and competency.", "Help your child develop their strengths and passions. Feeling passionate and skilled in one area may inspire hard work in other areas too.", "Talk with your learning disabled child about problem solving and share how you approach problems in your life.", "Ask your child how they approach problems. How do problems make them feel? How do they decide what action to take?", "If your child is hesitant to make choices and take action, try to provide some “safe” situations to test the water, like choosing what to make for dinner or thinking of a solution for a scheduling conflict.", "Discuss different problems, possible decisions, and outcomes with your child. Have your child pretend to be part of the situation and make their own decisions.", "Talk with your child about times when they persevered—why did they keep going? Share stories about when you have faced challenges and not given up.", "Discuss what it means to keep going even when things aren’t easy. Talk about the rewards of hard work, as well as the opportunities missed by giving up.", "When your child has worked hard, but failed to achieve their goal, discuss different possibilities for moving forward.", "Help your child identify a few short- or long-term goals and write down steps and a timeline to achieve the goals. Check in periodically to talk about progress and make adjustments as needed.", "Talk about your own short- and long-term goals with your child, as well as what you do when you encounter obstacles.", "Celebrate with your child when they achieve a goal. If certain goals are proving too hard to achieve, talk about why and how plans or goals might be adjusted to make them possible.", "Help your child nurture and develop good relationships. Model what it means to be a good friend and relative so your child knows what it means to help and support others.", "Demonstrate to your child how to ask for help in family situations.", "Share examples of people needing help, how they got it, and why it was good to ask for help. Present your child with role-play scenarios that might require help.", "Use words to identify feelings and help your child learn to recognize specific feelings.", "Ask your child the words they would use to describe stress. Does your child recognize when they are feeling stressed?", "Encourage your child to identify and participate in activities that help reduce stress like sports, games, music, or writing in a journal.", "Ask your child to describe activities and situations that make them feel stressed. Break down the scenarios and talk about how overwhelming feelings of stress and frustration might be avoided."]
    if payload=='remedies_learning':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_learning"}]
        bot.send_button_message(sender_id, random.choice(remedies_LearningDisorder), buttons)   
    if payload=='send_remedies_learning':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_learning"}]
        bot.send_button_message(sender_id, random.choice(remedies_LearningDisorder), buttons)                                         
    #medication
    #About   
    #Learning END  
    #ODD
    remedies_ODD = ["Always build on positives: Praise your child and offer positive reinforcement when he shows flexibility or cooperation. Recognize the “little victories” with enthusiasm.", "Learn to control yourself: Take a time-out or break if you suspect you are about to make the conflict with your child worse, not better.", "Pick your battles: Since a child with ODD has trouble avoiding power struggles, prioritize the demands you put on your child.", "Provide structure: Bad behavior tends to escalate when a child has unsupervised free time and unclear expectations. A daily routine, on the other hand, lets a child know what to expect.", "Position behavioral issues as problems she can solve: Explain to your child that ignoring an alarm clock doesn’t help her get to school on time, and ask what she can do to avoid being tardy again.", "Set up reasonable, age-appropriate limits and enforce consequences consistently: Resist the temptation to rescue the child from naturally occurring consequences.", "Don’t go it alone: Work with and get support from the other adults (teachers, coaches, and spouse) who interact with your child. Look for local support groups and/or parenting classes for parents of difficult children.", "Avoid burnout: Maintain interests other than your child so that managing her behavior doesn’t sap all of your time and energy. Manage your own stress with exercise and relaxation. Use respite care as needed.", "Recognize and praise your child's positive behaviors. Be as specific as possible, such as, I really liked the way you helped pick up your toys tonight.", "Providing rewards for positive behavior also may help, especially with younger children.", "Model the behavior you want your child to have. Demonstrating appropriate interactions and modeling socially appropriate behavior can help your child improve social skills.", "Pick your battles and avoid power struggles. Almost everything can turn into a power struggle, if you let it.", "Set limits by giving clear and effective instructions and enforcing consistent reasonable consequences. Discuss setting these limits during times when you're not confronting each other.", "Set up a routine by developing a consistent daily schedule for your child. Asking your child to help develop that routine may be beneficial.", "Build in time together by developing a consistent weekly schedule that involves you and your child spending time together.", "Work together with your partner or others in your household to ensure consistent and appropriate discipline procedures. Also enlist support from teachers, coaches and other adults who spend time with your child.", "Assign a household chore that's essential and that won't get done unless the child does it. Initially, it's important to set your child up for success with tasks that are relatively easy to achieve and gradually blend in more important and challenging expectations. Give clear, easy-to-follow instructions.", "Be prepared for challenges early on. At first, your child probably won't be cooperative or appreciate your changed response to his or her behavior. Expect behavior to temporarily worsen in the face of new expectations. Remaining consistent in the face of increasingly challenging behavior is the key to success at this early stage."]
    if payload=='remedies_odd':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_odd"}]
        bot.send_button_message(sender_id, random.choice(remedies_ODD), buttons)   
    if payload=='send_remedies_odd':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_odd"}]
        bot.send_button_message(sender_id, random.choice(remedies_ODD), buttons)                                         
    #medication
    #About   
    #ODD END  
    if payload=='mental_symptom_checker':
        bot.send_text_message(sender_id,"How old is the patient?\n Just type 'age:17' for example")
    '''    
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
    '''    
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
    
def choose_howto(sender_id,payload1,payload2,payload3,name):
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
    bot.send_quick_replies_message(sender_id, 'What is your concern about?', quick_replies)
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
