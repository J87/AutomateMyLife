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

#custom imports
import autoWebCrawl as WebCrawl

"""--------------Twitter Auto-Poster Reloaded-----------
This is an updated version to the autoTwitterScheduler.py original
where we automatically pull new blog posts and update a db
0. Using the original autoTwitterScheduler.py file 
1. import autoWebCrawl as WebCrawl
2. grab our RSS feed and extract new links
3. update the new blog post to our tweet database
4. troll top Twitter leaders to see what hashtags they're using
5. randomly pick a hashtag combo and posting schedule
6. There is still a manual process of creating the catchy description because
creative thinking isnt automated yet...
-------------------------------------
You will need the below for this to work (apps.twitter.com)
-------------------------------------
Consumer Key (API Key)	        
Consumer Secret (API Secret)	
Access Token	        
Access Token Secret
autoWebCrawl
a beer
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
global twitSchedDB

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

        
def tweetScheduled(uid):
    """function used to send scheduled posts"""
 
    alreadyTweeted = []
    #get the visitedLinks database
    visitedLinks = pd.read_csv(twitSchedDB)
    url = visitedLinks['Links'].loc[visitedLinks['index'] == uid].values[0]
    imageURL = visitedLinks['imageURL'].loc[visitedLinks['index'] == uid].values[0]
    startText = visitedLinks['StartText'].loc[visitedLinks['index'] == uid].values[0]
    endText = visitedLinks['EndText'].loc[visitedLinks['index'] == uid].values[0]
    newText = startText+ " " +url+" "+endText+""

    print newText

    if newText != '':
        #in case something goes wrong ensure a tweet
        try:
            #check to see if there is an image
            if imageURL != '':
                #post containing image
                tweet_image(imageURL,newText)
                #print "IM TWEETING AN IMAGE",newText
                
            else:
                #post with no image
                tweet(newText)
                #print "I TWEETED TEXT",newText
                
                #send a message confirming it worked
                print "You just tweeted: ",newText
                
        except Exception,e:
            print str(e)
            print "There was an erorr in the posting"
        
    else:
        print "I dont tweet blank stuff..."


def buildHashtagIndex(topLeaders):
    """gets a hashtag from a list of my viewers interests or top twitter leaders"""
    page_list = []
    for page in Cursor(api.user_timeline,screen_name=topLeaders, count=50,_rts=True).pages(10):
        page_list.append(page)
        
    
    for page in page_list:
        for status in page:
            txt = status.text
            if "#" in txt:
                getHash = txt.split()
                allHashTag = [x for x in getHash if "#" in x]
                newHashTag = [tags.append(x) for x in allHashTag if x not in tags] #get only uniques
                if len(tags) > 100:
                    return


def pollHashtags():
    """builds a hashtagIndex from the topLeaders for their pages and
    then gets 3 randomly chosen ones"""
    topLeaders = ["DataScienceCtrl","KirkDBorne","Sentdex"] #find some top leaders
    buildHashtagIndex(topLeaders)

    #get a random hastag 
    tag1 = tags[random.randint(0,len(tags)-1)]  #i want 3 hashtags
    tag2 = tags[random.randint(0,len(tags)-1)]
    tag3 = tags[random.randint(0,len(tags)-1)]

    #print tag1,tag2,tag3
    vals = tag1+tag2+tag3
    return vals



def reschedule():
    """randomly makes a new date combo to schedule"""
    hour = str(random.randint(0,23))
    minute = random.randint(0,59)
    #takes care of the extra zero
    if minute < 10:
        minute = "0"+str(minute)+""
    day = random.randint(0,7)
    dayList = ['sun','mon','tue','wed','thur','fri','sat','each']

    newTime = ""+hour+":"+str(minute)+""+dayList[day]+""
    return newTime


def makeSchedule(job,interval,uid):
    """Morning, Afternoon or Evening"""
    if 'sec' in interval:
        print "Scheduling ",interval
        interval = int(interval.replace('sec',''))
        schedule.every(interval).seconds.do(job,uid)
        
    elif 'min' in interval:
        print "Scheduling ",interval
        interval = int(interval.replace('min',''))
        schedule.every(interval).minutes.do(job,uid)
        
    elif 'hr' in interval:
        print "Scheduling ",interval
        interval = int(interval.replace('hr',''))
        schedule.every(interval).hours.do(job,uid)
        
    elif ':' in interval and 'each' in interval:
        print "Scheduling ",interval
        #interval formal 10:30
        interval = interval.replace('each','')
        schedule.every().day.at(interval).do(job,uid)
        
    elif ':' in interval and 'mon' in interval:
        print "Scheduling ",interval
        interval = interval.replace('mon','')
        schedule.every().monday.at(interval).do(job,uid)

    elif ':' in interval and 'tue' in interval:
        print "Scheduling ",interval
        interval = interval.replace('tue','')
        schedule.every().tuesday.at(interval).do(job,uid)
        
    elif ':' in interval and 'wed' in interval:
        print "Scheduling ",interval
        interval = interval.replace('wed','')
        schedule.every().wednesday.at(interval).do(job,uid)

    elif ':' in interval and 'thur' in interval:
        print "Scheduling ",interval
        interval = interval.replace('thur','')
        schedule.every().thursday.at(interval).do(job,uid)

    elif ':' in interval and 'fri' in interval:
        print "Scheduling ",interval
        interval = interval.replace('fri','')
        schedule.every().friday.at(interval).do(job,uid)

    elif ':' in interval and 'sat' in interval:
        print "Scheduling ",interval
        interval = interval.replace('sat','')
        schedule.every().saturday.at(interval).do(job,uid)

    elif ':' in interval and 'sun' in interval:
        print "Scheduling ",interval
        interval = interval.replace('sun','')
        schedule.every().sunday.at(interval).do(job,uid)


####DONT FORGET TO ADD YOUR URL IN THIS FUNCTION
def deploySpider():
    """updates the schedule db by itself"""
    randomURL = "THIS IS WHERE YOU ADD YOUR URL!!"
    return WebCrawl.mineWebsite(randomURL)



def updateSchedDB(uid):
    """update the scheduleDB - uid is not needed just placholder"""
    deploySpider() #link, descr, imagelink
    df = pd.read_csv('spiderRez.csv')
    df = df.drop('descr',1) #encoding sucks 

    oldDB = pd.read_csv(twitSchedDB)

    newDF = oldDB.merge(df,how='outer',on=['Links'],indicator=True)
    
    print newDF
    newDF['StartText'].fillna("Pending",inplace=True)
    newDF['EndText'].fillna("NeedHashTag",inplace=True)
    newDF['whatInterval'].fillna("whatTime",inplace=True)

    for index,row in newDF.iterrows():
        newTime = reschedule() #get a new time
        #make sure the time is not duplicated
        if newTime not in newDF['whatInterval']:
            if row['EndText'] == "NeedHashTag":
                newDF['EndText'].loc[newDF['Links']==row['Links']] = pollHashtags()
            if row['whatInterval'] == "whatTime":
                newDF['whatInterval'].loc[newDF['Links']==row['Links']] = newTime

    #get rid of the previous index to reset indexes
    newDF = newDF.drop('index',1)
    newDF = newDF.drop('_merge',1) #we dont need this anymore
    newDF.to_csv("newSched.csv",encoding="utf-8")



def runAMLautoPoster():
    """the RUN function for Automate My Lifes automated Twitter Scheduler"""

    #read from the database and get when to schedule each post
    df = pd.read_csv(twitSchedDB)
    for a,data in df.iterrows():
        uid = data['index']
        interval = data['whatInterval']
        job = tweetScheduled
        makeSchedule(job,interval,uid)

    #schedule the updates to db
    uid = "NONE"
    interval = "23:30each" #run every night at 11:30
    job = updateSchedDB
    makeSchedule(job,interval,uid)

    while True:
        schedule.run_pending()
        time.sleep(1)


#sign in
twitSchedDB = 'schedDB.csv'
api = signIntoTwitter()
global tags
tags = []
t = threading.Thread(target=runAMLautoPoster())
t.start()


