from datetime import datetime
import os
from messnger_syntax.bot import Bot
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
bot = Bot (ACCESS_TOKEN)

import sqlite3
from sqlite3 import Error
 
def con():
    try:
        con = sqlite3.connect('drpedia.db')
        return con
    except Error:
        print(Error)
con()
cur = con.cursor()
#Happen once after debugging
def create_table(con, qry):
    cur.execute("DROP TABLE users;")#for debugging
    con.commit()
    cur.execute(")
    con.commit()
    
create = "CREATE TABLE users(id integer PRIMARY KEY, sender_id text, last_seen text, first_name text, last_name text, last_message_ask text, last_message_answer text);"
create_table(con(),create)

def user_exists(sender_id):
    cur.execute("Select sender_id from users where sender_id = {}".format(sender_id))
    user = cur.fetchone()
    if user is None:
        user_fb = bot.get_user_info(sender_id)#all information
        create_user(sender_id, user_fb)
        return False
    return True
    
def create_user(sender_id, user_fb):
    timestamp = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    qry="insert into users (sender_id, first_name) values('Becerro','Aljie Rose');"
    cur.execute(qry)
    db.commit() 
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
    


''''
qry="insert into users (last_name, first_name) values('Becerro','Aljie Rose');"
cur=db.cursor()
cur.execute(qry)
db.commit() 

sql="SELECT first_name from users where last_name = 'Becerro';"
cur.execute(sql)
record=cur.fetchone()
print (record)
db.close()'''
