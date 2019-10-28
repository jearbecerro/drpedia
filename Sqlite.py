from datetime import datetime
import os
from messnger_syntax.bot import Bot
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
bot = Bot (ACCESS_TOKEN)

import sqlite3
from sqlite3 import Error
 
def con():
    try:
        con = sqlite3.connect('file:drpedia.db?branches=on')
        return con
    except Error:
        print(Error)
con = con()
cur = con.cursor()

#Happen once after debugging
def create_table(con, qry):
    cur.execute("DROP TABLE IF EXISTS users ;")
    con.commit()
    cur.execute(qry)
    con.commit()
    print("Created")
                
#create = "CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY, sender_id text, last_seen text, first_name text, last_name text, last_message_ask text, last_message_answer text, created_at text, accept_disclaimer text);"
#create_table(con,create)

def user_exists(sender_id):
    cur.execute("Select sender_id from users where sender_id = ?;",(str(sender_id),))
    user = cur.fetchone()
    if user is None:
        user_fb = bot.get_user_info(sender_id)#all information
        create_user(sender_id, user_fb)
        return False
    return True
    
def create_user(sender_id, user_fb):
    timestamp = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
    cur.execute("insert into users (sender_id, created_at, last_seen, first_name, last_name, last_message_ask, last_message_answer, accept_disclaimer) values(?, ?, ?, ?, ?, ?, ?, ?);",(str(sender_id), str(timestamp), "1970-01-01 00:00:00", str(user_fb['first_name']), str(user_fb['last_name']), "None","None","No",))
    con.commit() 
    
def set_terms(sender_id):
    cur.execute('UPDATE users SET accept_disclaimer = ? where sender_id = ?;',('Yes',str(sender_id),))
    con.commit()
def get_terms(sender_id):
    cur.execute("SELECT accept_disclaimer from users where sender_id = ?;",(str(sender_id),))
    row = cur.fetchone()
    if row is not None: 
     result = row[0]
     return result

#Setter Getter for last message send by the DrPedia ---
    #set last message ask by the chatbot
def set_ask(sender_id, ask):
    cur.execute('UPDATE users SET last_message_ask = ? where sender_id = ?;',(ask, str(sender_id),))
    con.commit()
def get_ask(sender_id):
    cur.execute("SELECT last_message_ask from users where sender_id = ?;",(str(sender_id),))
    #result = cur.fetchone()          
    #return str(result)
    row = cur.fetchone()
    if row is not None: 
     result = row[0]
     return str(result)
#End Setter Getter last message send by the DrPedia ---
#Setter Getter for last message send by the user ---
#set last message ask by the chatbot
def set_answer(sender_id, answer):
    cur.execute('UPDATE users SET last_message_answer = ? where sender_id = ?;',(answer, str(sender_id),))
    con.commit()
#get last message ask by the chatbot
def get_answer(sender_id):
    cur.execute("SELECT last_message_answer from users where sender_id = ?;",(str(sender_id),))
    #result = cur.fetchone()     
    #return str(result)
    row = cur.fetchone()
    if row is not None: 
     result = row[0]
     return result
    else:
     return "No return value"
#End Setter Getter last message send by the user ---

def update_last_seen(sender_id):
    now = datetime.now()
    timestamp = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    cur.execute('UPDATE users SET last_seen = ? where sender_id = ?;',(str(timestamp), str(sender_id),))
    con.commit()
