from datetime import datetime
import os
from messnger_syntax.bot import Bot
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
bot = Bot (ACCESS_TOKEN)

def find_user_id(users, user_object_id):
    # Convert from string to ObjectId:
    return users.find_one({'_id': ObjectId(user_object_id)})

# Has to use user_id since user might not exist
def user_exists(users, sender_id):
    user = users.find_one({'user_id': sender_id})
    if user is None:
        user_fb = bot.get_user_info(sender_id)#all information
        create_user(users, sender_id, user_fb)
        return False
    return True

# Manual input
def create_patient(patient, sender_id, name, age, weight, relation):
    timestamp = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    patient_insert = {'user_id': sender_id, 
                    'created_at': timestamp,
                    'name': name,
                    'age':age,
                    'weight': weight,
                    'relation': relation
                    }
    patient.insert(patient_insert)

# Has to use user_id since user has not existed
def create_user(users, sender_id, user_fb):
    timestamp = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    user_insert = {'user_id': sender_id, 
                    'created_at': timestamp,
                    'last_seen': "1970-01-01 00:00:00",
                    'first_name':user_fb['first_name'],
                    'last_name':user_fb['last_name'],
                    'last_message_ask':'None',
                    'last_message_answer':'None',
                    'accept_disclaimer':'No'
                   }
    users.insert(user_insert)
 
def get_data_users(users, sender_id):
    a = users.find_one({'user_id': sender_id})
    return a

def set_terms(users, sender_id):
    users.update({"user_id": sender_id},{"$set":{"accept_disclaimer": "Yes"}})
def get_terms(users, sender_id):
    #,{'accept_disclaimer':1,'_id':0}
    a = users.find_one({'user_id': sender_id},{'accept_disclaimer':1,'_id':0})
    return a["accept_disclaimer"]

#Setter Getter for last message send by the DrPedia ---
    #set last message ask by the chatbot
def set_ask(users, sender_id, ask):
    users.update({"user_id": sender_id},{"$set":{"last_message_ask": ask}})
    #get last message ask by the chatbot
def get_ask(users, sender_id):
    a = users.find_one({'user_id': str(sender_id)},{'last_message_ask':1,'_id':0})
    return a["last_message_ask"]
#End Setter Getter last message send by the DrPedia ---

#Setter Getter for last message send by the user ---
#set last message ask by the chatbot
def set_answer(users, sender_id, answer):
    users.update({"user_id": sender_id},{"$set":{"last_message_answer": answer}})
#get last message ask by the chatbot
def get_answer(users, sender_id):
    a = users.find_one({'user_id': str(sender_id)},{'last_message_answer':1,'_id':0})
    return a["last_message_answer"]
#End Setter Getter last message send by the user ---

# Input: Facebook's sender_id
def get_user_mongo(users, sender_id):
    return users.find_one({'user_id': sender_id})

def update_last_seen(users, sender_id):
    now = datetime.now()
    timestamp = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    users.update({"user_id": sender_id},{"$set":{"last_seen": timestamp}})



