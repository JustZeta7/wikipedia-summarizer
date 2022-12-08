from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from urllib import request as myReq
from bs4 import BeautifulSoup as bs
import re
import nltk
import heapq
import requests
# Create your views here.

#Function to Load Home Page
def home(request):
    return render(request,'home.html');

#Function to search the Topic in the URL(Text)
def findTopic(urlText):
    cleanUrlText=re.sub(r'[^a-zA-Z]',' ',urlText)
    cleanUrlText=re.sub(r'\bhttps\b|\ben\b|\bwiki\b|\borg\b|\bwikipedia\b',' ',cleanUrlText)
    return cleanUrlText;

#The Main Summarizing Function(Extractive Sumarization)
def summarize(request):
    
    url=request.POST['wikilink'];
    
    numberOfSentence=int(request.POST['nos']);
    allParagraphContent=""

    htmlDoc=myReq.urlopen(url)
    soupObject=bs(htmlDoc,'html.parser')
    paragraphContents=soupObject.findAll('p')

    for paragraphContent in paragraphContents:
        allParagraphContent += paragraphContent.text

    #Using Regular Expression to clean the Text and
    #Creating Sentence Tokens and Words Tokens (Tokenization):

    tempCleanData=re.sub(r'\[[0-9]*\]',' ',allParagraphContent)
    tempCleanData=re.sub(r'\s+',' ',tempCleanData)

    sentence_tokens=nltk.sent_tokenize(tempCleanData) 

    tempCleanData=re.sub(r'[^a-zA-Z]', ' ', tempCleanData)
    allParagraphContent_cleanedData=re.sub(r'\s+', ' ',tempCleanData)

    word_tokens=nltk.word_tokenize(allParagraphContent_cleanedData)

    #Calculating the word Frequency

    stopwords=nltk.corpus.stopwords.words('english')
    word_frequencies={}

    for word in word_tokens:
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word]=1
            else:
                word_frequencies[word] += 1

    #Calculating word's weighted Frequency

    maximum_frequency_word=max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency_word)
    
    #Calculate Sentence Score with each word's weighted frequency

    sentence_score={}
    for sentence in sentence_tokens:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_frequencies.keys():
                if len(sentence.split(' '))<30:
                    if sentence not in sentence_score.keys():
                        sentence_score[sentence]=word_frequencies[word]
                    else:
                        sentence_score[sentence] += word_frequencies[word]

    summary=heapq.nlargest(numberOfSentence,sentence_score,key=sentence_score.get)
    finalSummary=""
    for sen in summary:
        finalSummary += sen
        
    result="\""+finalSummary+"\"";
    
    topic=findTopic(url)
    
    return render(request,'summary.html', {'output':result,'topic':topic});