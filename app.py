#Libraries to be import START
import random
from flask import Flask, request
from messnger_syntax.bot import Bot
import os
import pymongo
from pymongo import MongoClient
import Mongo#import Mongo.py
#from NLU import nlp
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
    
    #if nlp.nlp(text) == 'fever':
       # bot.send_text_message(sender_id, "That doesn't sound healthy")
    
    if ask == "pleased to meet me?":
        oneqrbtn = [{"content_type":"text","title":"Nice meeting you 🤗","payload":'pmyou'}]
        bot.send_quick_replies_message(sender_id, 'Are you not glad to meet me {}😕?'.format(first_name(sender_id)), oneqrbtn) 
    
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
    
    if text=='pmyou':
        Mongo.set_ask(users,sender_id,'accept terms?')
        Mongo.set_answer(users,sender_id,'glad to meet you')
        bot.send_text_message(sender_id,"I'm pleased to meet you too {}. 😉".format(first_name(sender_id)))  
        greet_disclaimer(sender_id)
    
    
    
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

    
    
    if text =="yes_agree":
        Mongo.set_terms(users, sender_id,'Yes')
        bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff.")
        oneqrbtn = [{"content_type":"text","title":"Check Symptoms 🔍","payload":'check_symptoms'}]
        bot.send_quick_replies_message(sender_id, 'How can I assist you today {}?\nI can check your/your childs symptoms🔍 and provide you pre-emptive medication afterwards.'.format(first_name(sender_id)), oneqrbtn)
    if text=='see_details':
        bot.send_text_message(sender_id,"Sure {} here it is..".format(first_name(sender_id)))
        bot.send_text_message(sender_id,"Privacy Policy:\nhttps://www.termsfeed.com/privacy-policy/97973f4396e1a79a806facb4e007ed3e")
        bot.send_text_message(sender_id,"Terms and Conditions:\nhttps://www.termsfeed.com/terms-conditions/ec54290a74978eb95a1851754137c944")
        oneqrbtn = [{"content_type":"text","title":"🤝Agree and proceed","payload":'ready_accept'}]
        bot.send_quick_replies_message(sender_id, 'Ready to go?', oneqrbtn)
    if text == 'ready_accept':
        Mongo.set_terms(users, sender_id,'Yes')
        bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff.")
        oneqrbtn = [{"content_type":"text","title":"Check Symptoms 🔍","payload":'check_symptoms'}]
        bot.send_quick_replies_message(sender_id, 'How can I assist you today {}?\nI can check your/your childs symptoms🔍 and provide you pre-emptive medication afterwards.'.format(first_name(sender_id)), oneqrbtn)
    
    if text == 'check_symptoms':
        bot.send_text_message(sender_id,"If you find that your concern needs immidiate action by a real doctor.\nI recommend you go to the nearest emergency clinic/hospital!")
        quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
        bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(first_name(sender_id)), quick_replies)

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
    #About
    if payload=='about_dengue':
        bot.send_text_message(sender_id,'Dengue fever is a disease spread by the Aedes aegypti mosquito and is caused by one of four dengue viruses. Once you are infected with one of the dengue viruses, you will develop immunity to that virus for the rest of your life.\nHowever, you can still be infected with the other three viruses. It is possible to get all four dengue viruses in your lifetime.\nThe viruses that cause dengue fever are related to those that cause yellow fever and West Nile virus infection.')
        buttons = [{"type": "postback","title": "Dengue Symptoms", "payload": "send_symptoms_dengue" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Dengue?", buttons)
    if payload=='send_symptoms_dengue':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Symptoms generally last for about 10 days and can include:\nsudden, high fever (up to 106 degrees Fahrenheit)\nsevere headache\nswollen lymph glands\nsevere joint and muscle pains\nskin rash (appearing between two and five days after the initial fever)\nmild to severe nausea\nmild to severe vomiting\nmild bleeding from the nose or gums\nmild bruising on the skin\nfebrile convulsions")
    #Medication
    if payload=='medication_dengue':
        if age in range(6,12) and weight in range(16,20):
            bot.send_text_message(sender_id,"Paracetamol 250mg/5ml\ndosage:5ml, 7.5ml, 9ml, 10ml every 4 hours as needed")
        if age in range(13,15) and weight in range(17,25):   
            bot.send_text_message(sender_id,"Paracetamol 250mg tablet\ndosage:1 tablet every 4 hours as needed")
        if age in range(15,20) or int(age) > 15 and weight in range(26,30) or weight > 30:  
            bot.send_text_message(sender_id,"Paracetamol 500mg tablet\ndosage:1 tablet every 4 hours as needed")
        if age in range(1,12) and weight in range(8,17):
            bot.send_text_message(sender_id,"Carbocisteine suspension\ndosage:2.5ml, 5ml, 7.5ml, 10ml 3x a day for 7 days")
        if age in range(13,15):    
            bot.send_text_message(sender_id,"Carbocisteine 250mg capsule\ndosage:1 capsule 3x a day for 7 days")
        if age in range(16,20) or int(age) > 20:
            bot.send_text_message(sender_id,"Carbocisteine 500mg capsule\ndosage:1 capsule 3x a day for 7 days")
        if age in range(1,2) and weight in range(5,10):    
            bot.send_text_message(sender_id,"Phenylephrine HCI suspension\ndosage:2.5ml 3x a day for 5 days")
        if age in range(3,12):        
            bot.send_text_message(sender_id,"Phenylephrine HCI suspension\ndosage:5ml 3x day for 5 days")
        if age in range(12,16):    
            bot.send_text_message(sender_id,"Phenylephrine HCI 250mg tablet\ndosage:1 tablet 3x a day")
        if age in range(17,20) or int(age) > 20:     
            bot.send_text_message(sender_id,"Phenylephrine HCI 500mg tablet\ndosage:1 tablet 3x a day")
        if age in range(1,10):    
            bot.send_text_message(sender_id,"Cetirizine tablet\ndosage:1 tablet once a day for 7 days")
        if age in range(11,20) or int(age) > 20:    
            bot.send_text_message(sender_id,"Cetirizine tablet: 11-20 dosage:1 tablet once a day for 7 days")
        if age in range(1,8):    
            bot.send_text_message(sender_id,"Simeticone drops\ndosage:1ml 3x a day for 7 days")
        if age in range(9,15) or int(age) > 15:    
            bot.send_text_message(sender_id,"Simeticone tablet\ndosage:1 tablet 3x a day for 7 days")
        if age in range(1,13):    
            bot.send_text_message(sender_id,"Hyoscine-N-Butybromide suspension\ndosage:5ml every 6 hours as needed")
        if age in range(14,19) or int(age) > 19:    
            bot.send_text_message(sender_id,"Hyoscine-N-Butybromide 10mg tablet\ndosage:1 tablet every 6 hours as needed")
        if age in range(1,5) and weight in range(10,15):    
            bot.send_text_message(sender_id,"Co-Amoxiclav 125mg/5ml suspension\ndosage:3.5ml, 5ml, 6ml, 7ml 2x a day for 7 days")
        if age in range(6,12) and weight in range(16,19):    
            bot.send_text_message(sender_id,"Co-Amoxiclav 250mg/5ml suspension\ndosage:7.5ml, 9ml, 10ml, 10.5ml 2x a day for 7 days")
        if age in range(13,16):    
            bot.send_text_message(sender_id,"Co-Amoxiclav 250mg tablet\ndosage:1 tablet 2x a day for 7 days")
        if age in range(17,20) or int(age) > 20:    
            bot.send_text_message(sender_id,"Co-Amoxiclav 500mg tablet\ndosage:1 tablet 2x a day for 7 days")
        if age in range(1,11):    
            bot.send_text_message(sender_id,"Domperidone suspension\ndosage:2.5ml, 5ml, 7.5ml every 6 hours as needed or 3x a day for 5 days")
        if age in range(12,19) or int(age) > 19:    
            bot.send_text_message(sender_id,"Domperidone 10mg tablet\ndosage:1 tablet every 6 hours as needed or 3x a day for 5 days")
    #End Dengue
    #Gastro Remedies, Medication, About
    remedies_gastro = ["Fluids: Diarrhea and vomiting can be dehydrating. Make sure you take in plenty of water, sports drinks, or other clear liquids.", "Ice cubes: If you are having trouble keeping fluids down, try sucking on ice chips to help rehydrate.", "BRAT diet: BRAT stands for Bananas, Rice, Applesauce, and Toast which can make your stools more firm.", "Bananas also contain potassium which can help replace nutrients lost from vomiting and diarrhea.", "Tea: Caffeine-free teas can help replenish lost fluids, and some varieties, such as peppermint, may calm the stomach, and ginger, may help ease nausea.", "Apple cider vinegar: Some people report this helps ease nausea and stomach upset.", "Rest: Most people need to rest for a few days to let the illness work its course.", "Heating pad: A heating pad may help relieve abdominal cramping.", "Choose low fat or fat free yogurt, if you can tolerate dairy products.", "Acupressure: Finger pressure is used to stimulate trigger points on the body that may help relieve nausea and vomiting.", "Let your stomach settle. Stop eating solid foods for a few hours.", "Try drinking clear soda, clear broths or noncaffeinated sports drinks.", "Drink plenty of liquid every day, taking small, frequent sips.", "Avoid certain foods and substances until you feel better. These include dairy products, caffeine, alcohol, nicotine, and fatty or highly seasoned foods."]
    if payload=='remedies_gastro':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_gastro"}]
        bot.send_button_message(sender_id, random.choice(remedies_gastro), buttons) 
    if payload=='send_remedies_gastro':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_gastro"}]
        bot.send_button_message(sender_id, random.choice(remedies_gastro), buttons) 
    #About
    if payload=='about_gastroenteritis':
        bot.send_text_message(sender_id,'Gastroenteritis is an inflammation of the lining of the intestines caused by a virus, bacteria, or parasites. Viral gastroenteritis is the second most common illness in the U.S. The cause is often a norovirus infection.\n It spreads through contaminated food or water or by contact with an infected person. The best prevention is frequent hand washing.')
        buttons = [{"type": "postback","title": "Gastroenteritis Symptoms", "payload": "send_symptoms_gastroenteritis" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Gastroenteritis?", buttons)
    if payload=='send_symptoms_gastroenteritis':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Symptoms of viral gastroenteritis includes:\ndiarrhea\nnausea and vomiting\nheadache, muscle aches, or joint aches\nfever or chills\nsweating or clammy skin\nabdominal cramps and pain\nloss of appetite\nSymptoms of bacterial gastroenteritis:\nloss of appetite\nnausea and vomiting\ndiarrhea\nabdominal pains and cramps\nblood in your stools\nfever")
        buttons = [{"type": "postback","title": "Cause of Gastroenteritis","payload": "send_cause_gastroenteritis"}]
        bot.send_button_message(sender_id, "What causes Gastroenteritis?", buttons)
    if payload=='send_cause_gastroenteritis':   
        bot.send_text_message(sender_id,"Numerous bacteria can cause gastroenteritis, including:\nyersinia, found in pork\nstaphylococcus, found in dairy products, meat, and eggs\nshigella, found in water (often swimming pools)\nsalmonella, found in meat, dairy products, and eggs\ncampylobacter, found in meat and poultry\nE. coli, found in ground beef and salads\n\nBacterial gastroenteritis outbreaks can happen when restaurants serve contaminated food to many people. An outbreak can also trigger recalls of produce and other foods.\nBacterial gastroenteritis can be easily transmitted from person to person if someone carries the bacteria on their hands. Every time a person infected with this bacteria touches food, objects, or other people, they risk spreading the infection to others. You can even cause the infection to get into your own body if you touch your eyes, mouth, or other open parts of your body with infected hands.\nYou’re especially at risk for these infections if you travel a lot or live in a crowded area. Washing your hands often and using hand sanitizer with more than 60 percent alcohol can help you avoid catching infections from the people around you.")
    #Medication
    if payload=='medication_gastro':
        if age in range(5,11):    
            bot.send_text_message(sender_id,"Domperidone suspension\ndosage:5ml, 7.5ml, 10ml every 6 hours as needed or 3x a day for 5 days")
        if age in range(12,19) or int(age) > 19:    
            bot.send_text_message(sender_id,"Domperidone 10mg tablet\ndosage:1 tablet every 6 hours as needed or 3x a day for 5 days")
        if age in range(5,13):    
            bot.send_text_message(sender_id,"Hyoscine-N-Butybromide suspension\ndosage:5ml every 6 hours as needed")
        if age in range(14,19) or int(age) > 19:    
            bot.send_text_message(sender_id,"Hyoscine-N-Butybromide 10mg tablet\ndosage:1 tablet every 6 hours as needed")
        if age in range(5,8):    
            bot.send_text_message(sender_id,"Simeticone drops\ndosage:1ml 3x a day for 7 days")
        if age in range(9,15) or int(age) > 15:    
            bot.send_text_message(sender_id,"Simeticone tablet\ndosage:1 tablet 3x a day for 7 days")
        if age in range(5,8):    
            bot.send_text_message(sender_id,"Simeticone drops\ndosage:1ml 3x a day for 7 days")
        if age in range(5,10):    
            bot.send_text_message(sender_id,"Racecadotril 10mg sachet\ndosage:1 sachet 3x a day for 5 days")
        if age in range(11,15):    
            bot.send_text_message(sender_id,"Racecadotril 30mg sachet\ndosage:1 sachet 3x a day for 5 days")
        if age in range(16,20) or int(age) > 20:    
            bot.send_text_message(sender_id,"Racecadotril 100mg capsule\ndosage:1 capsule 3x a day for 5 days")
        if age in range(16,20) or int(age) > 20:    
            bot.send_text_message(sender_id,"Omeprazole 40mg capsule\ndosage:1 capsule every 7am for 7 days")
        if age in range(5,15):    
            bot.send_text_message(sender_id,"Nifuroxazide suspension\ndosage:5ml, 7.5ml, 10ml 3x a day for 7 days")
        if age in range(16,20)or int(age) > 20:    
            bot.send_text_message(sender_id,"Nifuroxazide 100mg capsule\ndosage:1 capsule 3x a days for 7 days")
        if age in range(12,20) or int(age) >20:    
            bot.send_text_message(sender_id,"Loperamide capsule\ndosage:1 capsule 3x a day for 5 days ")
    #End Gastro
    #Tonsil Remedies, Medication, About
    remedies_tonsil = ["Drinking warm liquids, including soups, broths, and teas, can help soothe a sore throat.", "Herbal teas containing ingredients such as honey, pectin, or glycerine may help, as these ingredients form a protective film over the mucous membranes in the mouth and throat.", "Eating cold, soft foods, such as frozen yogurt or ice cream, can numb the throat, offering temporary pain relief.", "Try eating softer foods that are easier to swallow or stick to soups, broths, or chilled smoothies until their symptoms subside.", "Gargling with salt water may temporarily soothe pain or tickling in the back of the throat.", "People with tonsillitis may benefit from using a cool mist humidifier. These devices release moisture back into the air, helping alleviate throat discomfort.", "If speaking is painful, a person should try to rest the voice as much as possible. ", "Get as much rest as possible. Resting will allow the body to fight off the viral or bacterial infection.", "Throat sprays and gargles are another way to deliver anesthetic, anti-inflammatory, and antiseptic medications directly to the throat."]
    if payload=='remedies_tonsil':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_tonsil"}]
        bot.send_button_message(sender_id, random.choice(remedies_tonsil), buttons) 
    if payload=='send_remedies_tonsil':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_tonsil"}]
        bot.send_button_message(sender_id, random.choice(remedies_tonsil), buttons) 
    #About
    if payload=='about_tonsillitis':
        bot.send_text_message(sender_id,'Tonsils are the two lymph nodes located on each side of the back of your throat. They function as a defense mechanism and help prevent your body from getting an infection. When tonsils become infected, the condition is called tonsillitis.\nTonsillitis can occur at any age and is a common childhood illness. It’s most often diagnosed in children from preschool age through their mid-teens. Symptoms include a sore throat, swollen tonsils, and fever.')
        buttons = [{"type": "postback","title": "Tonsillitis Symptoms", "payload": "send_symptoms_tonsillitis" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Tonsillitis?", buttons)
    if payload=='send_symptoms_tonsillitis':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Possible symptoms of tonsillitis include:\na very sore throat\ndifficulty or pain while swallowing\na scratchy-sounding voice\nbad breath\nfever\nchills\nearaches\nstomachaches\nheadaches\na stiff neck\njaw and neck tenderness from swollen lymph nodes\ntonsils that appear red and swollen\ntonsils that have white or yellow spots")
    #Medication
    if payload == 'medication_tonsil':
        if age in range(1,5) and weight in range(13,15):
            bot.send_text_message(sender_id,"Paracetamol 125mg/5ml suspension\ndosage:2ml, 5ml, 6ml every 4 hours as neededs")
        if age in range(6,12) and weight in range(16,20):
            bot.send_text_message(sender_id,"Paracetamol 250mg/5ml suspension\ndosage:5ml, 7.5ml, 9ml, 10ml every 4 hours as needed")     
        if age in range(13,15) and weight in range(17,25):
            bot.send_text_message(sender_id,"Paracetamol 250mg tablet\ndosage:1 tablet every 4 hours as needed")     
        if age in range(15,20) or int(age) > 20 and weight in range(26,30) or int(weight) > 30:
            bot.send_text_message(sender_id,"Paracetamol 500mg tablet\ndosage:1 tablet every 4 hours as needed")   
        if age in range(1,10) and weight in range(9,15):
            bot.send_text_message(sender_id,"Cefuroxime 125mg/5ml suspension\ndosage:2.5ml, 3ml, 4ml, 5ml, 6ml, 7.5ml 2x a day for 7 days")   
        if age in range(11,15) and weight in range(16,19):
            bot.send_text_message(sender_id,"Cefuroxime 250mg/5ml suspension\ndosage:9ml, 9.5ml, 10ml, 10.5ml 2x a day for 7 days")   
        if age in range(14,17) and weight in range(20,27):
            bot.send_text_message(sender_id,"Cefuroxime 250mg tablet\ndosage:1 tablet 2x a day for 7 days")   
        if age in range(18,20) or int(age) > 20:
            bot.send_text_message(sender_id,"Cefuroxime 500mg tablet\ntablet 2x a day for 7 days") 
    #End Tonsil
    #UTI Remedies, Medication, About
    remedies_uti = ["Drinking lots of water, and emptying your bladder when you need to, will help you flush harmful bacteria from your system.", "Try Unsweetened Cranberry Juice. Studies have shown that cranberries actually make it harder for the bacteria that causes UTIs to stick to the urinary tract walls.", "-Don’t “Hold It”, holding off going to the bathroom gives any bacteria that may already be in your bladder the chance to grow and multiply, potentially resulting in an infection.", "Eat garlic. A recent study showed that garlic extract may be effective in reducing the bacteria that causes UTIs.", "Some evidence shows that increasing your intake of vitamin C could protect against urinary tract infections.", "Red peppers, oranges, grapefruit and kiwifruit all contain the full recommended amount of vitamin C in just one serving .", "Probiotics are beneficial microorganisms that are consumed through food or supplements and promotes healthy balance of bacteria in your gut.", "When you have a UTI, caffeine, alcohol, spicy food, nicotine, carbonated drinks, and artificial sweeteners can irritate your bladder.", "Focus on healthy foods, such as high-fiber carbohydrates (such as oatmeal or lentil soup), that are good for your digestive health."]
    if payload=='remedies_uti':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_uti"}]
        bot.send_button_message(sender_id, random.choice(remedies_uti), buttons) 
    if payload=='send_remedies_uti':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_uti"}]
        bot.send_button_message(sender_id,  generated_remedies, buttons) 
    #About
    if payload=='about_uti':
        bot.send_text_message(sender_id,'A urinary tract infection (UTI) is an infection from microbes. These are organisms that are too small to be seen without a microscope.\nMost UTIs are caused by bacteria, but some are caused by fungi and in rare cases by viruses. UTIs are among the most common infections in humans.\nA UTI can happen anywhere in your urinary tract. Your urinary tract is made up of your kidneys, ureters, bladder, and urethra. Most UTIs only involve the urethra and bladder, in the lower tract.\nHowever, UTIs can involve the ureters and kidneys, in the upper tract. Although upper tract UTIs are more rare than lower tract UTIs, they’re also usually more severe.')
        buttons = [{"type": "postback","title": "UTI Symptoms", "payload": "send_symptoms_uti" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of UTI?", buttons)
    if payload=='send_symptoms_uti':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Symptoms of a lower tract UTI include:\nburning with urination\nincreased frequency of urination without passing much urine\nincreased urgency of urination\nbloody urine\ncloudy urine\nurine that looks like cola or tea\nurine that has a strong odor\npelvic pain in women\nrectal pain in men\nSymptoms of an upper tract UTI include:\npain and tenderness in the upper back and sides\nchills\nfever\nnausea\nvomiting")
        buttons = [{"type": "postback","title": "Cause of UTI","payload": "send_cause_uti"}]
        bot.send_button_message(sender_id, "What causes UTI?", buttons)
    if payload=='send_cause_uti':   
        bot.send_text_message(sender_id,"Anything that reduces your bladder emptying or irritates the urinary tract can lead to UTIs. There are also many factors that can put you at an increased risk of a getting a UTI. These factors include:\nage — older adults are more likely to get UTIs\nreduced mobility after surgery or prolonged bed rest\nkidney stones\na previous UTI\nurinary tract obstructions or blockages, such as an enlarged prostate, kidney stones, and certain forms of cancer\nprolonged use of urinary catheters, which may make it easier for bacteria to get into your bladder\ndiabetes, especially if poorly controlled, which may make it more likely for you to get a UTI\npregnancy\nabnormally developed urinary structures from birth\na weakened immune system")
    #Medication
    if payload == 'medication_uti':
        if age in range(0.0,0.3) and weight in range(2,6):      
            bot.send_text_message(sender_id,"Paracetamol drops\ndosage:0.25ml, 0.3ml, 0.5ml every 4 hours as needed")
        if age in range(0.4,0.6) and weight in range(7,9):      
            bot.send_text_message(sender_id,"Paracetamol drops\ndosage:0.6ml, 0.75ml, 0.9ml every 4 hours as needed")
        if age in range(0.5,0.11) and weight in range(10,12):      
            bot.send_text_message(sender_id,"Paracetamol drops\ndosage:1ml, 1.2ml, 1.5ml, 1.6ml, 2ml every 4 hours as needed")
        if age in range(1,5) and weight in range(13,15):      
            bot.send_text_message(sender_id,"Paracetamol 125mg/5ml suspension\ndosage:2ml, 5ml, 6ml every 4 hours as needed")
        if age in range(6,12) and weight in range(16,20):      
            bot.send_text_message(sender_id,"Paracetamol 250mg/5ml suspension\ndosage:5ml, 7.5ml, 9ml, 10ml every 4 hours as needed")        
        if age in range(13,15) and weight in range(17,25):      
            bot.send_text_message(sender_id,"Paracetamol 250mg tablet\ndosage:1 tablet every 4 hours as needed")        
        if age in range(15,20) or int(age) > 20 and weight in range(26,30) or int(weight) > 30:      
            bot.send_text_message(sender_id,"Paracetamol 500mg tablet\ndosage:1 tablet every 4 hours as needed")            
        if age in range(0.2,0.4) and weight in range(3,6) :      
            bot.send_text_message(sender_id,"Amoxicillin drops\ndosage:0.3ml, 0.5ml, 0.6ml 3x a day for 7 days")              
        if age in range(0.5,0.11) and weight in range(7,11) :      
            bot.send_text_message(sender_id,"Amoxicillin drops\ndosage:7.5ml, 9ml, 1ml, 1.5ml, 1.6ml, 1.9ml, 2ml 3x a day for 7 days")        
        if age in range(1,9) and weight in range(10,14) :      
            bot.send_text_message(sender_id,"Amoxicillin 125mg/5ml suspension\ndosage:2.5ml, 3.5ml, 5ml, 6ml 3x a day for 7 days")
        if age in range(10,14) and weight in range(15,20) :      
            bot.send_text_message(sender_id,"Amoxicillin 250mg/5ml suspension\ndosage:7.5ml, 9ml, 10.5ml 3x a day for 7 days")
        if age in range(15,17):      
            bot.send_text_message(sender_id,"Amoxicillin 250mg\ndosage:1 capsule 3x a day for 7 days")
        if age in range(18,20) or int(age) > 20:      
            bot.send_text_message(sender_id,"Amoxicillin 500mg capsule\ndosage: 1 capsule 3x a day for 7 days")

    #End UTI
    #Flu Remedies, Medication, About
    remedies_flu = ["Drinking water and other fluids is even more important when you have the flu.", "Water helps to keep your nose, mouth, and throat moist. This helps your body get rid of built-up mucous and phlegm.", "It’s important to rest and get more sleep when you have the flu. Sleeping can help boost your immune system.", "Drinking warm chicken or beef bone broth is a good way to help you stay hydrated. It helps to loosen and break up nose and sinus congestion.", "-Drinking broth is a good way to replenish these nutrients while you have the flu. Plus, protein is important for rebuilding immune cells.", "The mineral zinc is important for your immune system. This nutrient helps your body make germ-fighting white blood cells.", "Several herbs have natural antiviral and antibacterial properties. Star anise is a star-shaped spice from which oseltamivir was traditionally extracted.", "Sweeten herbal teas with pure honey. Honey, royal jelly, and other bee products have been found to have natural antiviral and antibacterial properties.", "According to the study, tea tree oil works best when it’s used within two hours of infection. This shows that it may help to block the flu virus from multiplying.", "In practice, you might add a few drops of tea tree oil to liquid hand soap when you wash your hands or mixed into lotion you use.", "-Using a humidifier to add humidity in your home and workplace might help reduce flu viruses in the air.", "Breathing in steam from a warm pot of water can help soothe your nose, sinuses, throat, and lungs. Steam inhalation might help to soothe a dry cough, irritated nose, and chest tightness."]
    if payload=='remedies_flu':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_flu"}]
        bot.send_button_message(sender_id, random.choice(remedies_flu), buttons) 
    if payload=='send_remedies_flu':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_flu"}]
        bot.send_button_message(sender_id, random.choice(remedies_flu), buttons) 
    #About
    if payload=='about_flu':
        bot.send_text_message(sender_id,'Influenza (the flu) is a common, infectious virus spread by infected droplets that enter another person’s body. From there, the virus takes hold and begins to develop.\nEach year, the flu spreads across the United States. Winter is the flu’s primary season, with a peak in February. But you can be infected with the flu any time of the year.\nMany strains of the flu exist. Doctors and researchers determine which strains of the virus will be most common each year. Those strains are then used to produce vaccines. A flu vaccine is one of the easiest and most effective ways to prevent a flu infection.')
        buttons = [{"type": "postback","title": "FLU Symptoms", "payload": "send_symptoms_flu" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of FLU?", buttons)
    if payload=='send_symptoms_flu':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Early symptoms of the flu:\nSymptoms of the flu appear quickly. This sudden onset of symptoms is often the flu’s first hallmark. With similar illnesses, such as a cold, it can take several days for symptoms to emerge.\nAnother common early symptom of the flu is the breadth of pain. People with the flu report feeling uncomfortable all over their body as an early symptom.\nYou may feel as if you’ve been “hit by a truck.” Getting out of bed may prove to be difficult and slow going. This feeling may be an early symptom of the flu")
        buttons = [{"type": "postback","title": "Cause of FLU","payload": "send_cause_flu"}]
        bot.send_button_message(sender_id, "What causes FLU?", buttons)
    if payload=='send_cause_flu':   
        bot.send_text_message(sender_id,"The flu is a virus that’s shared in several ways. First, you can pick up the virus from a person near you who has the flu and sneezes, coughs, or talks.\nThe virus can also live on inanimate objects for two to eight hours. If someone with the virus touched a common surface, like a door handle or a keyboard, and you touch the same surface, you could get the virus. Once you have the virus on your hand, it can enter your body by touching your mouth, eyes, or nose.\nIt’s possible to get the flu after receiving the flu shot if you come into contact with other strains of the virus. Even then, it’s likely your symptoms will be much less severe than if you hadn’t had the vaccine at all. This is because different strains of flu virus share common elements (called cross-protection), which means that the flu vaccine is able to work against them, too.")
    #Medication
    if payload == 'medication_flu':
        if age in range(0.0,0.3) and weight in range(2,6):      
            bot.send_text_message(sender_id,"Paracetamol drops\ndosage:0.25ml, 0.3ml, 0.5ml every 4 hours as needed")
        if age in range(0.4,0.6) and weight in range(7,9):      
            bot.send_text_message(sender_id,"Paracetamol drops\ndosage:0.6ml, 0.75ml, 0.9ml every 4 hours as needed")
        if age in range(0.5,0.11) and weight in range(10,12):      
            bot.send_text_message(sender_id,"Paracetamol drops\ndosage:1ml, 1.2ml, 1.5ml, 1.6ml, 2ml every 4 hours as needed")
        if age in range(1,5) and weight in range(13,15):      
            bot.send_text_message(sender_id,"Paracetamol 125mg/5ml suspension\ndosage:2ml, 5ml, 6ml every 4 hours as needed")
        if age in range(6,12) and weight in range(16,20):      
            bot.send_text_message(sender_id,"Paracetamol 250mg/5ml suspension\ndosage:5ml, 7.5ml, 9ml, 10ml every 4 hours as needed")        
        if age in range(13,15) and weight in range(17,25):      
            bot.send_text_message(sender_id,"Paracetamol 250mg tablet\ndosage:1 tablet every 4 hours as needed")  
        if age in range(0.1,0.4) and weight in range(3,6): 
            bot.send_text_message(sender_id,"Carbocisteine drops\ndosage:0.3ml, 0.5ml, 0.6ml 3x a day for 7 days")  
        if age in range(5,11) and weight in range(7,10): 
            bot.send_text_message(sender_id,"Carbocisteine drops\ndosage:0.75ml, 0.9ml, 1 ml 3x a day for 7 days") 
        if age in range(1,12) and weight in range(8,17): 
            bot.send_text_message(sender_id,"Carbocisteine suspension\ndosage:2.5ml, 5ml, 7.5ml, 10ml 3x a day for 7 days")    
        if age in range(13,15):
            bot.send_text_message(sender_id,"Carbocisteine 250mg capsule\ndosage:1 capsule 3x a day for 7 days")    
        if age in range(16,20) or int(age) >20:
            bot.send_text_message(sender_id,"Carbocisteine 500mg capsule\ndosage:1 capsule 3x a day for 7 dayss") 
        if age in range(1,12) and weight in range(2,4): 
            bot.send_text_message(sender_id,"Phenylephrine HCI drops\ndosage:0.25ml, 0.3ml, 3x a day for 5 days")
        if age in range(0.3,0.5) and weight in range(5,8): 
            bot.send_text_message(sender_id,"Phenylephrine HCI drops\ndosage:0.5ml, 0.6ml, 3x a day for 5 days")
        if age in range(0.6,0.11) and weight in range(9,11): 
            bot.send_text_message(sender_id,"Phenylephrine HCI drops\ndosage:0.7ml, 1ml 3x a day for 5 days")
        if age in range(1,2) and weight in range(5,10): 
            bot.send_text_message(sender_id,"Phenylephrine HCI suspension\ndosage:2.5ml 3x a day for 5 days" )                                  
        if age in range(3,12):
            bot.send_text_message(sender_id,"Phenylephrine HCI suspension\ndosage:5ml 3x day for 5 days")
        if age in range(12,16):
            bot.send_text_message(sender_id,"Phenylephrine HCI 250mg tablet\ndosage:1 tablet 3x a day")
        if age in range(17,20) or int(age) > 20:
            bot.send_text_message(sender_id,"Phenylephrine HCI 500mg tablet\ndosage:1 tablet 3x a days")            
        if age in range(0.1,0.4) and weight in range(2,5): 
            bot.send_text_message(sender_id,"Cefalexin Monohydrate drops\ndosage:0.25ml, 0.3ml, 0.5ml, 0.6ml 3x a day for 7 days" ) 
        if age in range(0.5,0.11) and weight in range(6,10): 
            bot.send_text_message(sender_id,"Cefalexin Monohydrate drops\ndosage:0.7ml, 0.8ml, 0.9ml, 1ml, 1.2ml, 1.3ml, 1.5ml, 2ml, 3ml 3x a day for 7 days" ) 
        if age in range(1,9) and weight in range(11.5,13.5): 
            bot.send_text_message(sender_id,"Cefalexin Monohydrate 125mg/5ml suspension\ndosage:2.5ml, 5ml, 7.5ml, 9ml, 10ml 3x a day for 7 days" ) 
        if age in range(10,12) and weight in range(14,20): 
            bot.send_text_message(sender_id,"Cefalexin Monohydrate 250mg/5ml suspension\ndosage:5ml, 7.5ml, 10ml, 10.5ml 3x a day for 7 days" ) 
        if age in range(135,16): 
            bot.send_text_message(sender_id,"Cefalexin Monohydrate 250mg capsule: 13-16y/o dosage:1 capsule 3x a day for 7 days" ) 
        if age in range(17,20) or int(age) > 20: 
            bot.send_text_message(sender_id,"Cefalexin Monohydrate 500mg capsule: 17-20y/o dosage:1 capsule 3x a day for 7 days" ) 

    #End flu
        
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
    #Medication
    if payload=='medication_adhd':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"Treatment for ADHD typically includes behavioral therapies, medication, or both")
        buttons = [{"type": "postback","title": "ADHD Medication", "payload": "send_medication_adhd2" }]
        bot.send_button_message(sender_id, "Want to know about stimulant and nonstimulant medication", buttons)
    if payload=='send_medication_adhd2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Stimulant and nonstimulant medications\nMedication is often an important part of treatment for a child with ADHD. However, it can be a difficult decision to make as a parent.\nTo make the best choice, you and your child’s doctor should work together to decide if medication is a good option.")
        buttons = [{"type": "postback","title": "ADHD Medication", "payload": "send_medication_adhd3" }]
        bot.send_button_message(sender_id, "Stimulant Medication", buttons)
    if payload=='send_medication_adhd3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Central nervous system stimulants\nThe effect improves your child’s concentration and helps them focus better.\nCommon CNS stimulants used to treat ADHD include:\namphetamine-based stimulants (Adderall, Dexedrine, Dextrostat)\ndextromethamphetamine (Desoxyn)\ndextromethylphenidate (Focalin)\nmethylphenidate (Concerta, Daytrana, Metadate, Ritalin)")
        buttons = [{"type": "postback","title": "ADHD Medication", "payload": "send_medication_adhd4" }]
        bot.send_button_message(sender_id, "Nonstimulant Medication", buttons)
    if payload=='send_medication_adhd4':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Nonstimulant medications\nYour child’s doctor may consider nonstimulant medications when stimulants haven't worked or have caused side effects that your child finds hard to handle.\nThese nonstimulant treatments include:\natomoxetine (Strattera)\nantidepressants like nortriptyline (Pamelor)\nOther nonstimulant medications can also help with ADHD. These other nonstimulants include:\nguanfacine (Intuniv) and clonidine (Kapvay)")
        buttons = [{"type": "postback","title": "ADHD Medication", "payload": "send_medication_adhd5" }]
        bot.send_button_message(sender_id, "Nonstimulant Medication", buttons)
    if payload=='send_medication_adhd5':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Nonstimulant medications\nYour child’s doctor may consider nonstimulant medications when stimulants haven't worked or have caused side effects that your child finds hard to handle.\nThese nonstimulant treatments include:\natomoxetine (Strattera)\nantidepressants like nortriptyline (Pamelor)\nOther nonstimulant medications can also help with ADHD. These other nonstimulants include:\nguanfacine (Intuniv) and clonidine (Kapvay)")
        buttons = [{"type": "postback","title": "ADHD Medication", "payload": "send_medication_adhd6" }]
        bot.send_button_message(sender_id, "Therapeutic ADHD treatments", buttons)
    if payload=='send_medication_adhd6':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Psychotherapy, Psychotherapy can be useful in getting your child to open up about their feelings of coping with ADHD.\nBehavior therapy, The goal of behavior therapy (BT) is to teach a child how to monitor their behaviors and then change those behaviors appropriately.\nSocial skills training, As with BT, the goal of social skills training is to teach the child new and more appropriate behaviors. \nSupport groups, Support groups are great for helping parents of children with ADHD connect with others who may share similar experiences and concerns.\nParenting skills training, Parenting skills training gives you tools and techniques for understanding and managing your child's behaviors.")
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
    if payload=='medication_anxiety':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"Cognitive behavioral therapy\nThe goal is to change your thinking and behaviors. This approach has been successful in creating permanent change in many people with anxiety.")
        buttons = [{"type": "postback","title": "Anxiety Medication", "payload": "send_medication_anxiety2" }]
        bot.send_button_message(sender_id, "More medication", buttons)
    if payload=='send_medication_anxiety2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Some common anti-anxiety medications are:\nalprazolam (Xanax)\nclonazepam (Klonopin)\nlorazepam (Ativan)")
        buttons = [{"type": "postback","title": "Anxiety Medication", "payload": "send_medication_anxiety3" }]
        bot.send_button_message(sender_id, "Antidepressants", buttons)
    if payload=='send_medication_anxiety3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Some common antidepressants are:\nbuspirone (Buspar)\ncitalopram (Celexa)\nescitalopram (Lexapro)\nfluoxetine (Prozac, Prozac Weekly, Sarafem)\nfluvoxamine (Luvox, Luvox CR)\nparoxetine (Paxil, Paxil CR, Pexeva)\nsertraline (Zoloft)\nvenlafaxine (Effexor XR)\ndesvenlafaxine (Pristiq)\nduloxetine (Cymbalta)")
#About  
    if payload=='about_anxiety':
        bot.send_text_message(sender_id,'It’s normal to feel anxious about moving to a new place, starting a new job, or taking a test. This type of anxiety is unpleasant, but it may motivate you to work harder and to do a better job. Ordinary anxiety is a feeling that comes and goes, but does not interfere with your everyday life.\nIn the case of an anxiety disorder, the feeling of fear may be with you all the time. It is intense and sometimes debilitating. This type of anxiety may cause you to stop doing things you enjoy.\nIn extreme cases, it may prevent you from entering an elevator, crossing the street, or even leaving your home. If left untreated, the anxiety will keep getting worse.')
        buttons = [{"type": "postback","title": "Anxiety Symptoms", "payload": "send_symptoms_anxiety" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Anxiety?", buttons)
    if payload=='send_symptoms_anxiety':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Symptoms of general anxiety include:\nincreased heart rate\n*rapid breathing\n*restlessness\n*trouble concentrating\n*difficulty falling asleep")
        buttons = [{"type": "postback","title": "Cause of Anxiety","payload": "send_cause_anxiety"}]
        bot.send_button_message(sender_id, "What causes Anxiety?", buttons)
    if payload=='send_cause_anxiety':   
        bot.send_text_message(sender_id,"Researchers are not sure of the exact cause of anxiety. But, it’s likely a combination of factors play a role. These include genetic and environmental factors, as well as brain chemistry.\nIn addition, researchers believe that the areas of the brain responsible for controlling fear may be impacted.\nCurrent research of anxiety is taking a deeper look at the parts of the brain that are involved with anxiety")
    
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
    if payload=='medication_autism':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"There are no “cures” for autism, but therapies and other treatment considerations can help people feel better or alleviate their symptoms.")
        buttons = [{"type": "postback","title": "ASD Medication", "payload": "send_medication_asd2" }]
        bot.send_button_message(sender_id, "Want to know about treatment approaches", buttons)
    if payload=='send_medication_asd2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Many treatment approaches involve therapies such as:\nbehavioral therapy\nplay therapy\noccupational therapy\nphysical therapy\nspeech therapy")
        buttons = [{"type": "postback","title": "ASD Medication", "payload": "send_medication_asd3" }]
        bot.send_button_message(sender_id, "Other therapy", buttons)
    if payload=='send_medication_asd3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Massages, weighted blankets and clothing, and meditation techniques may also induce relaxing effects. \nHowever, treatment results will vary.\nSome people on the spectrum may respond well to certain approaches, while others may not.")
        buttons = [{"type": "postback","title": "ASD Medication", "payload": "send_medication_asd4" }]
        bot.send_button_message(sender_id, "Relaxation Techniques", buttons)
    if payload=='send_medication_asd4':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Behavior problems are a common issue in people with ASD.\nCalming techniques, such as deep pressure massage or wearing weighted clothing, may soothe agitation in people with ASD.\nThis involves teaching people the difference between tense and relaxed muscles.\nThis is done in combination with deep breathing, and can help alleviate stress and agitation.")
    #About   
    if payload=='about_autism':
        bot.send_text_message(sender_id,'Autism spectrum disorder (ASD) is a broad term used to describe a group of neurodevelopmental disorders.\nThese disorders are characterized by problems with communication and social interaction.\nPeople with ASD often demonstrate restricted, repetitive, and stereotyped interests or patterns of behavior.')
        buttons = [{"type": "postback","title": "ASD Symptoms", "payload": "send_symptoms_asd" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of ASD?", buttons)
    if payload=='send_symptoms_asd':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Autism symptoms typically become clearly evident during early childhood, between 12 and 24 months of age. However, symptoms may also appear earlier or later.\nEarly symptoms may include a marked delay in language or social development.\nThe DSM-5 divides symptoms of autism into two categories: problems with communication and social interaction, and restricted or repetitive patterns of behavior or activities.\nProblems with communication and social interaction include:\nissues with communication, including difficulties sharing emotions, sharing interests, or maintaining a back-and-forth conversation\nissues with nonverbal communication, such as trouble maintaining eye contact or reading body language\ndifficulties developing and maintaining relationships\nRestricted or repetitive patterns of behavior or activities include:\nrepetitive movements, motions, or speech patterns\nrigid adherence to specific routines or behaviors\nan increase or decrease in sensitivity to specific sensory information from their surroundings, such as a negative reaction to a specific sound\nfixated interests or preoccupations.")
        buttons = [{"type": "postback","title": "Types of ASD","payload": "send_types_asd"}]
        bot.send_button_message(sender_id, "Want to know the types of ASD?", buttons)                                
    if payload=='send_types_asd':
        bot.send_text_message(sender_id,"The fifth and most recent edition of the DSM was released in 2013. The DSM-5 currently recognizes five different ASD subtypes, or specifiers. They are:")
        bot.send_text_message(sender_id,"with or without accompanying intellectual impairment.\nwith or without accompanying language impairment\nassociated with a known medical or genetic condition or environmental factor\nassociated with another neurodevelopmental, mental, or behavioral disorder\nwith catatonia")
        bot.send_text_message(sender_id,"Prior to the DSM-5, people on the autism spectrum may have been diagnosed with one of the following disorders:")
        bot.send_text_message(sender_id,"autistic disorder\nAsperger’s syndrome\npervasive development disorder-not otherwise specified (PDD-NOS)\nchildhood disintegrative disorder")
        buttons = [{"type": "postback","title": "Cause of ASD","payload": "send_cause_asd"}]
        bot.send_button_message(sender_id, "What causes ASD?", buttons)
    if payload=='send_cause_asd':   
        bot.send_text_message(sender_id,"The most current research demonstrates that there’s no single cause. Some of the suspected risk factors for autism include:\nhaving an immediate family member with autism\ngenetic mutations\nfragile X syndrome and other genetic disorders\nbeing born to older parents\nlow birth weight\nmetabolic imbalances\nexposure to heavy metals and environmental toxins\na history of viral infections\nfetal exposure to the medications valproic acid (Depakene) or thalidomide (Thalomid)")
 
    #Autsim END  
    #Bipolar
    remedies_Bipolar = ["Rhodiola, Officially known as rhodiola rosea, this herb has been used for years to help manage stress and has also demonstrated positive effects on people struggling with depression.", "Meditation, People who meditate using a supervised mindfulness-based cognitive therapy approach may see a reduction in depression that directly correlates to how many days they meditate.", "Omega-3 Fatty Acids, That's because the anti-inflammatory effects of omega-3 fatty acids could help regulate mood.", "Avoiding the 'Western' style diet that's rich in red meats, saturated fats and trans fats, and simple carbohydrates", "Eating less saturated fats and simple carbohydrates can help overall health but does not directly affect the symptoms of bipolar disorder.", "Eating a balance of protective, nutrient-dense foods. These foods include fresh fruits, vegetables, legumes, whole grains, lean meats, cold-water fish, eggs, low-fat dairy, soy products, and nuts and seeds.", "Watching caloric intake and exercising regularly to maintain a healthy weight", "Getting only moderate amounts of caffeine and not stopping caffeine use abruptly", "Avoiding high-fat meals to lower the risk for obesity", "Calming techniques such as massage therapy, yoga, acupuncture, meditation", "Adequate sleep can help stabilize your mood and reduce irritability. Tips to improve sleep include establishing a routine and creating a calm bedroom environment.", "Many people with bipolar disorder find if they stick to a daily schedule, it helps them control their mood.", "Tame stress, So take time to relax.Lying on the couch watching TV or checking your social media accounts isn't the best way to go. Instead, try something more focused, like yoga or other types of exercise. Meditation is another good choice."]
    if payload=='remedies_bipolar':
        buttons = [{"type": "postback","title": "📩Send Another","payload": "send_remedies_bipolar"}]
        bot.send_button_message(sender_id, random.choice(remedies_Bipolar), buttons)   
    if payload=='send_remedies_bipolar':   
        buttons = [ {"type": "postback", "title": "📩Send Another","payload": "send_remedies_bipolar"}]
        bot.send_button_message(sender_id, random.choice(remedies_Bipolar), buttons)                                         
    #medication
    if payload=='medication_bipolar':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"Several treatments are available that can help you manage your bipolar disorder. These include medications, counseling, and lifestyle changes. Some natural remedies may also be helpful.")
        buttons = [{"type": "postback","title": "Bipolar Medication", "payload": "send_medication_bipolar2" }]
        bot.send_button_message(sender_id, "Medications", buttons)
    if payload=='send_medication_bipolar2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Recommended medications may include:\nmood stabilizers, such as lithium (Lithobid)\nantipsychotics, such as olanzapine (Zyprexa)\nantidepressant-antipsychotics, such as fluoxetine-olanzapine (Symbyax)\nbenzodiazepines, a type of anti-anxiety medication such as alprazolam (Xanax) that may be used for short-term treatment")
        buttons = [{"type": "postback","title": "Bipolar Medication", "payload": "send_medication_bipolar3" }]
        bot.send_button_message(sender_id, "Psychotherapy", buttons)
    if payload=='send_medication_bipolar3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Cognitive behavioral therapy: You and a therapist talk about ways to manage your bipolar disorder. They will help you understand your thinking patterns.\nPsychoeducation: a kind of counseling that helps you and your loved ones understand the disorder.\nInterpersonal and social rhythm Therapy: Interpersonal and social rhythm therapy (IPSRT) focuses on regulating daily habits, such as sleeping, eating, and exercising.")
        buttons = [{"type": "postback","title": "Bipolar Medication", "payload": "send_medication_bipolar4" }]
        bot.send_button_message(sender_id, "Other treatment options", buttons)
    if payload=='send_medication_bipolar4':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Other treatment options may include:\nelectroconvulsive therapy (ECT)\nsleep medications\nsupplements\nacupuncture")

    #About   
    if payload=='about_bipolar':
        bot.send_text_message(sender_id,'Bipolar disorder is a mental illness marked by extreme shifts in mood. Symptoms can include an extremely elevated mood called mania.\nThey can also include episodes of depression. Bipolar disorder is also known as bipolar disease or manic depression.\nPeople with bipolar disorder may have trouble managing everyday life tasks at school or work, or maintaining relationships. There’s no cure, but there are many treatment options available that can help to manage the symptoms.')
        buttons = [{"type": "postback","title": "Bipolar Symptoms", "payload": "send_symptoms_bipolar" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Bipolar?", buttons)
    if payload=='send_symptoms_bipolar':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"There are three main symptoms that can occur with bipolar disorder: mania, hypomania, and depression.\nWhile experiencing mania, a person with bipolar disorder may feel an emotional high. They can feel excited, impulsive, euphoric, and full of energy.\nDuring manic episodes, they may also engage in behavior such as:\nspending sprees\nunprotected sex\ndrug use")
        buttons = [{"type": "postback","title": "Types of Bipolar","payload": "send_types_bipolar" } ]
        bot.send_button_message(sender_id, "Want to know the types of Bipolar?", buttons)                                
    if payload=='send_types_bipolar':
        bot.send_text_message(sender_id,"There are three main types of bipolar disorder: bipolar I, bipolar II, and cyclothymia.")
        bot.send_text_message(sender_id,"Bipolar I is defined by the appearance of at least one manic episode. You may experience hypomanic or major depressive episodes before and after the manic episode.\nThis type of bipolar disorder affects men and women equally.")
        bot.send_text_message(sender_id,"Bipolar II\nPeople with this type of bipolar disorder experience one major depressive episode that lasts at least two weeks.\nThey also have at least one hypomanic episode that lasts about four days. This type of bipolar disorder is thought to be more common in women.")
        bot.send_text_message(sender_id,"People with cyclothymia have episodes of hypomania and depression. These symptoms are shorter and less severe than the mania and depression caused by bipolar I or bipolar II disorder.\nMost people with this condition only experience a month or two at a time where their moods are stable.")
        buttons = [{"type": "postback","title": "Cause of Bipolar","payload": "send_cause_bipolar"}]
        bot.send_button_message(sender_id, "What causes Bipolar?", buttons)
    if payload=='send_cause_bipolar':   
        bot.send_text_message(sender_id,"Bipolar disorder is a common mental health disorder, but it’s a bit of a mystery to doctors and researchers. It’s not yet clear what causes some people to develop the condition and not others.\nGenetics\nYour brain\nEnvironmental factors")

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
    if payload=='medication_depression':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"You may successfully manage symptoms with one form of treatment, or you may find that a combination of treatments works best.")
        buttons = [{"type": "postback","title": "Depression Medication", "payload": "send_medication_depression2" }]
        bot.send_button_message(sender_id, "Medications", buttons)
    if payload=='send_medication_depression2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Medications: Your doctor may prescribe antidepressants, antianxiety, or antipsychotic medications\nPsychotherapy: Speaking with a therapist can help you learn skills to cope with negative feelings.\nLight therapy: Exposure to doses of white light can help regulate mood and improve symptoms of depression.")
        buttons = [{"type": "postback","title": "Depression Medication", "payload": "send_medication_depression3" }]
        bot.send_button_message(sender_id, "Alternative therapies", buttons)
    if payload=='send_medication_depression3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Ask your doctor about acupuncture or meditation.\nTalk with your doctor before taking a supplement or combining a supplement with prescription medication because some supplements can react with certain medications.\nSome supplements may also worsen depression or reduce the effectiveness of medication.")

    #About   
    if payload=='about_depression':
        bot.send_text_message(sender_id,'Depression is classified as a mood disorder. It may be described as feelings of sadness, loss, or anger that interfere with a person’s everyday activities.\nPeople experience depression in different ways. It may interfere with your daily work, resulting in lost time and lower productivity. \nIt also can influence relationships and some chronic health conditions.')
        buttons = [{"type": "postback","title": "Depression Symptoms", "payload": "send_symptoms_depression" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Depression?", buttons)
    if payload=='send_symptoms_depression':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Depression can be more than a constant state of sadness or feeling “blue.”\nMajor depression can cause a variety of symptoms. Some affect your mood, and others affect your body. Symptoms may also be ongoing or come and go.\nDepression can affect men, women, and children differently.")
        buttons = [{"type": "postback","title": "Cause of Depression","payload": "send_cause_depression"}]
        bot.send_button_message(sender_id, "What causes Depression?", buttons)
    if payload=='send_cause_depression':   
        bot.send_text_message(sender_id,"There are several possible causes of depression. They can range from biological to circumstantial. Common causes include:\nFamily history. You’re at a higher risk for developing depression if you have a family history of depression or another mood disorder.\nEarly childhood trauma. Some events impact the way that body reacts to fear and stressful situations.\nBrain structure. There’s a greater risk for depression if the frontal lobe of your brain is less active. However, scientists don’t know if this happens before or after the onset of depressive symptoms.\nMedical conditions. Certain conditions may put you at higher risk, such as chronic illness, insomnia, chronic pain, or attention-deficit hyperactivity disorder (ADHD).\nDrug use. A history of drug or alcohol misuse can impact your risk.")

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
    if payload=='medication_learning':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"Learning Disorder Treatments")
        buttons = [{"type": "postback","title": "Learning Disorder Medication", "payload": "send_medication_learningdisorder2" }]
        bot.send_button_message(sender_id, "Treatments", buttons)
    if payload=='send_medication_learningdisorder2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Extra help. A reading specialist, math tutor or other trained professional can teach your child techniques to improve his or her academic, organizational and study skills\nIndividualized education program (IEP). The IEP sets learning goals and determines strategies and services to support the child's learning in school.")
        buttons = [{"type": "postback","title": "Learning Disorder Medication", "payload": "send_medication_learningdisorder3" }]
        bot.send_button_message(sender_id, "Accomodations", buttons)
    if payload=='send_medication_learningdisorder3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Classroom accommodations might include more time to complete assignments or tests, being seated near the teacher to promote attention, use of computer applications that support writing, including fewer math problems in assignments, or providing audiobooks to supplement reading.")
        buttons = [{"type": "postback","title": "Learning Disorder", "payload": "send_medication_learningdisorder4" }]
        bot.send_button_message(sender_id, "Therapy", buttons)
    if payload=='send_medication_learningdisorder4':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Some children benefit from therapy. Occupational therapy might improve the motor skills of a child who has writing problems. A speech-language therapist can help address language skills.")
        buttons = [{"type": "postback","title": "Learning Disorder", "payload": "send_medication_learningdisorder5" }]
        bot.send_button_message(sender_id, "Medication", buttons)
    if payload=='send_medication_learningdisorder5':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Your child's doctor might recommend medication to manage depression or severe anxiety. Medications for attention-deficit/hyperactivity disorder may improve a child's ability to concentrate in school.")
    #About   
    if payload=='about_learning':
        bot.send_text_message(sender_id,'A learning disorder is an information-processing problem that prevents a person from learning a skill and using it effectively. Learning disorders generally affect people of average or above average intelligence.\nAs a result, the disorder appears as a gap between expected skills, based on age and intelligence, and academic performance.')
        buttons = [{"type": "postback","title": "Learning Disorder Symptoms", "payload": "send_symptoms_learningdisorder" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of Learning Disorder?", buttons)
    if payload=='send_symptoms_learningdisorder':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Doesn't master skills in reading, spelling, writing or math at or near expected age and grade levels\nHas difficulty understanding and following instructions\nHas trouble remembering what someone just told him or her\nLacks coordination in walking, sports or skills such as holding a pencil\nEasily loses or misplaces homework, schoolbooks or other items\nHas difficulty understanding the concept of time\nResists doing homework or activities that involve reading, writing or math, or consistently can't complete homework assignments without significant help\nActs out or shows defiance, hostility or excessive emotional reactions at school or while doing academic activities, such as homework or reading")
        buttons = [
                            {
                            "type": "postback",
                            "title": "Types of Learning Disorder",
                            "payload": "send_types_learningdisoder"
                            }
                            ]
        bot.send_button_message(sender_id, "Want to know the types of Learning Disorder?", buttons)                                
    if payload=='send_types_learningdisoder':
        bot.send_text_message(sender_id,"There are three common types of Learning Disorder such as:")
        bot.send_text_message(sender_id,"Reading Disorder")
        bot.send_text_message(sender_id,"Disorder of Written Expression")
        bot.send_text_message(sender_id,"Math Disorder")
        buttons = [{"type": "postback","title": "Cause of Learning Disorder","payload": "send_cause_learningdisorder"}]
        bot.send_button_message(sender_id, "What causes Learning Disorder?", buttons)
    if payload=='send_cause_learningdisorder':   
        bot.send_text_message(sender_id,"Factors that might influence the development of learning disorders include:\nFamily history and genetics. A family history of learning disorders increases the risk of a child developing a disorder.\nPrenatal and neonatal risks. Poor growth in the uterus (severe intrauterine growth restriction), exposure to alcohol or drugs before being born, premature birth, and very low birthweight have been linked with learning disorders.\nPsychological trauma. Psychological trauma or abuse in early childhood may affect brain development and increase the risk of learning disorders.\nPhysical trauma. Head injuries or nervous system infections might play a role in the development of learning disorders.\nEnvironmental exposure. Exposure to high levels of toxins, such as lead, has been linked to an increased risk of learning disorders.")

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
    if payload=='medication_odd':                                                                                                                                                                                                                                 
        bot.send_text_message(sender_id,"Early treatment is essential for people with ODD. Teens and adults with untreated ODD have increased risk for depression and substance abuse.")
        buttons = [{"type": "postback","title": "ODD Medication", "payload": "send_medication_odd2" }]
        bot.send_button_message(sender_id, "Individual cognitive behavioral therapy", buttons)
    if payload=='send_medication_odd2':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"A psychologist will work with the child to improve:\nanger management skills\ncommunication skills\nimpulse control\nproblem-solving skills")
        buttons = [{"type": "postback","title": "ODD Medication", "payload": "send_medication_odd3" }]
        bot.send_button_message(sender_id, "Other therapy", buttons)
    if payload=='send_medication_odd3':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"Family therapy: A psychologist will work with the whole family to make changes.\nParent-child interaction therapy (PCIT): Therapists will coach the parents as they interact with their children.\nPeer groups: The child can learn how to improve their social skills and relationships with other children.\nMedications: These can help treat causes of ODD, such as depression or ADHD. However, there is no specific medication to treat ODD itself.")
    #end odd3
    #About   
    if payload=='about_odd':
        bot.send_text_message(sender_id,'Even the most mild-mannered children have occasional outbursts of frustration and disobedience.\nBut a persistent pattern of anger, defiance, and vindictiveness against authority figures could be a sign of oppositional defiant disorder (ODD).\nODD is a behavioral disorder that results in defiance and anger against authority. It can affect a person’s work, school, and social life.\nODD affects between 1 and 16 percent of school age children. It’s more common in boys than girls.\nMany children start to show symptoms of ODD between the ages of 6 and 8 years. ODD also occurs in adults. Adults with ODD who were not diagnosed as children often go undiagnosed.')
        buttons = [{"type": "postback","title": "ODD Symptoms", "payload": "send_symptoms_odd" }]
        bot.send_button_message(sender_id, "Do you want to know what is the symptoms of ODD?", buttons)
    if payload=='send_symptoms_odd':                                                                                                                                                                                                                                   
        bot.send_text_message(sender_id,"ODD most commonly affects children and adolescents. Symptoms of ODD include:\nfrequent temper tantrums or episodes of anger\nrefusal to comply with adult requests\nexcessive arguing with adults and authority figures\nalways questioning or actively disregarding rules\nbehavior intended to upset, annoy, or anger others, especially authority figures\nblaming others for their own mistakes or misbehaviors\nbeing easily annoyed\nvindictiveness")
        buttons = [{"type": "postback","title": "Cause of ODD","payload": "send_cause_odd"}]
        bot.send_button_message(sender_id, "What causes ODD?", buttons)
    if payload=='send_cause_odd':   
        bot.send_text_message(sender_id,"There is no proven cause of ODD, but there are theories that can help identify potential causes. It’s thought a combination of environmental, biological, and psychological factors cause ODD. For example, it’s more common in families with a history of attention deficit hyperactivity disorder (ADHD).\nOne theory suggests ODD can begin to develop when children are toddlers, because children and adolescents with ODD show behaviors fairly typical of toddlers. This theory also suggests that the child or adolescent is struggling to become independent from parental or authority figures they were emotionally attached to.\nIt’s also possible that ODD develops as a result of learned behaviors, reflecting negative reinforcement methods some authority figures and parents use. This is especially true if the child uses bad behavior to get attention. In other cases, the child could adopt negative behaviors from a parent.\nOther possible causes include:\ncertain personality traits, like being strong-willed\nlack of positive attachment to a parent\nsignificant stress or unpredictability in the home or daily life")

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
            bot.send_text_message(sender_id, "{} I'm DrPedia, your own pediatric companion.".format(greet))
            bot.send_text_message(sender_id, "My main responsibility is to assist you with catering pediatric concern through our symptom checker.")
            bot.send_text_message(sender_id, "For that you'll have to answer some few questions.")
            bot.send_text_message(sender_id, "And of course, what ever you tell me will remain carefully between us!.")
            oneqrbtn = [{"content_type":"text","title":"Nice meeting you 🤗","payload":'pmyou'}]
            bot.send_quick_replies_message(sender_id, 'Are you glad to meet me {}?'.format(first_name(sender_id)), oneqrbtn) 
        else:
            if terms == 'Yes':
                bot.send_text_message(sender_id, "Hi {} welcome back!".format(first_name(sender_id)))
                quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
                bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(first_name(sender_id)), quick_replies)
            elif terms == 'No':
              greet_disclaimer(sender_id)

    #Persistent Menu Buttons        
    if payload=='start_over':
        if terms == "Yes":
            quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
            bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(first_name(sender_id)), quick_replies)
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
                                "title": "Like DrPedia",
                                "payload": "pm_like"
                            },
                            {
                                "type": "postback",
                                "title": "Share DrPedia",
                                "payload": "pm_share"
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
    
#Greetings, persisten menu, get started button
init_bot()
if __name__ == "__main__":
    app.run()
