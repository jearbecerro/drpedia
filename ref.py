#Python libraries that we need to import for our bo
import random
from flask import Flask, request
from pymessenger.bot import Bot
import os
import sys
import pandas as pd
import json

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)

SymptomTable 	= pd.read_csv('Symptoms.csv')
SymptomTable	= SymptomTable.set_index('illness')
all_illnesses 	= SymptomTable.index
all_symptoms 	= SymptomTable.columns

with open('Medicines.json') as medicine_file:
    Medicine = json.load(medicine_file)
    
normalizer 	= 0.2 / (len(all_illnesses)-1)
Prob = pd.Series(normalizer,index=all_illnesses)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
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
                    send_message(sender_id,'Hi!\nIm DrPedia')
                    if message['message'].get('text')=='diagnose':
                        #send_message(sender_id, 'Im DrCare\nI will ask some questions for diagnosting')
                        send_message(sender_id,'Hi!\nIm DrPedia')
                        send_message(sender_id,'I will help you diagnose your childs health.')
                        send_diagnose(sender_id,'I will ask some questions for diagnostic. Just Tap Diagnose.')
               
                if message.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    received_postback(message)
                    
    return "Message Processed"

def send_diagnose(sender_id,text):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Diagnose",
                        "payload": "diagnose"
                        }
        
                        ]

    send_button(sender_id,text,buttons)
    
def send_YN(sender_id,text,symptom):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Yes",
                        "payload": "Yes"+symptom
                        },
                        {
                        "type":"postback",
                        "title":"No",
                        "payload":"No"+symptom
                        }
                        ]

    send_button(sender_id,text,buttons)    

  
def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    image_url = 'https://raw.githubusercontent.com/clvrjc/repombot/master/static/'
    
    payload = event["postback"]["payload"]
    if payload == 'diagnose':
        for symptom in all_symptoms:
            # If no answer, then skip to next symptom.
            #yn = input("Is your child experiencing unusual %s? " % symptom)
            send_YN(sender_id,'Is your child experiencing unusual '+symptom,symptom)
            if payload == 'Yes'+symptom:
                has_symptom = True
            elif payload == 'No'+symptom:
                has_symptom = False
            else: 
                continue

            likelihood 	= SymptomTable[symptom]
            fValid 		= likelihood.notnull()
            if has_symptom:
                Prob[fValid] *= likelihood
            else:
                Prob[fValid] *= (1-likelihood)

            # Remember to normalize the distribution
            Prob /= Prob.sum()

            # Show the most probable illnesses
            #print( "\nI believe these illnesses are consistent with your symptoms:" )
        send_message(sender_id, "I believe these illnesses are consistent with your symptoms:")
        Prob = Prob.sort_values(ascending=False)
        for illness in Prob.index:
            pct = 100 * Prob.loc[illness].round(4)
            if pct > 10:
                send_message(sender_id,pct +"% "+illness)
                #print( "%02d %% \t %s" % (pct,illness) 
                
        diagnosis = Prob.idxmax()
        #print( "\nI recommend this medication for %s:" % diagnosis )
        send_message(sender_id, "I recommend this medication for: "+ diagnosis)
        for med, pill in Medicine.items():
            if diagnosis in pill:
                send_message(sender_id,med)
                #print(med)
                
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def send_random():
    sample_responses = ["Okay", "Thank You."]
    # return selected item to the user
    return random.choice(sample_responses)

def send_button(sender_id,text,buttons):
    bot.send_button_message(sender_id,text, buttons)
    return "success"

#uses PyMessenger to send response to user
def send_message(sender_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(sender_id, response)
    return "success"

if __name__ == "__main__":
    app.run()

