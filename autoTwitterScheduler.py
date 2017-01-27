import os
import pandas as pd
import numpy as np

#twitter imports
from tweepy import Stream,API
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time #we will use this to limit our consumption
import json #to capture the tweets

#web crawling imports
import urllib2
from urllib2 import urlopen
from bs4 import BeautifulSoup

#import timing for scheduling
import schedule #this is a cool new package I found!
import time

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

#initialize some arrays you will use
try:
    #bring in your urls from the database
    visitedLinks = pd.read_csv('visitedLinks.csv')
    visitedLinks = visitedLinks['Links'].unique().tolist()
except Exception,e:
    print str(e)
    isArray = True
    #if theres no file, just write to an array for now
    print "couldnt find the visited links file, using an array"
    visitedLinks = []

#all the stuff you weed out from crawling your site
badList = ['these can be special characters',
          'etc']

#lets make a random phrase list -- could also be a db you bring in
#here you can put specific phrases matching a post
randomPhraseList = ['Ever wonder how people on twitter are always posting 24-7?',
                    'Automation in Python is my fav',
                    'Automating my tweets was more time consuming than I thought',
                    'Glad I automated these posts though',
                    'Now I can sit back and relax',
                    'Tweeting my posts from Python',
                    'Such is the awesomeness of',
                    'WIN blog',
                    'Oh ya maybe I should work on my own Amazon Echo because I love @Spotify',
                    'Now to start typing up the Twitter Scheduler tutorial',
                    'Who has time to be on Twitter 24-7 these days?',
                    'Automate your Twitter posts instead']

#oh yea, maybe we should add the fancy hashtag and at sign
#to the tweet as well
#using the keywords we focus on give them hashtags
closing = ['#datascience #python #automatemylife #wordcloud @PyRunner',
           '#wordcloud #datascience @PyRunner',
           '#datascience #wordcloud @PyRunner',
           '@PyRunner the #mechiedataist #datascience',
           '#data @PyRunner ',
           '#datascience #automatemylife @PyRunner',
           '#datascience #automatemylife @PyRunner',
           '#automatemylife by @PyRunner',
           '@SpotifyEng #automatemylife @PyRunner',
           '#automatemylife from python with @PyRunner',
           '',
           '',
           '']

#set a delay between your tweets
#so you dont post all of them so quickly
timeDelayTweets = 120

#make api accesible globally
global api

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
    #there are other cool analytics you can show here

    return api


def tweetScheduled():
    """function used to send scheduled posts"""
    countT = 1 #I started from because i was getting a duplicate link
    alreadyTweeted = []
    #loop through links and use time to stagger posts
    for link in visitedLinks:
        schedText = link
        #don't tweet an infinite loop
        if countT == len(visitedLinks):
            print "All links have been tweeted...\n\n"
            return
        else:
            if schedText != '':
                #in case something goes wrong ensure a tweet
                try:
                    i = countT - 1 #keep track of count
                    startText = randomPhraseList[i]
                    endText = closing[i]
                    #merge the phrase hashtags and content
                    newText = startText+ " " +endText+" "+schedText+""
                    if newText not in alreadyTweeted:
                        alreadyTweeted.append(newText)
                        print "You just tweeted: ",newText
                        api.update_status(newText)
                    else:
                        print "You already tweeted: ",newText
                        
                except Exception,e:
                    print str(e)
                    if schedText not in alreadyTweeted:
                        #if some error, at least tweet the url
                        alreadyTweeted.append(schedText)
                        print "You just tweeted: ",schedText
                        api.update_status(schedText)
                    else:
                        print "You already tweeted: ",schedText
                        
 
                print "\nStaggering..."
                time.sleep(timeDelayTweets)
                
            else:
                print "I dont tweet blank stuff..."
        countT += 1
        
def tweet(someText):
    """if you just want a single tweet of 'someText' """
    if someText is not None and someText != "":
        api.update_status(someText)
        print "You just tweeted: ",someText

def getTimeline(sinceId,maxId,count,page):
    """returns count of the most recent statuses between sinceId and maxId"""
    api.home_timeline(sinceId,maxId,count,page)


class StdOutListener(StreamListener):
    ''' Handles data received from the stream. '''
    
    def on_data(self, data):
        try:

            #make the data into a json object
            #it looks like a dictionary anyway
            all_data = json.loads(data)

            tweetTime = all_data["created_at"]
            tweet = all_data["text"]
            username = all_data["user"]["screen_name"]

            #who is saying what?
            print "At ",tweetTime," ",username," says --\n ",tweet
            print "\n Oh No they Didn\\'t!!!"

            #where are they saying it from? in what language?
            country = all_data["place"]["country"]
            language = all_data["language"]

            #are there any blogs we should follow that our consumers are talking about? 
            #we can check our competitors blogs?
            #maybe we should blog about topics they do or dont cover?
            importantLinks = getLinks(tweet)


            #get a unix timestamp
            saveThis = str("User: "+username+" Text: "+tweet) #twitter uses colons sometimes so we have to some up with a different method

            #save into a csv or a db
            saveCSV = "N"

            ###if you want to save to a csv
            if saveCSV == "Y":
                saveFile = open('twitDB.csv','a')
                saveFile.write(saveThis)
                saveFile.write('\n')
                saveFile.close()

            #keep the light on
            return True

        except BaseException,e:
            print "failed ondata ",str(e)
            time.sleep(5)

    def on_status(self, status):
        # Prints the text of the tweet
        #print 'User: ',status.name
        print 'Tweet text: ', status.text
 
        # There are many options in the status object,
        # hashtags can be very easily accessed.
        for hashtag in status.entries['hashtags']:
            print hashtag['text']

        #keep it going
        return true

    
    def on_error(self, status_code):
        print 'Got an error with status code: ', str(status_code)

        #if you receive 420 error then you have hit a rate limit
        if status_code == 420:
            #stop streaming
            return False
        
        else:
            return True # To continue listening
 
    def on_timeout(self):
        print 'Timeout...' 
        return True # To continue listening
 
 
def listenToChannels(channels):
    """if you want to listen to certain channels, like your own, to check your post"""
    #channels = ['DataScienceCtrl','KDnuggets','PyRunner','KirkDBorne']
    print "Listening for: ",channels
    listener = StdOutListener()
    stream = Stream(auth, listener)
    stream.filter(track=channels)

####this is the web crawler portion
def openPageGetSource(url):
    """opens a url and ingests the sites source code"""
    
    try:
        soup = urlopen(url).read()
    except Exception,e:
        print str(e)
        
    #save the source code just in case you want to run offline
    saveFile = open('source.txt','w')
    saveFile.write(soup)
    saveFile.write('\n')
    saveFile.close()
    
    return soup

def makeLinkList():
    """mine my website to grab the links to tweet about"""

    #get the RSS feed
    randomURL = 'I USED MY RSS FEED HERE'
    
    #arrays that we will write to
    aLinks = []
    pContent = []
    wordArray = []

    
    #get the page
    sourceCode = openPageGetSource(randomURL)
    soup = BeautifulSoup(sourceCode)
    #print soup.prettify()
    
    for a in soup.body.find_all('a', href=True):
        link = a['href']
        #first level data check
        if link not in visitedLinks and link not in badList and "automatemylife.org" in link and "-" in link and "category" not in link:
            #second level data check
            if "#" not in link:
                visitedLinks.append(link)
                print "Found --> ",link

    #print visitedLinks

    #lets save the links to csv
    linkDF = pd.DataFrame(visitedLinks,columns=['Links'])
    linkDF.to_csv('visitedLinks.csv')
    
    
def makeSchedule(job,interval):
    """takes a target function 'job' and time 'interval' to schedule"""
    #i wrote it to read number and unit combinations
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

    #run it
    while True:
        schedule.run_pending()
        time.sleep(1)

##main loop of the code
def runAMLautoPoster():
    """the RUN function for Automate My Lifes automated Twitter Scheduler"""
    
    ###this is a twitter post job
    interval = '4hr'
    job = tweetScheduled
    makeSchedule(job,interval)

    ###this is a day schedule to make new posts on RSS feed
    interval = '10:30wed'
    job = makeLinkList
    makeSchedule(job,interval)


#sign in
api = signIntoTwitter()
makeLinkList() #dont forget to make this
runAMLautoPoster()

#give me a shotout when you run my code
listenToChannels(['PyRunner'])
tweet("Thanks for the awesome code! @PyRunner")




