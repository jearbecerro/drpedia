#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import os
import sys
import json

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)

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
                buttons = [
                                 {
                                "type": "postback",
                                "title": "Inquire",
                                "payload": "Inquire"
                                },
                                {
                                "type":"postback",
                                "title":"Contact Us",
                                "payload":"Contact Us"
                                }
                             ]
                
                
                    
                if message['message'].get('text')=='Details':
                        send_Details(sender_id)
                        send_gen_template(sender_id,'Ratsada Building Works and Renovation','https://raw.githubusercontent.com/clvrjc/repombot/master/static/visit.png','Visit Ratsada','https://www.facebook.com/Ratsada-Building-Construction-and-Renovation-2156085714682330/',buttons)
                        
                if message['message'].get('text')=='Location':
                        send_message(sender_id, 'We are located in Rosewood Arcade, Villa Kananga, Butuan City, Agusan del Norte.')
                        send_gen_template(sender_id,'Ratsada Building Works and Renovation','https://raw.githubusercontent.com/clvrjc/repombot/master/static/visit.png','Visit Ratsada','https://www.facebook.com/Ratsada-Building-Construction-and-Renovation-2156085714682330/',buttons)
                if message['message'].get('text')=='Menu':
                        send_gen_template(sender_id,'Ratsada Building Works and Renovation','https://raw.githubusercontent.com/clvrjc/repombot/master/static/visit.png','Visit Ratsada','https://www.facebook.com/Ratsada-Building-Construction-and-Renovation-2156085714682330/',buttons)
            elif message.get("postback"):  # user clicked/tapped "postback" button in earlier message
                received_postback(message)
                    
    return "Message Processed"

def send_gen_template(sender_id,title,image_url,sub,url,buttons):
    elements = [
                         {
                          "title":title,
                          "image_url":image_url,
                          "subtitle":sub,
                          "default_action": {
                            "type": "web_url",
                            "url": url,
                            "webview_height_ratio": "COMPACT"
                          },
                             "buttons":buttons
                        }
                      ]
    bot.send_generic_message(sender_id, elements)

def send_image(sender_id, image_url):
     #image_url = 'https://raw.githubusercontent.com/clvrjc/repombot/master/static/rtsada.png'
     bot.send_image_url(sender_id, image_url)
    

def button_for(title,payloadname):
     buttons = [
                                 {
                                "type": "postback",
                                "title": title,
                                "payload": payloadname
                                }
                             ]
     return buttons   

def back_button(sender_id,text,btn_name,payname):
    send_button(sender_id,text,button_for(btn_name,payname))
    
def received_postback(event):
    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    image_url = 'https://raw.githubusercontent.com/clvrjc/repombot/master/static/'
    
    payload = event["postback"]["payload"]
    if payload == "Inquire":
       send_Services(sender_id)
    
    elif payload == "Building Works":
       send_BW(sender_id)
       back_button(sender_id,'Back to Menu','Menu','backmenu')
    #inside Building Works
    elif payload == "Interior Design":
       send_gen_template(sender_id,'Interior Design',image_url+'Interior.png','See More Interior Design','https://www.google.com/search?sa=X&rlz=1C1VFKB_en__717__717&q=interior+design&tbm=isch&source=lnms&ved=2ahUKEwj-8vDOwNLiAhVSA4gKHUbRAEEQsAR6BAgGEAE&biw=1920&bih=888',button_for('Send Sample','sendinterior'))
    elif payload == "sendinterior":
       send_image(sender_id, image_url+'intdesign1.jpg')
       send_image(sender_id, image_url+'intdesign2.jpg')
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backbw')
    elif payload == "Roof Works":
       send_gen_template(sender_id,'Roof Works',image_url+'roofworks.jpg','See More Roof Works','https://www.google.com/search?q=Roof+Design&tbm=isch&tbs=rimg:CS8l4pQjSYwuIjixZ6fSpKWJNwBc0Q36SI8bythRBXqo8nb7BYmSw9y4pekou07uF0BifdtIKWU7azb0WJe6UyT8QCoSCbFnp9KkpYk3EbZoaw3mMgzhKhIJAFzRDfpIjxsRSgAxIh07FGwqEgnK2FEFeqjydhHBo0Hn-QGTbCoSCfsFiZLD3LilEQ9TA4pXtEybKhIJ6Si7Tu4XQGIR8NiWQ2ZeUmMqEgl920gpZTtrNhEAsZypfUpuKSoSCfRYl7pTJPxAESnrHpJWSbVr&tbo=u&sa=X&ved=2ahUKEwiAj7WmxtLiAhUQhbwKHc8NClcQ9C96BAgBEBg&biw=1920&bih=888&dpr=1',button_for('Send Sample','sendroof'))
       send_button(sender_id,"Go Back <-",button_for('Back <-','backbw'))
    elif payload == "sendroof":
       send_image(sender_id, image_url+'roofdesign1.jpg')
       send_image(sender_id, image_url+'roofdesign2.jpg')
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backbw')
    elif payload == "Electrical Works":
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backbw')
    elif payload == "backbw":
       send_BW(sender_id)
       back_button(sender_id,'Back to Menu','Menu','backmenu')
       
    elif payload == "Aluminum/Glass Works":
       send_AGW(sender_id)
       back_button(sender_id,'Back to Menu','Menu','backmenu')
    #inside Aluminum/Glass Works
    elif payload == "Window Screen":
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backagw')
    elif payload == "Screen Door":
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backagw')
    elif payload == "Glass Works":
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backagw')
    elif payload == "backagw":
       send_AGW(sender_id)
       back_button(sender_id,'Back to Menu','Menu','backmenu')
        
    elif payload == "Steel Fabrication":
       send_SF(sender_id)
       back_button(sender_id,'Back to Menu','Menu','backmenu')
    #inside Steel Fabrication Works
    elif payload == "Window Grill":
       send_gen_template(sender_id,'Window Grill',image_url+'windowgrill.jpg','See More Window Grill Designs','https://www.google.com/search?biw=1920&bih=888&tbm=isch&sa=1&ei=x9P3XJG2A9Xr-Qau3qOIDQ&q=window+grill+design&oq=window+grill&gs_l=img.1.0.0i67j0l2j0i67j0l3j0i67j0l2.84907.86973..89027...0.0..0.148.1637.0j12......0....1..gws-wiz-img.BFoq1Mo5_V8#imgrc=_',button_for('Send Sample','sendwindowgrill'))
    elif payload == "sendwindowgrill":
       send_image(sender_id, image_url+'windowgrill1.jpg')
       send_image(sender_id, image_url+'windowgrill2.jpg')
       send_image(sender_id, image_url+'windowgrill3.jpg')
       send_image(sender_id, image_url+'windowgrill4.jpg')
       send_image(sender_id, image_url+'windowgrill5.jpg')
       send_image(sender_id, image_url+'windowgrill6.jpg')
       send_image(sender_id, image_url+'windowgrill7.jpg')
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backsf')
    elif payload == "Steel Gate":
       send_gen_template(sender_id,'Steel Gate',image_url+'SteelGate.jpg','See More Steel Gate Designs','https://www.google.com/search?biw=1920&bih=888&tbm=isch&sa=1&ei=79T3XNqJKo-noASW_L_YBw&q=gate+design&oq=gate+design&gs_l=img.3..0i67l3j0l7.466367.468054..468362...0.0..0.159.1531.0j11......0....1..gws-wiz-img.0rVP6Of7AMA#imgrc=_',button_for('Send Sample','sendsteelgate'))
    elif payload == "sendsteelgate":
       send_image(sender_id, image_url+'steelgate1.jpg')
       send_image(sender_id, image_url+'steelgate2.jpg')
       send_image(sender_id, image_url+'steelgate3.jpg')
       send_image(sender_id, image_url+'steelgate4.jpg')
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backsf')
    elif payload == "Steel Wall":
       send_image(sender_id, image_url+'rtsada.png')
       send_just(sender_id)
       back_button(sender_id,'Go Back','Back','backsf')
    elif payload == "backsf":
       send_SF(sender_id)
       back_button(sender_id,'Back to Menu','Menu','backmenu')
        
    elif payload == "backmenu":
       buttons = [
                                 {
                                "type": "postback",
                                "title": "Inquire",
                                "payload": "Inquire"
                                },
                                {
                                "type":"postback",
                                "title":"Contact Us",
                                "payload":"Contact Us"
                                }
                             ]
       send_gen_template(sender_id,'Ratsada Building Works and Renovation','https://raw.githubusercontent.com/clvrjc/repombot/master/static/visit.png','Visit Ratsada','https://www.facebook.com/Ratsada-Building-Construction-and-Renovation-2156085714682330/',buttons)
        
    elif payload == "Contact Us":
       send_message(sender_id, 'You can visit in our office \n@Rosewood Arcade, Villa Kananga, Butuan City, Agusan del Norte.')
       send_message(sender_id, 'You may call us in this number: ')
       send_message(sender_id, '09101064727')
    
        
def send_just(sender_id):
    send_message(sender_id, 'Just Call Us For More Details')
    send_message(sender_id, '09101064727')
    send_message(sender_id, 'Kindly send us your details:\nSite Location:\nContact Number:')
    
def send_SF(sender_id):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Window Grill",
                        "payload": "Window Grill"
                        },
                        {
                        "type":"postback",
                        "title":"Steel Gate",
                        "payload":"Steel Gate"
                        },
                        {
                        "type":"postback",
                        "title":"Steel Wall",
                        "payload":"Steel Wall"
                        }
                        ]
    
    send_button(sender_id,"Please Specify if not in the list.\nSteel Fabrication:",buttons)

    
def send_AGW(sender_id):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Window Screen",
                        "payload": "Window Screen"
                        },
                        {
                        "type":"postback",
                        "title":"Screen Door",
                        "payload":"Screen Door"
                        },
                        {
                        "type":"postback",
                        "title":"Glass Works",
                        "payload":"Glass Works"
                        }
                        ]

    send_button(sender_id,"Please Specify if not in the list.\nAluminum/Glass Works:",buttons)    

    
def send_BW(sender_id):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Interior Design",
                        "payload": "Interior Design"
                        },
                        {
                        "type":"postback",
                        "title":"Roof Works",
                        "payload":"Roof Works"
                        },
                        {
                        "type":"postback",
                        "title":"Electrical Works",
                        "payload":"Electrical Works"
                        }
                        ]

    send_button(sender_id,"Please Specify if not in the list.\nBuilding Works:",buttons)

    
    
def send_Ask(sender_id):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Inquire",
                        "payload": "Inquire"
                        },
                        {
                        "type":"postback",
                        "title":"Contact Us",
                        "payload":"Contact Us"
                        }
                        ]

    send_button(sender_id,"How may I help you?",buttons)
    
def send_Services(sender_id):
    buttons = [
                        {
                        "type": "postback",
                        "title": "Building Works",
                        "payload": "Building Works"
                        },
                        {
                        "type":"postback",
                        "title":"Aluminum/Glass Works",
                        "payload":"Aluminum/Glass Works"
                        },
                        {
                        "type":"postback",
                        "title":"Steel Fabrication",
                        "payload":"Steel Fabrication"
                        }
        
                        ]

    send_button(sender_id,"Our services offered are: ",buttons)

def send_Details(sender_id):
    About = "Ratsada Construction, is a license building contractor in the purpose of rendering products and services. The company offers full-scale services from General Contracting through Design Build. In addition, Project Management and Owner Representative services are available." 
    About2 = "If you are considering a new building or renovations to an existing building, Ratsada Construction has the unique ability to personalize that project and make the entire experience rewarding from every aspect.\nOur expertise at maintaining a cost effective approach is unique in the construction field. They strive at providing a complete and composite overview of the work prescribed."
    send_message(sender_id, About)
    send_message(sender_id, About2) 
    
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

