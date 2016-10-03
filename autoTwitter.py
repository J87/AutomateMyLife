from tweepy import Stream,API
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener


ckey = 'c-key'
csecret = 'c-secret'
atoken = 'a-token'
asecret = 'a-secret'

class listener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=["car"])



