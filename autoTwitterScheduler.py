import os
import pandas as pd
import numpy as np
import random

#twitter imports
from tweepy import Stream,API
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time #we will use this to limit our consumption
import json #to capture the tweets

#web crawling imports
import requests
#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
from bs4 import BeautifulSoup

#import timing for scheduling
import schedule
import time
import threading


"""--------------The Process------------
Tweepy ref - http://docs.tweepy.org/en/v3.5.0/api.html
0. Get a twitter account and create a new app -- apps.twitter.com
1. Crawl your own website and make a list of URLs you will want to tweet out
2. Create the Scheduler function
3. Create the Post function
4. Integrate a timer function
5. Drink a beer while you watch it post
-------------------------------------
You will need the below for this to work (apps.twitter.com)
-------------------------------------
Consumer Key (API Key)	        
Consumer Secret (API Secret)	
Access Token	        
Access Token Secret
-------------------------------------
"""
ckey = 'YOUR CONSUMER KEY'
csecret = 'YOUR CONSUMER SECRET'
atoken = 'YOUR ACCESS TOKEN'
asecret = 'YOUR ACCESS SECRET'


timeDelay = random.randint(10,120)

#make api accesible globally
global api
global auth

def signIntoTwitter():
    """signs you into twitter"""
    print "Signing you in..."
    #authorize ourselves using OAuth by just passing the ckey csecret
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    api = API(auth)
    my = api.me()

    print 'Hello ',my.name
    print 'Twitter Friends: ',my.friends_count

    return api

def getImageAndSave(url):
    """opens a url and ingests the sites source code"""
    print url
    soup = requests.get(url,verify=False) #ignore the SSL connection cert
    #save the source code just in case you want to run offline
    saveFile = open('temp.jpg','wb')
    saveFile.write(soup.content)
    saveFile.close()

    print "I saved a local copy of the image to temp.jpg"
    #return soup.content


def tweet(someText):
    """App portion that does the posting"""
    if someText is not None and someText != "":
        api.update_status(someText)
        print "You just tweeted: ",someText


def tweet_image(url, message):
    filename = 'temp.jpg'
    request = requests.get(url, verify=False,stream=True)
    if request.status_code == 200:
        imageName = getImageAndSave(url)
        raw_input("hold before posting")
        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")

        
def tweetScheduled():
    """function used to send scheduled posts"""
    countT = 2
    c=0
    alreadyTweeted = []
    #get the visitedLinks database
    ##headers should be [index,Links,StartText,EndText,imageURL]
    visitedLinks = pd.read_csv('visitedLinks.csv')
           
    #put the urls 
    #loop through links and use time to stagger posts
    for index,schedText in visitedLinks.iterrows():
        #don't tweet an infinite loop
        print c
        if c == len(visitedLinks):
            print "All links have been tweeted...\n\n"
            return
        else:
            if schedText['Links'] != '':
                #in case something goes wrong ensure a tweet
                try:
                    #i = countT - 1
                    url = schedText['Links']
                    imageURL = schedText['imageURL']
                    startText = schedText['StartText']#randomPhraseList[i]
                    endText = schedText['EndText']#closing[i]
                    newText = startText+ " " +endText+" "+url+""
                    if newText not in alreadyTweeted:
                        alreadyTweeted.append(newText)
                           
                        #check to see if there is an image
                        if imageURL != '':
                            raw_input("hold")
                            #post containing image
                            #api.update_with_media(imageURL,status=newText)
                            tweet_image(imageURL,newText)
                            
                        else:
                            raw_input("hold")
                            #post with no image
                            api.update_status(newText)
        

                        #send a message confirming it worked
                        print "You just tweeted: ",newText
                    else:
                        print "You already tweeted: ",newText
                        
                except Exception,e:
                    print str(e)
                    print "There was an erorr in the posting"
                    raw_input("Please review...<ENTER>")
                        
 
                print "\nStaggering..."
                time.sleep(timeDelay)
                
            else:
                print "I dont tweet blank stuff..."
        countT += 1
        c += 1

    
def makeSchedule(job,interval):
    """Morning, Afternoon or Evening"""
    if 'sec' in interval:
        print "Scheduling ",interval
        interval = int(interval.replace('sec',''))
        print interval
        schedule.every(interval).seconds.do(job)
        
    elif 'min' in interval:
        print "Scheduling ",interval
        interval = int(interval.replace('min',''))
        schedule.every(interval).minutes.do(job)
        
    elif 'hr' in interval:
        print "Scheduling ",interval
        interval = int(interval.replace('hr',''))
        schedule.every(interval).hours.do(job)
        
    elif ':' in interval and 'each' in interval:
        print "Scheduling ",interval
        #interval formal 10:30
        interval = interval.replace('each','')
        schedule.every().day.at(interval).do(job)
        
    elif 'mon' in interval:
        print "Scheduling ",interval
        interval = interval.replace('mon','')
        schedule.every().monday.do(job)
        
    elif ':' in interval and 'wed' in interval:
        print "scheduling ",interval
        interval = interval.replace('wed','')
        print interval
        schedule.every().wednesday.at(interval).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


def runAMLautoPoster():
    """the RUN function for Automate My Lifes automated Twitter Scheduler"""
    
    ###this is a twitter post job
    interval = '30min'
    job = tweetScheduled
    makeSchedule(job,interval)

    ###this is a schedule to check for new posts on RSS feed
    interval = '10:30wed'
    job = makeLinkList
    makeSchedule(job,interval)


#sign in
#makeLinkList()
api = signIntoTwitter()
t = threading.Thread(target=runAMLautoPoster())
t.start()


