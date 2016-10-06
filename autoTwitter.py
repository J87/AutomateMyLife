from tweepy import Stream,API
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time #we will use this to limit our consumption
import json #to capture the tweets

#also use my sql to save the data
import MySQLdb

#what if we want to make some graphs with the data
import pandas as pd
import matplotlib.pyplot as plt


"""--------------The Process------------
Tweepy ref - http://docs.tweepy.org/en/v3.5.0/api.html
0. Get a twitter account and create a new app -- apps.twitter.com
1. Have a list of things you think your consumers are interested in
2. Open the Twitter stream and analyze the matches from the Twitter API
3. Keep an index of screen_names, tweets and any other key information you may be interested in
	-maybe even keep links to other blogs to scrape yourself for new key words??
4. Post that data into a database or save it to a text file 
5. Extend - Start gaining followers by "favouriting" their content
6. Extend Even Further - Create some charts for your Chief Marketing Officer (CMO) with pandas
"""


ckey = 'your consumer key'
csecret = 'your consumer secret'
atoken = 'your access token'
asecret = 'your access secret'


def getLinks(text):
    regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    match = re.search(regex, text)
    if match:
        return match.group()
    return ''


class listener(StreamListener):

    def on_data(self, data):
    	try:

            print data

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
            saveCSV = "Y"
            saveDB = "N"

            ###if you want to save to a csv
            if saveCSV == "Y":
	            saveFile = open('twitDB.csv','a')
	            saveFile.write(saveThis)
	            saveFile.write('\n')
	            saveFile.close()

	        #if saveDB == "Y":
            #    #replace mysql.server with "localhost" if you are running via your own server!
            #    #server   MySQL username    MySQL pass  Database name.
            #    conn = MySQLdb.connect("mysql.server","beginneraccount","cookies","beginneraccount$tutorial")
            #    c = conn.cursor()
			#	c.execute("INSERT INTO rolodex (tweetTime, username, tweet, importantLinks, country, language) VALUES (%s,%s,%s,%s,%s,%s)",
			#	(tweetTime, username, tweet, importantLinks, country, language))
			#	conn.commit()

	        #keep the light on
            return True

        except BaseException,e:
            print "failed ondata ",str(e)
            time.sleep(5)


    def on_error(self, status):
        print status

#####opening the stream and start listening
#authorize ourselves using OAuth by just passing the ckey csecret
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

#open the twitter stream by using our class
twitterStream = Stream(auth, listener())

#use the Streams filter handler
twitterStream.filter(track=["python","automate","programming","data science"])



