from datetime import datetime
import os
from messnger_syntax.bot import Bot
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
bot = Bot (ACCESS_TOKEN)


def get_data_users(users, sender_id):
    a = users.find_one({'user_id': sender_id})
    if a != None:
        return a
    return None

def set_terms(users, sender_id):
    users.update({"user_id": sender_id},{"$set":{"accept_disclaimer": "Yes"}})
    users.close()
def set_ask(users, sender_id, ask):
    users.update({"user_id": sender_id},{"$set":{"last_message_ask": ask}})
    users.close()
    #get last message ask by the chatbot
def set_answer(users, sender_id, answer):
    users.update({"user_id": sender_id},{"$set":{"last_message_answer": answer}})
    users.close()
    
def find_user_id(users, user_object_id):
    # Convert from string to ObjectId:
    return users.find_one({'_id': ObjectId(user_object_id)})
    

# Has to use user_id since user has not existed
def user_exists(users, sender_id):
    user = users.find_one({'user_id': sender_id})
    if user is None:
        user_fb = bot.get_user_info(sender_id)#all information
        create_user(users, sender_id, user_fb)
        return False
    return True

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
    users.close()

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
    patient.close()

# Input: Facebook's sender_id
def get_user_mongo(users, sender_id):
    return users.find_one({'user_id': sender_id})

def update_last_seen(users, sender_id):
    now = datetime.now()
    timestamp = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    users.update({"user_id": sender_id},{"$set":{"last_seen": timestamp}})
    users.close()



