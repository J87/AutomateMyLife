"""
Automate My Life's WebCrawler
=======================================
---Objective --------------------------
Create a web-crawler that ingests a url,
retrieves the new blog posts from my site
and updates the database
---------------------------------------
The Process
1. Create a simple web crawler
2. Extract the links I don't have already
3. Update a database with the image link
4. Figure out a way to randomize the Scheduling
---------------------------------------
"""

import os
from os import path
import pandas as pd
import numpy as np
import time

#imports for web crawling
import urllib2
from urllib2 import urlopen
from bs4 import BeautifulSoup
import requests
import re

#imaging stuff
import cv2
import imutils
from PIL import Image

#threading
import threading


#this also already exists in AutoWordCloud.py
def openPageGetSource(url):
    """opens a url and ingests the sites source code"""
    try:
        soup = requests.get(url,verify=False) #urlopen(url).read()
    except Exception,e:
        print str(e)
        
    #save the source code just in case you want to run offline
    saveFile = open('source.txt','w')
    saveFile.write(soup.content)
    saveFile.write('\n')
    saveFile.close()
    
    return soup.content


def getImageLink(soup):
    """get the image link to update as well"""
    global myImageLinks
    myImageLinks = []

    c = 1 
    for i in soup.find_all('img'):
        #i only want one of them
        if c ==1:
            c+=1
            link = i['src']
            #myImageLinks.append(link)
            return link
        else:
            return "NONE"

#this part of the code was meant to replace the marketing
#aspect of the title but I think that should still be 
#a manual process 
#have fun writing your own, this will take some work
def getPostDescription(someURL):
    """gets the first bit of info of a post"""
    #get the page source code
    sourceCode = openPageGetSource(someURL)
    #send it to BS4
    soup = BeautifulSoup(sourceCode,"lxml")
    
    c = 1
    #grabs the first <h4> tag as the Twitter Description
    for t in soup.find_all('h4'):
        if c == 1:
            descr = t.text
            descr = descr.replace("'","").replace("!","").replace("?","")
            if descr != "A Data Scientist's Hobby":
                c+=1
                #print descr
                #Only use this if the Featured Image is available on post
                imageLink = getImageLink(soup)
                #print descr,imageLink
                return descr,imageLink

        else:
            return "NONE"


def getAhref(soup):
    """get the <a href> link for each blog post"""
    sched = pd.read_csv("schedDB.csv") #load in your current links
    myLinks = sched['Links'].values.tolist()
    print myLinks
    raw_input("hold")
    badList = []
    data = []
    for a in soup.find_all('a',href=True):
        #print a
        link = a['href']
        if link.endswith("/"):
            link = link[:-1] #removes the trailing /
        #dont duplicate links
        if link not in myLinks and "automatemylife.org" in link and "-" in link and "category" not in link:  
            myLinks.append(link)
            #print "---Get Words for---",link
            #go to the link and get a quick description
            descr,imageLink = getPostDescription(link)
            #print descr,imageLink
            data.append([link,descr,imageLink])

    return data
    #raw_input("test hold")



def mineWebsite(randomURL):
    """this should take a url input and return a txt file with words in it"""

    """
    #uncomment if you want to run offline
    with open('source.txt','r') as f:
        sourceCode = f.read()
        f.close()
    """

    #arrays that we will write to
    aLinks = []
    pContent = []
    wordArray = []

    #get the page source code
    sourceCode = openPageGetSource(randomURL)
    #send it to BS4
    soup = BeautifulSoup(sourceCode,"lxml")
    #if you want to print it
    #print soup.prettify()

    """
    with open('source.txt','r') as f:
        soup = f
        sourceCode = BeautifulSoup(soup,'lxml')
        f.close()
    """
    #get all the new ahrefs
    data = getAhref(soup)

    #keep a separate file just in case
    df = pd.DataFrame(data,columns=['Links','descr','imageURL'])
    df.to_csv('spiderRez.csv',encoding='utf-8',index=False)
  
    #return nothing to keep trucking
    return



