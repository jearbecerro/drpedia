#Libraries to be import START
import random
from flask import Flask, request
from messnger_syntax.bot import Bot
import os
import json
import pymongo
from pymongo import MongoClient
import Mongo#import Mongo.py
from NLU import nlp
from collections import Counter #install collections
#Libraries to be import END

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
MONGO_TOKEN = os.environ['MONGO_DB']

bot = Bot (ACCESS_TOKEN)
cluster = MongoClient(MONGO_TOKEN)
db = cluster["DrPedia"]
users = db["users"]
patient = db["patient"]

with open("illness.json") as file:
	data = json.load(file)
		
image_url = 'https://raw.githubusercontent.com/clvrjc2/drpedia/master/images/'
GREETING_RESPONSES = ["Hi", "Hey", "Hello there", "Hello", "Hi there"]

'''
with open("remedies.json") as file:
	remedies = json.load(file)
for ra in remedies["medication"]:#get all data in the 'illness' 
	name = ra["name"]
	if name.lower() == 'Flu':
		flu_remedies = ra["remedies"]
		flu_about = ra["about"]
	if name.lower() == 'UTI':
		uti_remedies = ra["remedies"]
	if name.lower() == 'Dengue':
		dengue_remedies = ra["remedies"]
	if name.lower() == 'Gastro':
		gastro_remedies = ra["remedies"]
	if name.lower() == 'Tonsil':
		tonsill_remedies = ra["remedies"]
'''	
flu_about = ["Influenza is a serious virus that leads to many illnesses each year, you don’t have to be young or have a compromised immune system to get gravely ill from the infection and healthy people can get sick from the flu and spread it to friends and family."]

uti_about = ["A urinary tract infection (UTI) is an infection from microbes. Most UTIs only involve the urethra and bladder, in the lower tract. However, UTIs can involve the ureters and kidneys, in the upper tract."]
       
dengue_about = ["Dengue fever is a disease spread by the Aedes aegypti mosquito and is caused by one of four dengue viruses. Dengue fever is transmitted via the bite of a mosquito harboring the dengue virus."]

gastro_about = ["Gastroenteritis is an inflammation of your stomach and intestines caused by one of any number of viruses. This highly contagious illness spreads through close contact with people who are infected or through contaminated food or water."]
   
tonsill_about = ["When tonsils become infected, the condition is called tonsillitis. It’s most often diagnosed in children from preschool age through their mid-teens."]
 
commoncold_about = ["Cold symptoms typically take a few days to appear. Colds rarely cause additional health conditions or problems."]
                            
typhoidfever_about = ["Typhoid fever is a serious bacterial infection that easily spreads through contaminated water and food. Along with high fever, it can cause abdominal pains headache, and loss of appetite."]
 
bronchitis_about = ["Your bronchial tubes deliver air from your trachea (windpipe) into your lungs. When these tubes become inflamed, mucus can build up.", "This condition is called bronchitis, and it causes symptoms that can include coughing, shortness of breath, and low fever."]
               
pneumonia_about = ["Pneumonia is an infection in one or both lungs. Bacteria, viruses, and fungi cause it."]

diarrhea_about = ["Diarrhea is characterized by loose, watery stools or a frequent need to have a bowel movement. You might experience diarrhea as a result of a viral or bacterial infection."]
 
fever_about = ["Fever is also known as hyperthermia, pyrexia, or elevated temperature. It describes a body temperature that’s higher than normal."]
 
cough_about = ["Coughing is a common reflex action that clears your throat of mucus or foreign irritants. Coughing is a symptom of many illnesses and conditions."]

muscleaches_about = ["Muscle aches (myalgia) are extremely common. Because there’s muscle tissue in nearly all parts of the body, this type of pain can be felt practically anywhere."]
        
headache_about = ["A headache is a very common condition that causes pain and discomfort in the head, scalp, or neck. Headaches can sometimes be mild, but in many cases, they can cause severe pain that makes it difficult to concentrate at work and perform other daily activities."]
  
fatigue_about = ["Fatigue is a term used to describe an overall feeling of tiredness or lack of energy. Fatigue is a common symptom of many medical conditions that range in severity from mild to serious."]
                                            
burningurin_about = ["Painful urination is a broad term that describes discomfort during urination. This pain may originate in the bladder, urethra, or perineum."]
        
lossappetite_about = ["A decreased appetite occurs when you have a reduced desire to eat. It may also be known as a poor appetite or loss of appetite."]
       
increasedfrequencyofurinationwithoutpassingmuchurine_about = ["Frequent urination describes the need to urinate more often than usual. However, there isn’t really a clear definition of “frequent” when it comes to how often you urinate. "]
 
increasedurgencyofurination_about = ["Urgent urination describes an overwhelming need to get to a restroom immediately. It may be accompanied by pain or discomfort in the bladder or urinary tract."]
               
bloodyurine_about = ["Hematuria is the medical term for blood in your urine. Several different conditions and diseases can cause hematuria."]
        
cloudyurine_about = ["If your urine is cloudy, it may mean something is amiss with your urinary tract. While cloudy urine doesn’t typically indicate a medical emergency, it can be a sign of a serious medical problem."]
        
urinehasastrongodor_about = ["You may notice that your urine occasionally has a stronger smell than it normally does. But sometimes strong or unusual smelling urine is a sign of an underlying medical problem."]
   
pelvicpain_about = ["The pelvis houses the reproductive organs. It’s located at the lower abdomen, where your abdomen meets your legs. Pelvic pain can radiate up into the lower abdomen, making it hard to differentiate from abdominal pain."]
  
rectalpain_about = ["Rectal pain can refer to any pain or discomfort in the anus, rectum, or lower portion of the gastrointestinal (GI) tract. Oftentimes, it results from a bout of muscle spasms or constipation."]
           
swollenlymphnodes_about = ["Lymph nodes are small glands that filter lymph, the clear fluid that circulates through the lymphatic system. They become swollen in response to infection and tumors."]
        
jointpain_about = ["Joint pain refers to discomfort, aches, and soreness in any of the body’s joints. Joint pain is a common complaint. Sometimes, joint pain is the result of an illness or injury."]
        
rashes_about = ["A rash is a noticeable change in the texture or color of your skin. Your skin may become scaly, bumpy, itchy, or otherwise irritated."]
        
nausea_about = ["Nausea is stomach discomfort and the sensation of wanting to vomit. Nausea can be a precursor to vomiting the contents of the stomach."]
        
vomiting_about = ["Vomiting, or throwing up, is a forceful discharge of stomach contents. Vomiting itself is not a condition. It’s a symptom of other conditions."]
        
bleedingnosegums_about = ["Nosebleeds are common. They may be scary, but they rarely indicate a serious medical problem. There are many causes of nosebleeds. If you have frequent nosebleeds, you could have a more serious problem."]
        
bruisingontheskin_about = ["A bruise, or contusion, appears on the skin due to trauma. Some bruises appear with very little pain, and you might not notice them."]
        
dia_about = ["Diarrhea is characterized by loose, watery stools or a frequent need to have a bowel movement. You might experience diarrhea as a result of a viral or bacterial infection."]
        
clammyskin_about = ["Clammy skin refers to wet or sweaty skin. Changes in your body from physical exertion or extreme heat can trigger your sweat glands and cause your skin to become clammy."]
        
abdominalpain_about = ["Abdominal pain is pain that occurs between the chest and pelvic regions. Inflammation or diseases that affect the organs in the abdomen can cause abdominal pain."]
        
abdominalcrapms_about = ["Abdominal pain is pain that occurs between the chest and pelvic regions. Inflammation or diseases that affect the organs in the abdomen can cause abdominal pain."]
        
sorethroat_about = ["A sore throat is pain, scratchiness or irritation of the throat that often worsens when you swallow. The most common cause of a sore throat (pharyngitis) is a viral infection, such as a cold or the flu. A sore throat caused by a virus resolves on its own."]
        
paininswallowing_about = ["Pain in the throat is one of the most common symptoms. It accounts for more than 13 million visits to doctor’s offices each year."]
                 
scrathcyvoice_about = ["Hoarseness, an abnormal change in your voice, is a common condition that’s often experienced in conjunction with a dry or scratchy throat. Hoarseness is typically caused by a viral infection in the upper respiratory tract."]
        
badbreath_about = ["Bad breath is also known as halitosis or fetor oris. Odor can come from the mouth, teeth, or as a result of an underlying health problem."]
        
chills_about = ["The term “chills” refers to a feeling of being cold without an apparent cause. You get this feeling when your muscles repeatedly expand and contract and the vessels in your skin constrict."]
        
earache_about = ["Earaches usually occur in children, but they can occur in adults as well. An earache may affect one or both ears, but the majority of the time it’s in one ear."]
        
stomachache_about = ["Abdominal or stomach pain is pain that occurs between the chest and pelvic regions. Inflammation or diseases that affect the organs in the abdomen can cause abdominal pain."]
        
redswollentonsil_about = ["Tonsils can become infected by viruses and bacteria. When they do, they swell up. Swollen tonsils are known as tonsillitis."]
        
whiteoryellowspotsintonsils_about = ["White discoloration may appear only on the tonsils or it may appear around the tonsils and throughout the mouth. In addition to the white spots, your tonsils may feel scratchy and you might find it difficult to swallow."]
        
nasalcongestion_about = ["Nasal congestion, also called a stuffy nose, is often a symptom of another health problem such as a sinus infection. It may also be caused by the common cold."]
        
sneezing_about = ["Sneezing is your body’s way of removing irritants from your nose or throat. When these membranes become irritated, it causes you to sneeze."]
        
weakness_about = ["Asthenia, also known as weakness, is the feeling of body fatigue or tiredness. Others may experience full-body weakness, which is often the result of a bacterial or viral infection such as influenza or hepatitis."]
        
feelingcold_about = ["Some people are prone to feeling cold, especially those who have chronic health problems or little body fat."]
        
backpain_about = ["Lower back pain, also called lumbago, is not a disorder. It’s a symptom of several different types of medical problems."]
        
coughwiththickyellowgreenorbloodtingedmucus_about = ["You typically don’t produce noticeable amounts of phlegm unless you are sick with a cold or have some other underlying medical issue. If you see green or yellow phlegm, it’s usually a sign that your body is fighting an infection."]
        
stabbingchestpainworsenswhencoughingorbreathing_about = ["Chest pain is one of the most common reasons that people visit the emergency room. It may feel like a sharp, stabbing pain or a dull ache."]
        
suddenonsetofchills_about = ["The term “chills” refers to a feeling of being cold without an apparent cause. You get this feeling when your muscles repeatedly expand and contract and the vessels in your skin constrict."]
        
frequenturgebowels_about = ["Frequent urge to bowel is a condtion that makes you frequently urges you to bowel which may lead to serious health condtion"]
        
loosestools_about = ["Loose stools are bowel movements that appear softer than normal. They can be watery, mushy, or shapeless."]
        
bloating_about = ["Abdominal bloating occurs when the gastrointestinal (GI) tract is filled with air or gas. Most people describe bloating as feeling full, tight, or swollen in the abdomen."]
        
cramping_about = ["Muscle cramps are sudden, involuntary contractions that occur in various muscles. These contractions are often painful and can affect different muscle groups."]
        
dehydration_about = ["Dehydration takes place when your body loses more fluid than you drink. When too much water is lost from the body, its organs, cells, and tissues fail to function as they should, which can lead to dangerous complications."]
        
wheezing_about = ["Wheezing is a high-pitched whistling sound made while you breathe. Asthma and chronic obstructive pulmonary disease (COPD) are the most common causes of wheezing."]
        
#illnesses remedies
flu_remedies = ["Call your doctor", "Let your child rest as much as needed", "Keep your child hydrated with plenty of liquids, breast milk or formula for babies; water, juice, ice pops, and cool drinks for older kids (but no caffeinated drinks)", "Relieve symptoms with: a cool-mist humidifier, saline (saltwater) nose drops, acetaminophen or ibuprofen (give according to package directions)"]
uti_remedies = ["Try cranberries. Cranberries may contain an ingredient that stops bacteria from attaching to the walls of the urinary tract. You might be able to reduce your risk with unsweetened cranberry juice, cranberry supplements, or by snacking on dried cranberries.", "Drink plenty of water. The more you drink, the more you’ll urinate. Urinating helps flush harmful bacteria from the urinary tract.", "Pee when you need to. Holding your urine or ignoring the urge to urinate can allow bacteria to multiply in your urinary tract. As a rule of thumb, always use the bathroom when you feel the urge.", "Take probiotics. Probiotics promote healthy digestion and immunity. They also may be effective in treating and preventing UTIs.", "Get more vitamin C. Increasing your intake of vitamin C may help prevent a UTI. Vitamin C strengthens the immune system and may help acidify to prevent infection."]
dengue_remedies = ["There is no medication or treatment specifically for dengue infection.", "If you believe you may be infected with dengue, you should use over-the-counter pain relievers to reduce your fever, headache, and joint pain", "Your doctor should perform a medical exam, and you should rest and drink plenty of fluids.", " If you feel worse after the first 24 hours of illness, once your fever has gone down, you should be taken to the hospital as soon as possible to check for complications"]
gastro_remedies = ["Allow your child to rest", "When your child's vomiting stops, begin to offer small amounts of an oral rehydration solution (CeraLyte, Enfalyte, Pedialyte). Don't use only water or only apple juice.", "Drinking fluids too quickly can worsen the nausea and vomiting, so try to give small frequent sips over a couple of hours, instead of drinking a large amount at once", " Try using a water dropper of rehydration solution instead of a bottle or cup", "Gradually introduce bland, easy-to-digest foods, such as toast, rice, bananas and potatoes", "Avoid giving your child full-fat dairy products, such as whole milk and ice cream, and sugary foods, such as sodas and candy. These can make diarrhea worse", "If you're breast-feeding, let your baby nurse. If your baby is bottle-fed, offer a small amount of an oral rehydration solution or regular formula"]
tonsill_remedies = ["Drink plenty of fluids. This includes warm, soothing liquids, such as soup, broth, or tea with honey and lemon", "Eat soft foods, especially if it hurts to swallow", "Gargle with warm salt water (1/4 teaspoon of salt in 8 ounces of warm water)", "Take acetaminophen or ibuprofen for fever and pain. Keep in mind that children younger than 18 years of age should not take aspirin", "Suck on a throat lozenge or hard candy", "Use a cool-misthumidifier to moisten the air", "Rest your body and your voice"]
commoncold_remedies = ["Ease discomfort with: acetaminophen or ibuprofen as needed if your child is older than 6 months, a cool-mist humidifier or steamy bathroom, saline (saltwater) drops for a congested nose, gentle suction of nasal mucus using a bulb syringe when necessary", "Offer lots of liquids — breast milk or formula for babies; water and diluted juice for older kids, but no caffeinated beverages", "Never give cough or cold medicine to children under 6 years old. Call a doctor first for older kids", "Never give aspirin to a child"]
typhoidfever_remedies = ["Antibiotic therapy is the only effective treatment for typhoid fever. Commonly prescribed antibiotics include:", "Ciprofloxacin (Cipro). In the United States, doctors often prescribe this for nonpregnant adults. Another similar drug called ofloxacin also may be used.", "Azithromycin (Zithromax). This may be used if a person is unable to take ciprofloxacin or the bacteria is resistant to ciprofloxacin", "Ceftriaxone. This injectable antibiotic is an alternative in more-complicated or serious infections and for people who may not be candidates for ciprofloxacin, such as children"]
bronchitis_remedies = ["Take OTC nonsteroidal anti-inflammatory drugs, such as ibuprofen (Advil) and naproxen (Aleve, Naprosyn), which may soothe your sore throat", "Get a humidifier to create moisture in the air. This can help loosen mucus in your nasal passages and chest, making it easier to breathe", "Drink plenty of liquids, such as water or tea, to thin out mucus. This makes it easier to cough it up or blow it out through your nose", "Add ginger to tea or hot water. Ginger is a natural anti-inflammatory that can relieve irritated and inflamed bronchial tubes", "Consume dark honey to soothe your cough. Honey also soothes your throat and has antiviral and antibacterial properties"]
pneumonia_remedies = ["Control the fever with the proper medicine and right strength for the age of your child. Fevers lower than 101° F do not need to be treated unless the child is uncomfortable", "Give your child plenty of fluids to prevent dehydration", "See that your child gets lots of rest", "Do not give over-the-counter (OTC) cough medicines or other OTC medicines without asking the health provider first. The child needs to cough and bring up the phlegm. Coughing is the body’s way of clearing the infection from the lungs", "Avoid exposing your child to tobacco smoke or other irritants in the air"]
dia_remedies = ["Continue your child's regular diet and give more liquids", "Offer additional breast milk or formula to infants", "Use an oral rehydration solution (ORS) to replace lost fluids"]
#symptoms remedies
fever_remedies = ["Encourage your child to drink fluids", "Dress your child in lightweight clothing", "Use a light blanket if your child feels chilled, until the chills end", "Don't give an infant any type of pain reliever until after you've contacted a doctor and your child has been evaluated", "If your child is 6 months old or older, give your child acetaminophen (Tylenol, others) or ibuprofen (Advil, Motrin, others). Read the label carefully for proper dosing"]
cough_remedies = ["If your child develops a “barky” or “croupy” cough, sit in a steamy bathroom together for about 20 minutes", "Offer plenty of fluids (breast milk or formula for babies; cool water and juice for older kids). Avoid carbonated or citrus drinks that may irritate a raw throat", "Run a cool-mist humidifier in your child’s bedroom", "Use saline (saltwater) nose drops to relieve congestion", "Never give cough drops (a choking hazard) to young kids or cough or cold medicine to kids under 6 years of age."]
muscleache_remedies = ["resting the area of the body where you’re experiencing aches and pains", "taking an over-the-counter pain reliever, such as ibuprofen (Advil)", "applying ice to the affected area to help relieve pain and reduce inflammation"]
headache_remedies = ["lie down in a dark, quiet room", "drink liquids", "take acetaminophen or ibuprofen as needed", "put a cool, moist cloth across the forehead or eyes"]
fatigue_remedies = ["drink enough fluids to stay hydrated", "practice healthy eating habits", "get enough sleep", "take part in relaxing activities, such as yoga"]
burningurination_remedies = ["Seek medical expert immediately"]
lossappetite_remedies = ["Start by eating 3 meals and 2-3 snacks per day", "Set an alarm to remind you to eat if you are not experiencing regular hunger cues or have a hard time remembering to eat", "Try to include more nutritious energy-dense foods such as: nuts and nut butters, dried fruits, cheese, granola bars, and avocados", "Try nutrition supplement drinks like Ensure Plus, Boost Plus, Equate Plus (Walmart brand), Carnation Instant Breakfast or regular milkshakes"]
runnynose_remedies = ["Apply a warm, moist washcloth to your face several times a day", "Inhale steam 2 to 4 times a day. One way to do this is to sit in the bathroom with the shower running. DO NOT inhale hot steam", "Use a vaporizer or humidifier"]
increasedfrequencyofurinationwithoutpassingmuchurine_remedies = ["Diet modification. You should avoid any food that appears to irritate your bladder or acts as a diuretic", "Monitoring fluid food intake. You should drink enough to prevent constipation and over-concentration of urine", "Kegel exercises. These exercises help strengthen the muscles around the bladder and urethra to improve bladder control and reduce urinary urgency and frequency."]
increasedurgencyofurination_remedies = ["Diet modification. You should avoid any food that appears to irritate your bladder or acts as a diuretic", "Monitoring fluid food intake. You should drink enough to prevent constipation and over-concentration of urine", "Kegel exercises. These exercises help strengthen the muscles around the bladder and urethra to improve bladder control and reduce urinary urgency and frequency."]
bloodyurine_remedies = ["Seek medical expert immediately"]
cloudyurine_remdies = ["Seek medical expert immediately"]
urinehasastrongodor_remedies = ["Seek medical expert immediately"]
pelvicpain_remedies = ["Over-the-counter pain relievers. Taking ibuprofen (Advil, Motrin) or acetaminophen (Tylenol) is a good first step for CPP relief", "Get moving. It might be hard to think about exercise when you feel you can’t get off the couch—but you must. Exercise increases blood flow", "Take the heat. It helps increase blood flow, which may help reduce your pain. Sit in a tub full of warm water to provide relief during flare-ups.", "Make a change. Just tweaking some of your habits can have an effect on your pain. If you smoke, stop. Nicotine -- the active ingredient in tobacco products -- inflames nerves and triggers pain", "Try supplements. In some cases, chronic pelvic pain is linked to lower-than-normal amounts of key vitamins and minerals in the blood. Vitamin D, vitamin E, and magnesium supplements may help to soothe chronic pelvic pain", "Relax. Meditation, yoga, and even deep breathing exercises can help to reduce the stress and tension that can make chronic pain even worse"]
rectalpain_remedies = ["Soak in warm baths", "After bowel movements, gently pat area with moist toilet paper or pads", "Take acetaminophen (Tylenol) or ibuprofen (Advil, Motrin) for pain", "If you know you have hemorrhoids, use over-the-counter hemorrhoid cream", "If you have fissures (cracks or splits in anal opening), use an over-the-counter hydrocortisone cream"]
swollenlymphnodes_remedies = ["Apply a warm compress. Apply a warm, wet compress, such as a washcloth dipped in hot water and wrung out, to the affected area", "Take an over-the-counter pain reliever. These include aspirin, ibuprofen (Advil, Motrin, others), naproxen (Aleve) or acetaminophen (Tylenol, others)", "Get adequate rest. You often need rest to aid your recovery from the underlying condition"]
jointpain_remedies = ["Seek medical expert immediately"]
rashes_remedies = ["add a few cups of oatmeal to the bath", "pat the skin dry (instead of rubbing) after a bath or shower", "don't scrub or scratch the affected skin", "leave the rash exposed to the air as much as possible"]
nausea_remedies = ["Drinking gradually larger amounts of clear liquids", "Avoiding solid food until the vomiting episode has passed", "Resting", "Temporarily discontinuing all oral medications, which can irritate the stomach and make vomiting worse"]
vomiting_remedies = ["Try deep breathing, This helps keep the biological response that causes motion sickness in check. Deep breathing also helps calm anxiety that may occur when you’re feeling sick", "Eat bland crackers, Dry crackers like saltines are a tried-and-true remedy for morning sickness. It’s thought they help absorb stomach acids", "Aromatherapy, Aromatherapy may help relieve nausea and vomiting", "Over-the-counter (OTC) medications to stop vomiting (antiemetics) such as Pepto-Bismol and Kaopectate contain bismuth subsalicylate"]
bleedingnosegums_remedies = ["Sit upright and lean forward. By remaining upright, you reduce blood pressure in the veins of your nose. This discourages further bleeding", "Pinch your nose. Pinching sends pressure to the bleeding point on the nasal septum and often stops the flow of blood", "To prevent re-bleeding, don't pick or blow your nose and don't bend down for several hours after the bleeding episode", "If re-bleeding occurs, blow out forcefully to clear your nose of blood clots. Then spray both sides of your nose with a decongestant nasal spray containing oxymetazoline (Afrin)"]
bruisingontheskin_remedies = ["Rest the bruised area, if possible", "Ice the bruise with an ice pack wrapped in a towel. Leave it in place for 10 to 20 minutes. Repeat several times a day for a day or two as needed", "Compress the bruised area if it is swelling, using an elastic bandage. Don't make it too tight"]
diarrhea_remedies = ["continue your child's regular diet and give more liquids", "offer additional breast milk or formula to infants", "use an oral rehydration solution (ORS) to replace lost fluids"]
clammyskin_remedies = ["Seek medical expert immediately"]
abdominalpain_remedies = ["Provide clear fluids to sip, such as water, broth, or fruit juice diluted with water", "Serve bland foods, such as saltine crackers, plain bread, dry toast, rice, gelatin, or applesauce", "Avoid spicy or greasy foods and caffeinated or carbonated drinks until 48 hours after all symptoms have gone away", "Encourage the child to have a bowel movement", "Ask your child’s doctor before giving any medicine for abdominal pain. Drugs can mask or worsen the pain"]
abdominalcrapms_remedies = ["Provide clear fluids to sip, such as water, broth, or fruit juice diluted with water", "Serve bland foods, such as saltine crackers, plain bread, dry toast, rice, gelatin, or applesauce", "Avoid spicy or greasy foods and caffeinated or carbonated drinks until 48 hours after all symptoms have gone away", "Encourage the child to have a bowel movement", "Ask your child’s doctor before giving any medicine for abdominal pain. Drugs can mask or worsen the pain"]
sorethroat_remedies = ["Rest. Get plenty of sleep. Rest your voice, too", "Drink fluids. Fluids keep the throat moist and prevent dehydration. Avoid caffeine and alcohol, which can dehydrate you", "Try comforting foods and beverage. Warm liquids — broth, caffeine-free tea or warm water with honey — and cold treats such as ice pops can soothe a sore throat", "Gargle with saltwater. A saltwater gargle of 1/4 to 1/2 teaspoon (1.25 to 2.50 milliliters) of table salt to 4 to 8 ounces (120 to 240 milliliters) of warm water can help soothe a sore throat", "Humidify the air. Use a cool-air humidifier to eliminate dry air that may further irritate a sore throat, being sure to clean the humidifier regularly so it doesn't grow mold or bacteria", "Consider lozenges or hard candy. Either can soothe a sore throat, but don't give them to children age 4 and younger because of choking risk", "Avoid irritants. Keep your home free from cigarette smoke and cleaning products that can irritate the throat"]
paininswallowing_remedies = ["Rest. Get plenty of sleep. Rest your voice, too", "Drink fluids. Fluids keep the throat moist and prevent dehydration. Avoid caffeine and alcohol, which can dehydrate you", "Try comforting foods and beverage. Warm liquids — broth, caffeine-free tea or warm water with honey — and cold treats such as ice pops can soothe a sore throat", "Gargle with saltwater. A saltwater gargle of 1/4 to 1/2 teaspoon (1.25 to 2.50 milliliters) of table salt to 4 to 8 ounces (120 to 240 milliliters) of warm water can help soothe a sore throat", "Humidify the air. Use a cool-air humidifier to eliminate dry air that may further irritate a sore throat, being sure to clean the humidifier regularly so it doesn't grow mold or bacteria", "Consider lozenges or hard candy. Either can soothe a sore throat, but don't give them to children age 4 and younger because of choking risk", "Avoid irritants. Keep your home free from cigarette smoke and cleaning products that can irritate the throat"]
scrathcyvoice_remedies = ["Breathe moist air. Use a humidifier to keep the air throughout your home or office moist", "Rest your voice as much as possible. Avoid talking or singing too loudly or for too long", "Drink plenty of fluids to prevent dehydration (avoid alcohol and caffeine)", "Moisten your throat. Try sucking on lozenges, gargling with salt water or chewing a piece of gum"]
badbreath_remedies = ["Brush your teeth after you eat. Keep a toothbrush at work to use after eating. Brush using a fluoride-containing toothpaste at least twice a day, especially after meals", "Floss at least once a day. Proper flossing removes food particles and plaque from between your teeth, helping to control bad breath", "Brush your tongue. Your tongue harbors bacteria, so carefully brushing it may reduce odors", "Clean dentures or dental appliances. If you wear a bridge or a denture, clean it thoroughly at least once a day or as directed by your dentist", "Avoid dry mouth. To keep your mouth moist, avoid tobacco and drink plenty of water — not coffee, soft drinks or alcohol, which can lead to a drier mouth", "Adjust your diet. Avoid foods such as onions and garlic that can cause bad breath. Eating a lot of sugary foods is also linked with bad breath"]
chills_remedies = ["Seek medical expert immediately"]
earache_remedies = ["Warm compresses held to the outside of the ear may help with some of the pain. Make certain that water does not get into the ear canal", "Alternatively, a cool compress may help if warmth does not. Holding a cool compress for 20 minutes at a time against the ear may be helpful", "Over-the-counter pain medications may be helpful. These include ibuprofen (Advil, Motrin), naproxen (Aleve) and acetaminophen (Tylenol, Panadol)", "Keep well hydrated and drink plenty of fluid", "Humidity may help sinuses and ears drain. It is important to be careful when using steam or hot water, especially around infants and children, to prevent scald burns", "Chewing or yawning may be helpful in easing pressure within the middle ear. Sometimes one can feel or hear popping sounds, like rice krispies, as the Eustachian tubes open and close to try to equalize pressure"]
stomachache_remedies = ["Eat several smaller meals instead of three big ones", "Chew your food slowly and well", "Stay away from foods that bother you (spicy or fried foods, for example)", "Ease stress with exercise, meditation, or yoga", "You might try a heating pad to ease belly pain", "Chamomile or peppermint tea may help with gas", "Be sure to drink plenty of clear fluids so your body has enough water"]
redswollentonsil_remedies = ["Seek medical expert immediately"]
whiteoryellowspotsintonsils_remedies = ["Seek medical expert immediately"]  
nasalcongestion_remedies = ["Use a humidifier or vaporizer", "Take long showers or breathe in steam from a pot of warm (but not too hot) water", "Drink lots of fluids. This will thin out your mucus, which could help prevent blocked sinuses", "Use a nasal saline spray. It’s salt water, and it will help keep your nasal passages from drying out", "Place a warm, wet towel on your face. It may relieve discomfort and open your nasal passages", "Prop yourself up. At night, lie on a couple of pillows. Keeping your head elevated may make breathing more comfortable"]
sneezing_remedies = ["Seek medical expert immediately"]
weakness_remedies = ["Seek medical expert immediately"]
feelingcoldeasily_remedies = ["Seek medical expert immediately"]
backpain_remedies = ["Stop normal physical activity for only the first few days. This helps calm your symptoms and reduce swelling (inflammation) in the area of the pain", "Apply heat or ice to the painful area. Use ice for the first 48 to 72 hours, then use heat", "Take over-the-counter pain relievers such as ibuprofen (Advil, Motrin IB) or acetaminophen (Tylenol)", "Sleep in a curled-up, fetal position with a pillow between your legs. If you usually sleep on your back, place a pillow or rolled towel under your knees to relieve pressure", "DO NOT do activities that involve heavy lifting or twisting of your back for the first 6 weeks after the pain begins", "DO NOT exercise in the days right after the pain begins. After 2 to 3 weeks, slowly begin to exercise again. A physical therapist can teach you which exercises are right for you"]
coughwiththickyellowgreenorbloodtingedmucus_remedies = ["Seek medical expert immediately"]
stabbingchestpainworsenswhencoughingorbreathing_remedies = ["Seek medical expert immediately"]
suddenonsetofchills_remedies = ["Seek medical expert immediately"]
frequenturgetoevacuateyourbowels_remedies = ["Seek medical expert immediately"]
loosestools_remedies = ["Same remedies with Diearrhea"]
bloating_remedies = ["ADD TURMERIC TO YOUR FOOD: Turmeric helps in treating and preventing stomach bloating as an ingredient present in turmeric, which is also referred to as curcumin is a fat-soluble antioxidant", "INCREASE YOUR POTASSIUM INTAKE: Consuming potassium is a great remedy to treat bloating. It helps in flushing out excess salt from the body and maintains fluid balance", "DRINK LEMON WATER, By drinking lemon juice, it helps in flushing out extra water content and gives relief from a bloated stomach"]
cramping_remedies = ["Seek medical expert immediately"]
dehydration_remedies = ["Help them to sit down and give them plenty of water to drink", " Giving them an oral rehydration solution to drink will help replace salt and other minerals which they’ve lost – you can buy this in sachets from any pharmacy", "If they have any painful cramps, encourage them to rest, help them stretch and massage their muscles that hurt", " Keep checking how they’re feeling – if they still feel unwell once they’re rehydrated then encourage them to see a doctor straight away"]

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
symptoms = ""
phrase = ''
phrase2= ''
myself = False
average = 0
count_yes = 0
total_symptoms = 0
has_fever = False
last_inserted_symptoms = ''

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
						#bot.send_text_message(sender_id,get_message())
						pass
				elif message.get("postback"):  # user clicked/tapped "postback" button in earlier message
					received_postback(message)
					
	return "Message Processed"

#if user send a message in text
def received_text(event):
	sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
	recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
	text = event["message"]["text"]
	global created_at, last_seen, fname, lname, ask, answer, terms
	global name, age, weight, relation, phrase, phrase2, myself, has_fever, count_yes, total_symptoms, average, symptoms,last_inserted_symptoms
	
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
		symptoms = patient_data['symptoms']
	else: 
		pass
	if symptoms == None:
		symptoms = ''
	else:
		symptoms = symptoms
	if relation == 'myself':
		phrase = 'Are you '
		phrase2 = 'you'
		myself = True
	else:
		phrase = 'Is {} '.format(name)
		myself = False
		phrase2 = name
   
	if ask == "pleased to meet me?":
		oneqrbtn = [{"content_type":"text","title":"Nice meeting you 🤗","payload":'pmyou'}]
		bot.send_quick_replies_message(sender_id, 'Are you not glad to meet me 😕?', oneqrbtn) 
		
	if ask == "agree and proceed?":
		quick_replies = {"content_type":"text","title":"🤝Agree and proceed", "payload":"yes_agree"},{"content_type":"text","title":"📇See details","payload":"see_details"}
		bot.send_quick_replies_message(sender_id, "By tapping 'Agree and proceed' you accept DrPedia's Terms of Use and Privacy Policy", quick_replies)
	
	if ask == "agree and proceed?" and answer == "see_details":
		oneqrbtn = [{"content_type":"text","title":"🤝Agree and proceed","payload":'ready_accept'}]
		bot.send_quick_replies_message(sender_id, 'Ready to go?', oneqrbtn)
		
	if ask == "check symptoms":
		oneqrbtn = [{"content_type":"text","title":"Check Symptoms 🔍","payload":'check_symptoms'}]
		bot.send_quick_replies_message(sender_id, 'How can I assist you today {}?\nI can check your/your childs symptoms🔍 and provide you pre-emptive medication afterwards.'.format(fname), oneqrbtn)
	
	if ask == "who check":
		quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
		bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(fname), quick_replies)

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
				bot.send_text_message(sender_id,'I told you in human years.')
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
				bot.send_text_message(sender_id,'Oh right {}'.format(fname)) 
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
	
	if ask == "What seems you trouble today?":
		a = "Well that doesn't sound healthy."
		inp_symptom = nlp.nlp(text)
		sentumas = list(symptoms.split(",")) 
		
		if inp_symptom != 'Invalid':
			p = ["you haven't said","we haven't covered","we haven't cater"]
			quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
			if inp_symptom in (sentumas):
				x = ["Send another symptom that you didn't said earlier","Send symptom that you simply did not give earlier"]
				bot.send_text_message(sender_id,"{} {}.".format(random.choice(x),fname))
				bot.send_quick_replies_message(sender_id, "Is there any symptoms {} experiencing that {}?".format(phrase2,random.choice(p)), quick_replies)  
				
			else:
				rest = inp_symptom.replace(" ","").replace("/","").replace("-","").replace(",","")
				Mongo.set_patient(patient, sender_id, 'symptoms',"{}{},".format(symptoms,str(inp_symptom)))
				#bot.send_text_message(sender_id,"Hmm, clearly you are not feeling well.")
				#duration and severity
				if inp_symptom == "cough":
					hardormild = {"content_type":"text","title":"Hard", "payload":'hard_cough' },{ "content_type":"text", "title":"Mild", "payload":'mild_cough' }
					bot.send_quick_replies_message(sender_id, "Is the *cough Mild or Hard?", hardormild)  
						
				if inp_symptom in ("fever","muscle aches","headache","urine has a strong odor","pelvic pain","rectal pain","joint pain","pain in swallowing","earache","stomachache","back pain","sudden onset of chills","bloating","abdominal pain","abdmoinal cramp"):
					severormild = {"content_type":"text","title":"Severe", "payload":'sever_'+rest },{ "content_type":"text", "title":"Mild", "payload":'mild_'+rest }
					bot.send_quick_replies_message(sender_id, "Is the *{} Mild or Severe?".format(inp_symptom), severormild)  
				
				if inp_symptom in ("fatigue","loss appetite","runny nose","burning urination","bloody urine","cloudy urine","swollen lymph nodes","rashes","nausea","bruising on the skin","sore throat","scratchy voice","bad breath","chills","red, swollen tonsil","white or yellow spots in tonsils","weakness","poor appetite","tiredness","wheezing","cramping","dehydration","clammy skin"):
					if inp_symptom == "bloody urine":
						bot.send_text_message(sender_id,"Bloody urine is a severe symptom,\nGo to the nearest ER/hospital immediately for further evaluation by a doctor.")
					else:
						bot.send_text_message(sender_id,"If the {} occurs 2-3 days or more.\nI suggest you seek for doctors advice.".format(inp_symptom))
					bot.send_quick_replies_message(sender_id, "Is there any symptoms {} experiencing that {}?".format(phrase2,random.choice(p)), quick_replies)  
				if inp_symptom in ("stabbing chest pain","loose stools","cough with thick yellow, green or blood-tinged mucus","feeling cold easily","increased urgency of urination","vomiting","bleeding nose/gums","nasal congestion","sneezing","diarrhea","increased frequency of urination without passing much urine"):
					if inp_symptom == "vomiting":
						bot.send_text_message(sender_id,"If vomiting \n*occurs 2-3 days or more\n*occurs 3-5 times a day or more\n*OR if vommting blood.\nGo to the nearest ER/hospital immediately!")
					else:
						bot.send_text_message(sender_id,"If the {} \n*occurs 2-3 days or more\n*occurs 3-5 times a day or more.\nI suggest you seek for doctors advice.".format(inp_symptom))
					bot.send_quick_replies_message(sender_id, "Is there any symptoms {} experiencing that {}?".format(phrase2,random.choice(p)), quick_replies)

		else:
			x =["Im sorry, humans are complicated, I'm not trained to understand things well","Sorry, I did't quite follow that, perhaps use different words?","Sorry, I did't quite follow that, maybe use different words?"]
			bot.send_text_message(sender_id,random.choice(x))
			bot.send_text_message(sender_id, "OK {}, what seems you trouble today?\nYou can just type 'i have fever' or just 'fever' and so on.".format(fname))
		
def get_average(count_yes, total_symptoms):
	print(count_yes, total_symptoms)
	if count_yes != 0 and total_symptoms !=0:
		div = count_yes / total_symptoms
		percentage =  div * 100
		print(percentage,'%')
		return int(round(percentage))
	return 0
		
def countOccurrence(tup, lst): 
	counts = Counter(tup) 
	return sum(counts[i] for i in lst)

def send_remedies(sender_id,symptoms):
	patient_symptoms = list(symptoms.split(","))
	len_ps = len(patient_symptoms)
	elements = []
	if len_ps > 2:
		print(len_ps)
		for x in range(0,len_ps-1):
			rest = patient_symptoms[x].replace(" ","").replace("/","").replace("-","").replace(",","")
			elements.append({"title":patient_symptoms[x].capitalize(),"image_url":image_url +rest+'.png',"subtitle":"If symptom persist or worsen get a doctor's consultation.","buttons":[{"type":"postback","title":"More Details","payload":rest+"_about"},{"type":"postback","title":"Remedies","payload":rest+"_remedies"}]},)
			if x == len_ps-1:
				break
		else:
			bot.send_generic_message(sender_id, elements)
	elif len(patient_symptoms) == 2:
		ps = patient_symptoms[0]

		rest = ps.replace(" ","").replace("/","").replace("-","").replace(",","")
		print(ps,len(patient_symptoms),rest)
		elements = [
				 {
				  "title":ps.capitalize(),
				  "image_url":image_url +rest+'.png',
				  "subtitle":"If symptom persist or worsen get a doctor's consultation.",
				     "buttons":[
					{
					"type":"postback",
					"title":"More Details",
					"payload":rest+"_about"
					},
					 {
					"type":"postback",
					"title":"Remedies",
					"payload":rest+"_remedies"
					}
				     ]
				}
			      ]
		bot.send_generic_message(sender_id, elements)
       		
		
	
def get_the_rest_symptoms(patient,sender_id,text, symptoms,illness,total_symptoms,count_yes,ill_name):
	patient_symptoms = list(symptoms.split(","))
	tr_symptom = [i for i in illness if i not in patient_symptoms]
	total_has_symptoms = len(patient_symptoms)
	total_illness_symptoms = len(illness)
	while True:
		if count_yes == 0:
			Mongo.set_patient(patient,sender_id,'count_yes',total_has_symptoms)
			Mongo.set_patient(patient, sender_id, 'total_symptoms', total_has_symptoms)
			tr_symptom = [i for i in illness if i not in patient_symptoms]
			if tr_symptom != None:
				res = [ tr_symptom[0]] 
				rest = res[0].replace(" ", "").replace("/", "").replace("-", "").replace(",", "")
			else:
				pass
			Mongo.set_patient(patient, sender_id, 'symptoms',"{}{},".format(patient_symptoms,str(res[0])))
			twoqrbtn = {"content_type":"text","title":"Yes","payload":'yes_'+rest},{"content_type":"text","title":"No","payload":'no_'+rest}
			bot.send_quick_replies_message(sender_id, '{} experiencing {}?'.format(phrase,res[0]), twoqrbtn)          
		else:
			Mongo.set_patient(patient, sender_id, 'count_yes', count_yes +1)
			Mongo.set_patient(patient, sender_id, 'total_symptoms', total_symptoms+1)
			tr_symptom = [i for i in illness if i not in patient_symptoms]
			if tr_symptom != None:
				res = [tr_symptom[0]]
				rest = res[0].replace(" ", "").replace("/", "").replace("-", "").replace(",", "")
			else:
				pass
			if total_illness_symptoms == total_symptoms:
				if get_average(count_yes, total_symptoms) >= 50:
					Mongo.set_patient(patient, sender_id, 'count_yes', 0)
					Mongo.set_patient(patient, sender_id, 'total_symptoms', 0)
					bot.send_text_message(sender_id, "Base on my symptom checker the {} possibly might have {}.".format(phrase2,ill_name))
					bot.send_text_message(sender_id, "I suggest that you must get a doctors consultation immediately!")
					send_remedies(sender_id,patient_symptoms)
			else:   
				Mongo.set_patient(patient, sender_id, 'symptoms',"{}{},".format(patient_symptoms,str(res[0])))
				twoqrbtn = {"content_type":"text","title":"Yes","payload":'yes_'+rest},{"content_type":"text","title":"No","payload":'no_'+rest}
				bot.send_quick_replies_message(sender_id, '{} experiencing {}?'.format(phrase,rest), twoqrbtn)   
			if text:
				if text =='yes_'+rest:
					Mongo.set_patient(patient, sender_id, 'count_yes', count_yes +1)
					twoqrbtn = {"content_type":"text","title":"Yes","payload":'yes_'+rest},{"content_type":"text","title":"No","payload":'no_'+rest}
					bot.send_quick_replies_message(sender_id, '{} experiencing {}?'.format(phrase,rest), twoqrbtn)  
				if text =='no_'+rest:
					Mongo.set_patient(patient, sender_id, 'count_yes', count_yes +1)
					twoqrbtn = {"content_type":"text","title":"Yes","payload":'yes_'+rest},{"content_type":"text","title":"No","payload":'no_'+rest}
					bot.send_quick_replies_message(sender_id, '{} experiencing {}?'.format(phrase,rest), twoqrbtn) 
		
		
#if user tap a button from a quick reply
def received_qr(event):
	sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
	recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
	text = event["message"]["quick_reply"]["payload"]
	global created_at, last_seen, fname, lname, ask, answer, terms
	global name, age, weight, relation, phrase, phrase2, myself, has_fever, count_yes, total_symptoms, average, symptoms
	
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
		symptoms = patient_data['symptoms']
	else: 
		pass
	print(symptoms)
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
	empathy = ["That sounds like it was really hurtful.","I hate that you're going through that","I’m sorry to hear that","Oh no, That sounds really hard for you","I hope things get better for you","I know how you feel","That sounds really unhealthy","Ugh... Sorry to hear that"]
	anything = ["Is there any symptoms that we haven't cater?","Aside from that, anything else?","Apart from that, Is there any symptoms?","Is there any symptoms that we haven't covered?"]
	if text == "mild_abdmoinalcramp":
		bot.send_text_message(sender_id,"Mild abdmoinal cramp is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If abdmoinal cramp occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
		
	if text == "sever_abdmoinalcramp":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If abdmoinal cramp occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_abdominalpain":
		bot.send_text_message(sender_id,"Mild abdominal pain is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If abdominal pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_abdominalpain":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If abdominal pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_bloating":
		bot.send_text_message(sender_id,"Mild bloating is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If bloating occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_bloating":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If bloating occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_suddenonsetofchills":
		bot.send_text_message(sender_id,"Mild sudden onset of chills is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If sudden onset of chills occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_suddenonsetofchills":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If sudden onset of chills occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_backpain":
		bot.send_text_message(sender_id,"Mild back pain is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If back pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_backpain":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If back pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_stomachache":
		bot.send_text_message(sender_id,"Mild stomachache is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If headache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_stomachache":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If stomachache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_earache":
		bot.send_text_message(sender_id,"Mild earache is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If headache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_earache":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If earache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_paininswallowing":
		bot.send_text_message(sender_id,"Mild pain in swallowing is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If pain in swallowing occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_paininswallowing":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If pain in swallowing occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_jointpain":
		bot.send_text_message(sender_id,"Mild joint pain is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If joint pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_jointpain":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If joint pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_rectalpain":
		bot.send_text_message(sender_id,"Mild rectal pain is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If rectal pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_rectalpain":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If rectal pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_pelvicpain":
		bot.send_text_message(sender_id,"Mild pelvic pain is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If pelvic pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_pelvicpain":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If pelvic pain occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_urinehasastrongodor":
		bot.send_text_message(sender_id,"Urine with a strong odor is just mild, it is curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If headache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_urinehasastrongodor":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If urine with a strong odor occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_headache":
		bot.send_text_message(sender_id,"Mild headache can be curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If headache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_headache":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If headache occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_muscleaches":
		bot.send_text_message(sender_id,"Mild muscle aches can be curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If muscle aches occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_muscleaches":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If muscle aches occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "mild_fever":
		bot.send_text_message(sender_id,"Mild fever can be curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If fever occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "sever_fever":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If fever occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  
	if text == "hard_cough":
		bot.send_text_message(sender_id,"{} 😔.".format(random.choice(empathy)))
		bot.send_text_message(sender_id,"If cough occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  		
	if text == "mild_cough":
		bot.send_text_message(sender_id,"Mild cough can be curable with home and natural remedies and/or over the counter medication.\nBUT if symptom persist or worsen get a medical providers advice.")
		bot.send_text_message(sender_id,"If cough occurs 2-3 days or more.\nI suggest you seek for doctors advice.")
		quick_replies = {"content_type":"text","title":"Yes", "payload":'yes_symptoms' },{ "content_type":"text", "title":"No", "payload":'no_symptoms' }
		bot.send_quick_replies_message(sender_id, "{}".format(random.choice(anything)), quick_replies)  		
	
	if text =='yes_symptoms':
		el = ["What symptoms?","Name it...","What else?"]
		bot.send_text_message(sender_id,"{}".format(random.choice(el)))  
			
	if text =='no_symptoms':
		Mongo.set_ask(users,sender_id,"")
		patient_symptoms = list(symptoms.split(","))
		for illness in data["illness"]:#get all data in the 'illness' 
			name = illness["name"]
			if name.lower() == 'flu':
				flu = illness["symptoms"]
			if name.lower() == 'dengue':
				dengue = illness["symptoms"]
			if name.lower() == 'uti':
				uti = illness["symptoms"]
			if name.lower() == 'gastroenteritis':
				gastro = illness["symptoms"]
			if name.lower() == 'tonsil':
				tonsil = illness["symptoms"]
			if name.lower() == 'common cold':
				cc = illness["symptoms"]
			if name.lower() == 'typhoid fever':
				tf = illness["symptoms"]
			if name.lower() == 'bronchitis':
				b = illness["symptoms"]
			if name.lower() == 'pneumonia':
				p = illness["symptoms"]
			if name.lower() == 'diarrhea':
				d = illness["symptoms"]
			   
		if get_average(countOccurrence(patient_symptoms, flu),len(flu)) > 70 and 'fatigue' in (patient_symptoms) and 'sore throat' in (patient_symptoms) and 'cough' in (patient_symptoms) and 'fever' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Flu".format(phrase2))
			send_remedies(sender_id,"flu,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.") 
		elif get_average(countOccurrence(patient_symptoms, dengue), len(dengue)) > 70 and 'rashes' in (patient_symptoms) and 'vomiting' in (patient_symptoms) and 'nausea' in (patient_symptoms) and 'muscle ache' in (patient_symptoms) and 'headache' in (patient_symptoms) and 'fever' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Dengue".format(phrase2)) 
			send_remedies(sender_id,"dengue,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.") 
		elif get_average(countOccurrence(patient_symptoms, uti), len(uti)) > 70 and 'burning urination' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have UTI".format(phrase2)) 
			send_remedies(sender_id,"uti,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.") 
		elif get_average(countOccurrence(patient_symptoms, gastro), len(gastro)) > 70 and 'diarrhea' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Gastroenteritis".format(phrase2)) 
			send_remedies(sender_id,"gastro,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.") 
		elif get_average(countOccurrence(patient_symptoms, tonsil), len(tonsil)) > 70 and 'sore throat' in (patient_symptoms) and 'fever' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Tonsillitis".format(phrase2)) 
			send_remedies(sender_id,"tonsil,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.")
		elif get_average(countOccurrence(patient_symptoms, cc), len(cc)) > 70 and 'sore throat' in (patient_symptoms) and 'headache' in (patient_symptoms) and 'sneezing' in (patient_symptoms) and 'cough' in (patient_symptoms) and 'runny nose' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Common Cold".format(phrase2)) 
			send_remedies(sender_id,"commoncold,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.")
		elif get_average(countOccurrence(patient_symptoms, tf), len(tf)) > 70 and 'headache' in (patient_symptoms) and 'diarrhea' in (patient_symptoms) and 'loss appetite' in (patient_symptoms) and 'fever' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Typhoid Fever".format(phrase2)) 
			send_remedies(sender_id,"typhoidfever,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.")
		elif get_average(countOccurrence(patient_symptoms,b), len(b)) > 70 and 'fever' in (patient_symptoms) and 'cough' in (patient_symptoms) and 'tiredness' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Bronchitis".format(phrase2)) 
			send_remedies(sender_id,"bronchitis,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.")
		elif get_average(countOccurrence(patient_symptoms, p), len(p)) > 70 and 'fatigue' in (patient_symptoms) and 'cough' in (patient_symptoms) and 'fever' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Pneumonia".format(phrase2)) 
			send_remedies(sender_id,"pneumonia,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.")
		elif get_average(countOccurrence(patient_symptoms, d), len(d)) > 70 and 'loose stools' in (patient_symptoms) and 'fever' in (patient_symptoms) and 'abdmoninal pain' in (patient_symptoms):
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is posible that {} might have Diarrhea".format(phrase2)) 
			send_remedies(sender_id,"diarrhea,")
			bot.send_text_message(sender_id,"I suggest you seek for experts advice.")
		else:
			bot.send_text_message(sender_id,"Based on my symptom checker in my database, there is no posible illness that {} might have".format(phrase2))   
			sorp = "is"
			if len(patient_symptoms) > 2:
				sorp= 'are'
				bot.send_text_message(sender_id,"Get an experts consultation if symptoms is worsen.")
			bot.send_text_message(sender_id,"But here {} the symptoms you've given to me and their remedies.".format(sorp))   
			send_remedies(sender_id,symptoms)
		
	if text == 'send_dengue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dengue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dengue_remedies), oneqrbtn)   
		
	if text == 'send_fever_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fever_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fever_remedies), oneqrbtn)        
	
	if text == 'send_headache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_headache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(headache_remedies), oneqrbtn)    

	if text == 'send_swollenlymphnodes_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_swollenlymphnodes_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(swollenlymphnodes_remedies), oneqrbtn)        

	if text == 'send_jointpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_jointpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(jointpain_remedies), oneqrbtn)    

	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)    

	if text == 'send_rashes_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_rashes_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(rashes_remedies), oneqrbtn)
 
	if text == 'send_nausea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nausea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nausea_remedies), oneqrbtn)        

	if text == 'send_vomiting_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_vomiting_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(vomiting_remedies), oneqrbtn)    
 
	if text == 'send_bleedingnose/gums_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bleedingnose/gums_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bleedingnose/gums_remedies), oneqrbtn)    

	if text == 'send_bruisingontheskin_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bruisingontheskin_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bruisingontheskin_remedies), oneqrbtn)    

	if text == 'send_flu_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_flu_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(flu_remedies), oneqrbtn)    
	#cough
	if text == 'send_cough_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_cough_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(cough_remedies), oneqrbtn)
	#muscleache
	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)  
	#fatigue
	if text == 'send_fatigue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fatigue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fatigue_remedies), oneqrbtn)
	#lossappetite
	if text == 'send_lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	#runnynose
	if text == 'send_runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)

	if text == 'send_uti_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_uti_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(uti_remedies), oneqrbtn)  
	#burningurination
	if text == 'send_burningurination_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_burningurination_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(burningurination_remedies), oneqrbtn)
	#increasedfrequencyofurinationwithoutpassingmuchurine
	if text == 'send_increasedfrequencyofurinationwithoutpassingmuchurine_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_increasedfrequencyofurinationwithoutpassingmuchurine_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(increasedfrequencyofurinationwithoutpassingmuchurine_remedies), oneqrbtn)  
	#increasedurgencyofurination
	if text == 'send_increasedurgencyofurination_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_increasedurgencyofurination_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(increasedurgencyofurination_remedies), oneqrbtn)    
	#bloodyurine
	if text == 'send_bloodyurine_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bloodyurine_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bloodyurine_remedies), oneqrbtn)
	#cloudyurine
	if text == 'send_cloudyurine_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_cloudyurine_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(cloudyurine_remedies), oneqrbtn)
	#urinehasastrongodor
	if text == 'send_urinehasastrongodor_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_urinehasastrongodor_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(urinehasastrongodor_remedies), oneqrbtn)
	#pelvicpain (women)
	if text == 'send_pelvicpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_pelvicpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(pelvicpain_remedies), oneqrbtn)
	#rectalpain (men)
	if text == 'send_rectalpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_rectalpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(rectalpain_remedies), oneqrbtn)

	if text == 'send_gastro_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_gastro_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(gastro_remedies), oneqrbtn)
	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)  
	#jointpain
	if text == 'fatigue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fatigue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fatigue_remedies), oneqrbtn)
	if text == 'send_fatigue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fatigue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fatigue_remedies), oneqrbtn)
	#muscleache
	if text == 'lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	if text == 'send_lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	#fever
	if text == 'runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)
	if text == 'send_runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)
	#clammyskin
	#abdominalcramps
	if text == 'muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)
	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)  
	#abdominalpain
	#lossappetite
	if text == 'lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	if text == 'send_lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)

	if text == 'tonsill_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_tonsill_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(tonsill_remedies), oneqrbtn)
	if text == 'send_tonsill_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_tonsill_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(tonsill_remedies), oneqrbtn)
	#sorethroat
	#paininswallowing
	#scratchyvoice
	if text == 'scratchyvoice_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_scratchyvoice_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(scratchyvoice_remedies), oneqrbtn)
	if text == 'send_scratchyvoice_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_scratchyvoice_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(scratchyvoice_remedies), oneqrbtn)  
	#badbreath
	if text == 'badbreath_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_badbreath_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(badbreath_remedies), oneqrbtn)
	if text == 'send_badbreath_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_badbreath_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(badbreath_remedies), oneqrbtn)    
	#chills
	if text == 'chills_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_chills_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(chills_remedies), oneqrbtn)
	if text == 'send_chills_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_chills_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(chills_remedies), oneqrbtn)
	#earache
	if text == 'earache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_earache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(earache_remedies), oneqrbtn)
	if text == 'send_earache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_earache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(earache_remedies), oneqrbtn)
	#stomachaches
	if text == 'stomachaches_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stomachaches_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stomachaches_remedies), oneqrbtn)
	if text == 'send_stomachaches_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stomachaches_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stomachaches_remedies), oneqrbtn)
	#headaches
	if text == 'headaches_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_headaches_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(headaches_remedies), oneqrbtn)
	if text == 'send_headaches_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_headaches_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(headaches_remedies), oneqrbtn)  
	#redswollentonsils
	if text == 'redswollentonsils_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_redswollentonsils_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(redswollentonsils_remedies), oneqrbtn)
	if text == 'send_redswollentonsils_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_redswollentonsils_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(redswollentonsils_remedies), oneqrbtn)    
	#whiteoryellowspotsintonsils
	if text == 'whiteoryellowspotsintonsils_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_whiteoryellowspotsintonsils_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(whiteoryellowspotsintonsils_remedies), oneqrbtn)
	if text == 'send_whiteoryellowspotsintonsils_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_whiteoryellowspotsintonsils_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(whiteoryellowspotsintonsils_remedies), oneqrbtn)



	if text == 'commoncold_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_commoncold_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(commoncold_remedies), oneqrbtn)
	if text == 'send_commoncold_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_commoncold_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(commoncold_remedies), oneqrbtn)
	#runnynose
	if text == 'runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)
	if text == 'send_runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)
	#nasalcongestion
	if text == 'nasalcongestion_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nasalcongestion_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nasalcongestion_remedies), oneqrbtn)
	if text == 'send_nasalcongestion_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nasalcongestion_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nasalcongestion_remedies), oneqrbtn)
	#sneezing
	if text == 'sneezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sneezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sneezing_remedies), oneqrbtn)
	if text == 'send_sneezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sneezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sneezing_remedies), oneqrbtn)
	if text == 'send_sorethroat_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sorethroat_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sorethroat_remedies), oneqrbtn)
	#muscleache
	if text == 'muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)
	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)   
		
	if text == 'typhoidfever_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_typhoidfever_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(typhoidfever_remedies), oneqrbtn)
	if text == 'send_typhoidfever_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_typhoidfever_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(typhoidfever_remedies), oneqrbtn)
	#weakness
	if text == 'weakness_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_weakness_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(weakness_remedies), oneqrbtn)
	if text == 'send_weakness_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_weakness_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(weakness_remedies), oneqrbtn)
	#stomachache
	if text == 'stomachache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stomachache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stomachache_remedies), oneqrbtn)
	if text == 'send_stomachache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stomachache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stomachache_remedies), oneqrbtn)
	#lossappetite
	if text == 'lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	if text == 'send_lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	 
	#fatigue
	if text == 'fatigue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fatigue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fatigue_remedies), oneqrbtn)
	if text == 'send_fatigue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fatigue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fatigue_remedies), oneqrbtn)   
	#diarrhea
	if text == 'diarrhea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_diarrhea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(diarrhea_remedies), oneqrbtn)
	if text == 'send_diarrhea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_diarrhea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(diarrhea_remedies), oneqrbtn)

	if text == 'bronchitis_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bronchitis_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bronchitis_remedies), oneqrbtn)
	if text == 'send_bronchitis_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bronchitis_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bronchitis_remedies), oneqrbtn)
	#runnynose
	if text == 'runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)
	if text == 'send_runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)
	#tiredness
	if text == 'tiredness_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_tiredness_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(tiredness_remedies), oneqrbtn)
	if text == 'send_tiredness_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_tiredness_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(tiredness_remedies), oneqrbtn)
	#sneezing
	if text == 'sneezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sneezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sneezing_remedies), oneqrbtn)
	if text == 'send_sneezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sneezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sneezing_remedies), oneqrbtn)
	#wheezing
	if text == 'wheezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_wheezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(wheezing_remedies), oneqrbtn)
	if text == 'send_wheezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_wheezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(wheezing_remedies), oneqrbtn)
	#feelingcoldeasily
	if text == 'feelingcoldeasily_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_feelingcoldeasily_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(feelingcoldeasily_remedies), oneqrbtn)
	if text == 'send_feelingcoldeasily_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_feelingcoldeasily_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(feelingcoldeasily_remedies), oneqrbtn)   
	#backpain
	if text == 'backpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_backpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(backpain_remedies), oneqrbtn)
	if text == 'send_backpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_backpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(backpain_remedies), oneqrbtn)   
	#muscleache
	if text == 'muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)
	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)

	if text == 'pneumonia_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_pneumonia_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(pneumonia_remedies), oneqrbtn)
	if text == 'send_pneumonia_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_pneumonia_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(pneumonia_remedies), oneqrbtn)
	#coughwiththickyellowgreenorblood-tingedmucus ", ", "", "", "", ""]
	if text == 'coughwiththickyellowgreenorblood-tingedmucus_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_coughwiththickyellowgreenorblood-tingedmucus_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(coughwiththickyellowgreenorblood-tingedmucus_remedies), oneqrbtn)
	if text == 'send_coughwiththickyellowgreenorblood-tingedmucus_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_coughwiththickyellowgreenorblood-tingedmucus_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(coughwiththickyellowgreenorblood-tingedmucus_remedies), oneqrbtn)
	#stabbingchestpain
	if text == 'stabbingchestpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stabbingchestpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stabbingchestpain_remedies), oneqrbtn)
	if text == 'send_stabbingchestpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stabbingchestpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stabbingchestpain_remedies), oneqrbtn)
	#worsenswhencoughingorbreathing
	if text == 'worsenswhencoughingorbreathing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_worsenswhencoughingorbreathing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(worsenswhencoughingorbreathing_remedies), oneqrbtn)
	if text == 'send_worsenswhencoughingorbreathing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_worsenswhencoughingorbreathing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(worsenswhencoughingorbreathing_remedies), oneqrbtn)
	#suddenonsetofchills
	if text == 'uddenonsetofchills_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_uddenonsetofchills_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(uddenonsetofchills_remedies), oneqrbtn)
	if text == 'send_uddenonsetofchills_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_uddenonsetofchills_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(uddenonsetofchills_remedies), oneqrbtn)
	#muscleache
	if text == 'muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)
	if text == 'send_muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)   

	if text == 'dia_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dia_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dia_remedies), oneqrbtn)
	if text == 'send_dia_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dia_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dia_remedies), oneqrbtn)
	#frequenturgetoevacuateyourbowels
	if text == 'frequenturgetoevacuateyourbowels_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_frequenturgetoevacuateyourbowels_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(frequenturgetoevacuateyourbowels_remedies), oneqrbtn)
	if text == 'send_frequenturgetoevacuateyourbowels_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_frequenturgetoevacuateyourbowels_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(frequenturgetoevacuateyourbowels_remedies), oneqrbtn)
	#loosestools
	if text == 'loosestools_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_loosestools_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(loosestools_remedies), oneqrbtn)
	if text == 'send_loosestools_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_loosestools_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(loosestools_remedies), oneqrbtn)
	#bloating
	if text == 'bloating_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bloating_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bloating_remedies), oneqrbtn)
	if text == 'send_bloating_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bloating_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bloating_remedies), oneqrbtn)
	#abdominalpain
	if text == 'abdominalpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_abdominalpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(abdominalpain_remedies), oneqrbtn)
	if text == 'send_abdominalpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_abdominalpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(abdominalpain_remedies), oneqrbtn)
	#nausea
	if text == 'nausea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nausea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nausea_remedies), oneqrbtn)
	if text == 'send_nausea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nausea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nausea_remedies), oneqrbtn)   
	#dehydration
	if text == 'dehydration_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dehydration_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dehydration_remedies), oneqrbtn)
	if text == 'send_dehydration_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dehydration_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dehydration_remedies), oneqrbtn)

	if text=='pmyou':
		Mongo.set_ask(users,sender_id,'accept terms?')
		Mongo.set_answer(users,sender_id,'glad to meet you')
		bot.send_text_message(sender_id,"I'm pleased to meet you too {}. 😉".format(fname))  
		greet_disclaimer(sender_id)
   
	if text =="yes_agree":
		Mongo.set_terms(users, sender_id,'Yes')
		bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff.")
		oneqrbtn = [{"content_type":"text","title":"Check Symptoms 🔍","payload":'check_symptoms'}]
		bot.send_quick_replies_message(sender_id, 'How can I assist you today {}?\nI can check your/your childs symptoms🔍 and provide you pre-emptive medication afterwards.'.format(fname), oneqrbtn)
	if text=='see_details':
		Mongo.set_answer(users,sender_id, "see_details")
		buttons = [{"type":"web_url","url":"https://www.termsfeed.com/disclaimer/94dea8e335bd3dc535499b2e9240c0e6","title":"Disclaimer","webview_height_ratio": "full"},{"type":"web_url","url":"https://www.termsfeed.com/terms-conditions/75301170f414e755d98670a5a116f8f7","title":"Terms and Condition","webview_height_ratio": "full"},{"type":"web_url","url":"https://www.termsfeed.com/privacy-policy/3656d3131b2631aabcc0fc318a64c2f6","title":"Privacy Policy","webview_height_ratio": "full"}]
		bot.send_button_message(sender_id, "Sure {}, here it is..".format(fname), buttons) 
		oneqrbtn = [{"content_type":"text","title":"🤝Agree and proceed","payload":'ready_accept'}]
		bot.send_quick_replies_message(sender_id, 'Ready to go?', oneqrbtn)
		
	if text == 'ready_accept':
		Mongo.set_terms(users, sender_id,'Yes')
		Mongo.set_ask(users, sender_id, 'check symptoms')
		bot.send_text_message(sender_id,"Exellent!, Now that we got that covered, we can proceed onward to the significant stuff.")
		oneqrbtn = [{"content_type":"text","title":"Check Symptoms 🔍","payload":'check_symptoms'}]
		bot.send_quick_replies_message(sender_id, 'How can I assist you today {}?\nI can check your/your childs symptoms🔍 and provide you pre-emptive medication afterwards.'.format(fname), oneqrbtn)
	
	if text == 'check_symptoms':
		Mongo.set_ask(users, sender_id, 'who check')
		bot.send_text_message(sender_id,"If you find that your concern needs immidiate action by a real doctor.\nI recommend you go to the nearest emergency clinic/hospital!")
		quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
		bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(fname), quick_replies)

	if text =='myself':
		Mongo.create_patient(patient, sender_id, first_name(sender_id), '', '', 'myself',0,0,'')
		Mongo.set_ask(users, sender_id, "How old are you?")
		bot.send_text_message(sender_id, "May I ask how old are you? In human years.")
		bot.send_text_message(sender_id, "Just type '18'\nof course you are not 200 years old. 😉")   
	if text =='mychild':
		Mongo.create_patient(patient, sender_id, '', '', '', 'mychild',0,0,'')
		Mongo.set_ask(users, sender_id, "Whats the name of your child?")
		bot.send_text_message(sender_id, "Whats the name of your child {}?".format(first_name(sender_id)))    
	if text =='someone':
		Mongo.create_patient(patient, sender_id, '', '', '', 'someone',0,0,'')
		Mongo.set_ask(users, sender_id, "Whats the name of the child?")
		bot.send_text_message(sender_id, "Whats the name the child {}?".format(first_name(sender_id)))
		
	if text == 'yes_correct1':
		if relation == 'myself':
		   bot.send_text_message(sender_id,'And you are {} kg in weight'.format(weight))
		elif relation == 'mychild':
		   bot.send_text_message(sender_id,"And your child is {} kg in weight".format(weight))
		elif relation == 'someone':
		   bot.send_text_message(sender_id,"And the child's weight is {} kg.".format(name, weight))
		bot.send_quick_replies_message(sender_id, 'Correct?', quick_replies)  
			
	if text == 'no_correct1':
		if myself == True:
			Mongo.set_ask(users, sender_id, "How old are you?")
			bot.send_text_message(sender_id, "May I ask how old are you? In human years.")
			bot.send_text_message(sender_id, "Just type '18'\nof course you are not 200 years old. 😉")
		else:
			Mongo.set_ask(users, sender_id, "Whats the name of your child?")
			bot.send_text_message(sender_id, "Whats the name the child {}?".format(first_name(sender_id)))   
			
	if text == 'yes_correct':
		Mongo.set_ask(users, sender_id, "What seems you trouble today?")
		bot.send_text_message(sender_id, "Great!")
		bot.send_text_message(sender_id, "What symptoms makes {} trouble today?".format(phrase2))
	if text == 'no_correct':
		if myself == True:
			Mongo.set_ask(users, sender_id, "How old are you?")
			bot.send_text_message(sender_id, "May I ask how old are you? In human years.")
			bot.send_text_message(sender_id, "Just type '18'\nof course you are not 200 years old. 😉")
		else:
			Mongo.set_ask(users, sender_id, "Whats the name of your child?")
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
	#illness about
	if payload == "flu_about":
		bot.send_text_message(sender_id,flu_about[0])
	if payload == "uti_about": 
		bot.send_text_message(sender_id,uti_about[0])
	if payload == "dengue_about":
		bot.send_text_message(sender_id,dengue_about[0])
	if payload == "gastro_about":
		bot.send_text_message(sender_id,gastro_about[0])
	if payload == "tonsil_about":
		bot.send_text_message(sender_id,flu_about[0])
	if payload == "commoncold_about":
		bot.send_text_message(sender_id,commoncold_about[0])
	if payload == "typhoidfever_about":
		bot.send_text_message(sender_id,typhoidfever_about[0])
	if payload == "bronchitis_about":
		bot.send_text_message(sender_id,bronchitis_about[0])
	if payload == "pneumonia_about":
		bot.send_text_message(sender_id,pneumoni_about[0])
	if payload == "diarrhea_about":
		bot.send_text_message(sender_id,diarrhea_about[0])
	#symptoms about
	if payload == "fever_about":
		bot.send_text_message(sender_id,fever_about[0])
	if payload == "cough_about":
		bot.send_text_message(sender_id,cough_about[0])
	if payload == "muscleache_about":
		bot.send_text_message(sender_id,diarrhea_about[0])
	if payload == "headache_about":
		bot.send_text_message(sender_id,headache_about[0])
	if payload == "fatigue_about":
		bot.send_text_message(sender_id,fatigue_about[0])
	if payload == "burningurination_about":
		bot.send_text_message(sender_id,burningurination_about[0])
	if payload == "lossappetite_about":
		bot.send_text_message(sender_id,lossappetite_about[0])
	if payload == "runnynose_about":
		bot.send_text_message(sender_id,runnynose_about[0])
	if payload == "increasedfrequencyofurinationwithoutpassingmuchurine_about":
		bot.send_text_message(sender_id,runnynose_about[0])
	if payload == "increasedurgencyofurination_about":
		bot.send_text_message(sender_id,increasedurgencyofurination_about[0])
	if payload == "bloodyurine_about":
		bot.send_text_message(sender_id,bloodyurine_about[0])
	if payload == "cloudyurine_about":
		bot.send_text_message(sender_id,cloudyurine_about[0])
	if payload == "urinehasastrongodor_about":
		bot.send_text_message(sender_id,urinehasastrongodor_about[0])
	if payload == "pelvicpain_about":
		bot.send_text_message(sender_id,pelvicpain_about[0])
	if payload == "rectalpain_about":
		bot.send_text_message(sender_id,rectalpain_about[0])
	if payload == "swollenlymphnodes_about":
		bot.send_text_message(sender_id,swollenlymphnodes_about[0])
	if payload == "jointpain_about":
		bot.send_text_message(sender_id,jointpain_about[0])
	if payload == "rashes_about":
		bot.send_text_message(sender_id,rashes_about[0])
	if payload == "nausea_about":
		bot.send_text_message(sender_id,nausea_about[0])
	if payload == "vomiting_about":
		bot.send_text_message(sender_id,vomiting_about[0])
	if payload == "bleedingnosegums_about":
		bot.send_text_message(sender_id,bleedingnosegums_about[0])
	if payload == "bruisingontheskin_about":
		bot.send_text_message(sender_id,bruisingontheskin_about[0])
	if payload == "diarrhea_about":
		bot.send_text_message(sender_id,dia_about[0])
	if payload == "clammyskin_about":
		bot.send_text_message(sender_id,clammyskin_about[0])
	if payload == "abdominalpain_about":
		bot.send_text_message(sender_id,abdominalpain_about[0])
	if payload == "abdominalcrapms_about":
		bot.send_text_message(sender_id,abdominalcramps_about[0])
	if payload == "sorethroat_about":
		bot.send_text_message(sender_id,sorethroat_about[0])
	if payload == "paininswallowing_about":
		bot.send_text_message(sender_id,paininswallowing_about[0])
	if payload == "scrathcyvoice_about":
		bot.send_text_message(sender_id,scrathcyvoice_about[0])
	if payload == "badbreath_about":
		bot.send_text_message(sender_id,badbreath_about[0])
	if payload == "chills_about":
		bot.send_text_message(sender_id,chills_about[0])
	if payload == "earache_about":
		bot.send_text_message(sender_id,earache_about[0])
	if payload == "stomachache_about":
		bot.send_text_message(sender_id,stomachache_about[0])
	if payload == "redswollentonsil_about":
		bot.send_text_message(sender_id,redswollentonsil_about[0])
	if payload == "whiteoryellowspotsintonsils_about":
		bot.send_text_message(sender_id,whiteoryellowspotsintonsils_about[0])
	if payload == "nasalcongestion_about":
		bot.send_text_message(sender_id,nasalcongestion_about[0])
	if payload =="sneezing_about":
		bot.send_text_message(sender_id,sneezing_about[0])
	if payload == "weakness_about":
		bot.send_text_message(sender_id,weakness_about[0])
	if payload == "feelingcoldeasily_about":
		bot.send_text_message(sender_id,feelingcoldeasily_about[0])
	if payload == "backpain_about":
		bot.send_text_message(sender_id,backpain_about[0])
	if payload == "coughwiththickyellowgreenorbloodtingedmucus_about":
		bot.send_text_message(sender_id,coughwiththickyellowgreenorbloodtingedmucus_about[0])
	if payload == "stabbingchestpainworsenswhencoughingorbreathing_about":
		bot.send_text_message(sender_id,stabbingchestpainworsenswhencoughingorbreathing_about[0])
	if payload == "suddenonsetofchills_about":
		bot.send_text_message(sender_id,suddenonsetofchills_about_about[0])
	if payload == "frequenturgetoevacuateyourbowels_about":
		bot.send_text_message(sender_id,frequenturgebowels_about_about_about[0])
	if payload == "loosestools_about":
		bot.send_text_message(sender_id,loosestools_about[0])
	if payload == "bloating_about":
		bot.send_text_message(sender_id,bloating_about[0])
	if payload == "cramping_about":
		bot.send_text_message(sender_id,cramping_about[0])
	if payload == "dehydration_about":
		bot.send_text_message(sender_id,dehydration_about[0])
	
	if payload == 'cough_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_cough_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(cough_remedies), oneqrbtn)
	if payload == 'dengue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dengue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dengue_remedies), oneqrbtn)
	
	#swollenlymphnodes
	if payload == 'swollenlymphnodes_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_swollenlymphnodes_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(swollenlymphnodes_remedies), oneqrbtn)  

	#jointpain	
	if payload == 'jointpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_jointpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(jointpain_remedies), oneqrbtn)

	#vomiting
	if payload == 'vomiting_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_vomiting_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(vomiting_remedies), oneqrbtn)
	
	#bleedingnosegums
	if payload == 'bleedingnosegums_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bleeding nose/gums_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bleedingnose/gums_remedies), oneqrbtn)
	
	#bruisingontheskin
	if payload == 'bruisingontheskin_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bruisingontheskin_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bruisingontheskin_remedies), oneqrbtn)
	
	#flu
	if payload == 'flu_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_flu_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(flu_remedies), oneqrbtn)
	
	#uti
	if payload == 'uti_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_uti_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(uti_remedies), oneqrbtn)
	
	#burningurination
	if payload == 'burningurination_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_burningurination_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(burningurination_remedies), oneqrbtn)
	
	#increasedfrequencyofurinationwithoutpassingmuchurine
	if payload == 'increasedfrequencyofurinationwithoutpassingmuchurine_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_increasedfrequencyofurinationwithoutpassingmuchurine_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(increasedfrequencyofurinationwithoutpassingmuchurine_remedies), oneqrbtn)
	
	#increasedurgencyofurination
	if payload == 'increasedurgencyofurination_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_increasedurgencyofurination_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(increasedurgencyofurination_remedies), oneqrbtn)
	
	#bloodyurine
	if payload == 'bloodyurine_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bloodyurine_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bloodyurine_remedies), oneqrbtn)
	
	#cloudyurine
	if payload == 'cloudyurine_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_cloudyurine_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(cloudyurine_remedies), oneqrbtn)
	
	#urinehasastrongodor
	if payload == 'urinehasastrongodor_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_urinehasastrongodor_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(urinehasastrongodor_remedies), oneqrbtn)
	
	#pelvicpain (women)
	if payload == 'pelvicpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_pelvicpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(pelvicpain_remedies), oneqrbtn)
	
	#rectalpain (men)
	if payload == 'rectalpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_rectalpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(rectalpain_remedies), oneqrbtn)
	
	#gastro	
	if payload == 'gastro_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_gastro_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(gastro_remedies), oneqrbtn)
	
	#clammyskin
	if payload == 'clammyskin_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_clammyskin_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(clammyskin_remedies), oneqrbtn)
	
	#abdominalcramps
	if payload == 'abdominalcramps_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_abdominalcramps_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(abdominalcramps_remedies), oneqrbtn)
	
	#tonsill
	if payload == 'tonsill_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_tonsill_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(tonsill_remedies), oneqrbtn)
	
	#paininswallowing
	if payload == 'paininswallowing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_paininswallowing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(paininswallowing_remedies), oneqrbtn)
	
	#scratchyvoice
	if payload == 'scratchyvoice_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_scratchyvoice_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(scratchyvoice_remedies), oneqrbtn)
	
	#badbreath
	if payload == 'badbreath_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_badbreath_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(badbreath_remedies), oneqrbtn)
	
	#chills
	if payload == 'chills_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_chills_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(chills_remedies), oneqrbtn)
	
	#earache
	if payload == 'earache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_earache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(earache_remedies), oneqrbtn)
	
	#redswollentonsils
	if payload == 'redswollentonsils_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_redswollentonsils_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(redswollentonsils_remedies), oneqrbtn)
	
	#whiteoryellowspotsintonsils
	if payload == 'whiteoryellowspotsintonsils_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_whiteoryellowspotsintonsils_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(whiteoryellowspotsintonsils_remedies), oneqrbtn)
	
	#commoncold
	if payload == 'commoncold_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_commoncold_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(commoncold_remedies), oneqrbtn)
	
	#nasalcongestion
	if payload == 'nasalcongestion_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nasalcongestion_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nasalcongestion_remedies), oneqrbtn)
	#Dre pag sugod raz tangala ang 'text' alisdig 'payload' pero ang naay mga 'send_' e erease
	
	#sorethroat
	if payload == 'sorethroat_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sorethroat_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sorethroat_remedies), oneqrbtn)
	
	#headache
	if payload == 'headache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_headache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(headache_remedies), oneqrbtn)
	
	#muscleache
	if payload == 'muscleache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_muscleache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(muscleache_remedies), oneqrbtn)
	
	#fever
	if payload == 'fever_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fever_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fever_remedies), oneqrbtn)
	
	#typhoidfever	
	if payload == 'typhoidfever_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_typhoidfever_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(typhoidfever_remedies), oneqrbtn)
	
	#weakness
	if payload == 'weakness_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_weakness_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(weakness_remedies), oneqrbtn)
	
	#stomachache
	if payload == 'stomachache_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stomachache_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stomachache_remedies), oneqrbtn)
	
	#lossappetite
	if payload == 'lossappetite_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_lossappetite_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(lossappetite_remedies), oneqrbtn)
	
	#rashes
	if payload == 'rashes_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_rashes_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(rashes_remedies), oneqrbtn)
	
	#fatigue
	if payload == 'fatigue_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_fatigue_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(fatigue_remedies), oneqrbtn)
	
	#diarrhea
	if payload == 'diarrhea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_diarrhea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(diarrhea_remedies), oneqrbtn)
	
	#bronchitis
	if payload == 'bronchitis_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bronchitis_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bronchitis_remedies), oneqrbtn)
	
	#runnynose
	if payload == 'runnynose_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_runnynose_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(runnynose_remedies), oneqrbtn)

	#tiredness
	if payload == 'tiredness_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_tiredness_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(tiredness_remedies), oneqrbtn)

	#sneezing
	if payload == 'sneezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_sneezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(sneezing_remedies), oneqrbtn)
	
	#wheezing
	if payload == 'wheezing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_wheezing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(wheezing_remedies), oneqrbtn)
	
	#feelingcoldeasily
	if payload == 'feelingcoldeasily_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_feelingcoldeasily_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(feelingcoldeasily_remedies), oneqrbtn)
	
	#backpain
	if payload == 'backpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_backpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(backpain_remedies), oneqrbtn)

	#pneumonia
	if payload == 'pneumonia_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_pneumonia_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(pneumonia_remedies), oneqrbtn)
	
	#coughwiththickyellowgreenorblood-tingedmucus ", ", "", "", "", ""]
	if payload == 'coughwiththickyellowgreenorblood-tingedmucus_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_coughwiththickyellowgreenorblood-tingedmucus_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(coughwiththickyellowgreenorblood-tingedmucus_remedies), oneqrbtn)
	
	#stabbingchestpain
	if payload == 'stabbingchestpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_stabbingchestpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(stabbingchestpain_remedies), oneqrbtn)
	
	#worsenswhencoughingorbreathing
	if payload == 'worsenswhencoughingorbreathing_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_worsenswhencoughingorbreathing_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(worsenswhencoughingorbreathing_remedies), oneqrbtn)
	
	#suddenonsetofchills
	if payload == 'suddenonsetofchills_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_suddenonsetofchills_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(suddenonsetofchills_remedies), oneqrbtn)
	
	#dia
	if payload == 'dia_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dia_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dia_remedies), oneqrbtn)
	
	#frequenturgetoevacuateyourbowels
	if payload == 'frequenturgetoevacuateyourbowels_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_frequenturgetoevacuateyourbowels_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(frequenturgetoevacuateyourbowels_remedies), oneqrbtn)
	
	#loosestools
	if payload == 'loosestools_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_loosestools_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(loosestools_remedies), oneqrbtn)

	#bloating
	if payload == 'bloating_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_bloating_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(bloating_remedies), oneqrbtn)

	#abdominalpain
	if payload == 'abdominalpain_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_abdominalpain_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(abdominalpain_remedies), oneqrbtn)
	
	#nausea
	if payload == 'nausea_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_nausea_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(nausea_remedies), oneqrbtn)
	 
	#dehydration
	if payload == 'dehydration_remedies':
		oneqrbtn = [{"content_type":"text","title":"📩Send Another","payload":'send_dehydration_remedies'}]
		bot.send_quick_replies_message(sender_id, random.choice(dehydration_remedies), oneqrbtn)
	
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
			Mongo.set_ask(users,sender_id, "")
			Mongo.set_answer(users,sender_id, "")
			quick_replies = {"content_type":"text","title":"Myself","payload":"myself"},{"content_type":"text","title":"My Child","payload":"mychild"},{"content_type":"text","title":"Someone else","payload":"someone"}
			bot.send_quick_replies_message(sender_id, 'Who do you want to 🔍check symptom, {}?'.format(first_name(sender_id)), quick_replies)
		elif terms == "No":
			greet_disclaimer(sender_id)
		
	if payload=='pm_dengue_prevention':
		bot.send_text_message(sender_id,'Dengue Prevention Under Construction')
	if payload=='pm_about':
		bot.send_text_message(sender_id,'About Under Construction')
	
	

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
	Mongo.set_ask(users,sender_id, "agree and proceed?")
	bot.send_text_message(sender_id,"Before we proceed onward, it's time for a brief interruption from my good friends, the lawyers. ⚖️")
	bot.send_text_message(sender_id,"Remember that DrPedia is just a robot 🤖, not a doctor 👨‍⚕️.")
	bot.send_text_message(sender_id,"DrPedia is intended for informational purposes only and DrPedia don't attempt to represent a real pediatrician or a doctor in any way.")
	quick_replies = {"content_type":"text","title":"🤝Agree and proceed", "payload":"yes_agree"},{"content_type":"text","title":"📇See details","payload":"see_details"}
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
