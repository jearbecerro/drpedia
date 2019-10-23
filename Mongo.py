from datetime import datetime
import os
from messnger_syntax.bot import Bot
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
bot = Bot (ACCESS_TOKEN)

def find_user_id(users, user_object_id):
    # Convert from string to ObjectId:
    return users.find_one({'_id': ObjectId(user_object_id)})

# Has to use user_id since user might not exist
def user_exists(users, user_id):
    user = users.find_one({'user_id': user_id})
    if user is None:
        print user_id
        user_fb = bot.get_user_info(user_id)#all information
        create_user(users, user_id, user_fb)
        return False
    return True


def create_patient(patient, user_id,name, age, weight, relation):
    timestamp = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    patient_insert = {'user_id': user_id, 
                    'created_at': timestamp,
                    'name': name,
                    'age':age,
                    'weight': weight,
                    'relation': relation
                    }
                }
    patient.insert(patient_insert)

# Has to use user_id since user has not existed
def create_user(users, user_id, user_fb):
    timestamp = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    user_insert = {'user_id': user_id, 
                    'created_at': timestamp,
                    'last_seen': "1970-01-01 00:00:00",
                    'first_name':user_fb['first_name'],
                    'last_name':user_fb['last_name'],
                    'gender': user_fb['gender'],
                    'timezone':user_fb['timezone']
                    }
                }
    users.insert(user_insert)

# Input: Facebook's user_id
def get_user_mongo(users, user_id):
    return users.find_one({'user_id': user_id})


def update_last_seen(users, user):
    now = datetime.now()
    timestamp = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    users.update({"user_id": user['user_id']},{"$set":{"last_seen": timestamp}})

def update_first_time(users, user, first_time_name):
    users.update({'_id': user['_id']},{"$set":{"first_time_using." + first_time_name: 0}})

def first_time_using(users, user, first_time_name):
    tried = users.find_one({'_id': user['_id']},{"first_time_using." + first_time_name: 1})['first_time_using']
    if tried:
        return False
    else:
        update_first_time(users, user, first_time_name)
        return True


