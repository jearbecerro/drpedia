import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import os
path = os.path.dirname(os.path.abspath(__file__))
with open(path+"/symptoms.json",'r') as file:
	data = json.load(file)

try:
	with open(path+"/data.pickle", "rb") as f:#rb ReadByte
		words, labels, training, output = pickle.load(f)
except:
	words = []
	labels = []
	docs_x = []
	docs_y = []

	for intent in data["intents"]:#get all data in the 'intent' 
		for pattern in intent["patterns"]:#get all data in the 'pattern' list
			wrds = nltk.word_tokenize(pattern)#tokenize - get all the words in a sentence or in the 'pattern'
			words.extend(wrds)#put the tokenize words in the 'words list variable'
			docs_x.append(wrds)
			docs_y.append(intent["tag"])

		if intent["tag"] not in labels:
			labels.append(intent["tag"])

	words = [stemmer.stem(w.lower()) for w in words if w != "?"]
	words = sorted(list(set(words)))
	labels = sorted(labels)
	training = []
	output = []

	out_empty = [0 for _ in range(len(labels))]

	for x, doc in enumerate(docs_x):
		bag = []
		wrds = [stemmer.stem(w.lower()) for w in doc]
		for w in words:
			if w in wrds:
				bag.append(1)
			else:
				bag.append(0)

		output_row = out_empty[:]
		output_row[labels.index(docs_y[x])] = 1

		training.append(bag)
		output.append(output_row)


	training = numpy.array(training)
	output = numpy.array(output)

	with open(path+"/data.pickle", "wb") as f:
		pickle.dump((words, labels, training, output), f)

tensorflow.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)
model = tflearn.DNN(net)

try:
	model.load(path+"/model.tflearn")#Erease this for re traning
except:
	model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)#this line for retraining
	model.save(path+"/model.tflearn")

def bag_of_words(s, words):
	bag = [0 for _ in range(len(words))]
	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]
	for se in s_words:
		for i, w in enumerate(words):
			if w == se:
				bag[i] = 1
	return numpy.array(bag)
	
def nlp(inp):
	results = model.predict([bag_of_words(inp, words)])[0]
	results_index = numpy.argmax(results)
	tag = labels[results_index]

	if results[results_index] > 0.7:#
		for tg in data["intents"]:
			if tg['tag'] == tag:
				responses = tg['responses']
		print(responses)
		return random.choice(responses)
	else:
		return "Invalid"
