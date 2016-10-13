######################Stream Using PYSPOTIFY##########################

###MUST HAVE A SPOTIFY PREMIUM ACCOUNT!!!!

#!/usr/bin/env python

"""
This is an example of playing music from Spotify using pyspotify.
The example use the :class:`spotify.AlsaSink`, and will thus only work on
systems with an ALSA sound subsystem, which means most Linux systems.

0. Make sure you have a Spotify Premium account -- it doesnt work for free accounts
1. Follow these references to create a Spotify Developer account/ make a new app and get the binaries
	ref = get keys -- https://pyspotify.mopidy.com/en/latest/quickstart/#application-keys
2. Get PySpotify installed with AlsaSink as well
	ref = install -- https://pyspotify.mopidy.com/en/latest/installation/
3. Start developing and if you need to read some documentation
	ref = https://media.readthedocs.org/pdf/pyspotify/v2.x-develop/pyspotify.pdf
4. You are only limited by your imagination
"""

from __future__ import unicode_literals

import sys
import threading

import spotify
from spotify import sink


def on_connection_state_updated(session):
	"""create a function that listens for the login status"""
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
	"""listens to see if its the end of the track"""
    end_of_track.set()


def getPlaylist(playlistName):
	"""gets the uris from a playlistName you want to search for"""
	print "You have ",len(session.playlist_container)," playlists on your account"
	i = 0
	#print all the playlist names
	for ea in session.playlist_container:
		print session.playlist_container[i].load().name

	#you can comment this out, just making sure to logout properly
	session.logout()
	session.forget_me()


def playTrack(trackURI):
	"""play any track with any given trackURI"""
	#####main function to play something

	#this is only needed if you dont use Track(u'xxxx')
	# Play a single track
	#track_uri = 'spotify:track:'+trackURI
	#track_uri = trackURI
	#track = session.get_track(track_uri).load() 

	#play a track using the info provided by Spotify themselves
	session.player.load(trackURI)
	session.player.play()

	# Wait for playback to complete or Ctrl+C
	try:
	    while not end_of_track.wait(0.1):
	        pass

	    #after exiting loop, logout 
	    session.logout()
	    session.forget_me()
	    print "logged you out properly...I think"
	
	except:
		session.logout()
		session.forget_me()
		print "Shit went wrong, I'm logging out..."


def getAlbum(albumURI):
	"""get the album information -- right now only works if you know the album URI"""
	try:
		album_uri = 'spotify:album:'+albumURI
		album = session.get_album(album_uri)
		album.load()
	except:
		print "Sorry, couldn't load the album info..."

	print "The Album name is: ",album.name()
	print "The Artist name is: ",album.artist.load().name

	#now we can browse the album
	browser = album.browse()

	#now we can get all the albums tracks
	return browser.tracks


def getCover(trackURI):
	"""get the cover and show it -- loads the values but doesnt display it for you"""
	try:
		cover_uri = 'spotify:album:'+trackURI
		cover = session.get_album(cover_uri)
		cover.load()
	except:
		print "Sorry, couldn't load the cover info..."


def getURI(searchTerm):
	"""input any search term and I'll find it for you and returns trackNames and trackURIs to use"""
	try:
		search = session.search(searchTerm)
		print search.load()
		#(search.artist_total, search.album_total, search.track_total, track.playlist_total)
		print search.artists[0].load().name #get first result
		
		#eventually will go and get cover art at the same time
		#getCover(theAlbumURI)

		print len(search.tracks) #the total number of tracks
		print [a.load() for a in search.tracks] #if you leave "name" off, you get the uris
		trackNames = [a.load().name for a in search.tracks] #make the list of all the track names
		trackURIs = [a.load() for a in search.tracks] #make a list with all the track URIs
		return trackNames,trackURIs
		#lets play blackbird - which is 1 location

	except:
		print "sorry, I couldn't find ",searchTerm," for you..."



# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()
# Process events in the background
loop = spotify.EventLoop(session)
loop.start()
# Connect an audio sink - alsaSink is used on unix systems
audio = spotify.AlsaSink(session)

# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()
# Register event listeners
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
# Assuming a previous login, we may want to logout, especially if remember_me=True previously
session.logout() #clear out any priors just in case
session.forget_me()
try:
	session.relogin()
	print "I re-logged you in good Sir..."
except:
	session.login(username="YOUR USERNAME",password="YOUR PASSWORD",remember_me=False)
	print "You have\'t been here in a bit..."

#login and wait for the end of the track
logged_in.wait()


##use this to print out what playlists you have
#getPlaylist(trackURI)

##get the cover info - this one is still in progress
#getCover(someTrackURIthatYouHave)

#loop through the tracks for the Beatles and Play them all....
trackNames,trackURIs = getURI("The Beatles")
#for every trackName and trackURI in the found lists
for trackName,trackURI in zip(trackNames,trackURIs):
	#ask if we should play that song
	answer = str(raw_input("Play "+trackName+" now?(Y,N)>"))
	#if yes, then stream it
	if answer != "N":
		print "Playing ",trackName," ..."
		playTrack(trackURI)
	else:
		pass

	#make sure you log out
	session.logout()
	session.forget_me()
