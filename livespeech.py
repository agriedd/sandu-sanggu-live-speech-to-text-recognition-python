import os
from pocketsphinx import LiveSpeech
from pocketsphinx import get_model_path
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 12000))

speech = LiveSpeech(
     lm='./3427.lm', 
     hmm='./en-us/en-us',
	 dict = './3427.dic', 
     verbose=False, no_search=False, full_utt=False, buffer_size=1048, sampling_rate=16000
)

import json
strdata = open('./datasets.json')
words = json.load(strdata)

def getDataNormalize(items):
	# get all labels
	labels = list()
	indexLabels = list()
	labelIndex = 0

	patterns = list()
	minWord = 1
	maxWord = 1

	for item in items:
		labels.append(item['label'])
		for index in item['pattern']:
			indexLabels.append(labelIndex)
			patterns.append(index)
			# check min and max word
			wordCount = len(index.split())
			if minWord > wordCount:
				minWord = wordCount
			if maxWord <= wordCount:
				maxWord = wordCount
		# increase label index pointer
		labelIndex += 1
	result = {
		'labels': {
			'data': labels,
			'index': indexLabels
		},
		'patterns': {
			'data': patterns,
			'word': {
				'min': minWord,
				'max': maxWord
			}
		}
	}
	return result

data = getDataNormalize(words)
print(data)


def tokenizing(words, wordOptions):
	wordsList = words.strip().split()
	wordsCount = len(wordsList)
	result = list()
	# divide by min and max word section

	for wordSection in range(wordOptions['min'], wordOptions['max'] + 1):
		# split words
		sectionAvailable = wordsCount - (wordSection - 1)

		startWord = 0

		for section in range(sectionAvailable) :
			startWord = section
			endWord = wordSection + startWord
			if endWord >= wordsCount:
				endWord = wordsCount
			wordJoined = " ".join(wordsList[startWord:endWord])
			# print(wordSection, section, startWord, sectionAvailable, wordJoined)
			result.append(wordJoined)
	return result

def parseVoice(word):
    print(word)
    tokenized = tokenizing(words=word, wordOptions=data['patterns']['word'])
    # check the tokenized match words
    # reverse tokenized
    # print(tokenized)
    tokenized.reverse()
    # print(tokenized)
    patternMatched = None
    for token in tokenized:
        # print(tokenized)
        for index, pattern in enumerate(data['patterns']['data']):
            # print(pattern, "==", token, pattern == token)
            if pattern == token:
                patternMatched = index
            if patternMatched is not None:
                break
        if(patternMatched is not None):
            break
    label = None
    if(patternMatched is not None):
        labelIndex = data['labels']['index'][patternMatched]
        label = data['labels']['data'][labelIndex]
    return {
        'label': label,
        'pattern': patternMatched
    }

while True:
    message, address = server_socket.recvfrom(1024)
    print(message, address)
    for phrase in speech:
        print(phrase)
        # print(message)
        word = str(phrase)
        # print(word)
        parsedVoice = parseVoice(word.lower())
        try:
            if(parsedVoice['pattern'] is not None):
                server_socket.sendto(str.encode(
                    parsedVoice['label']
                    # word
                ), address)
        except:
            print("error")
            "error"
        
