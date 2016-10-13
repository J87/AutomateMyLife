######################PYSPOTIFY##########################

###MUST HAVE A SPOTIFY PREMIUM ACCOUNT!!!!

#!/usr/bin/env python

"""
This is an example of playing music from Spotify using pyspotify.
The example use the :class:`spotify.AlsaSink`, and will thus only work on
systems with an ALSA sound subsystem, which means most Linux systems.
You can either run this file directly without arguments to play a default
track::
    python play_track.py
Or, give the script a Spotify track URI to play::
    python play_track.py spotify:track:3iFjScPoAC21CT5cbAFZ7b

ref = install -- https://pyspotify.mopidy.com/en/latest/installation/
ref = https://media.readthedocs.org/pdf/pyspotify/v2.x-develop/pyspotify.pdf
"""

from __future__ import unicode_literals

import sys
import threading

import spotify
from spotify import sink



def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
    end_of_track.set()


def getPlaylist(playlistName):
	"""gets the uris from a playlist"""
	print "You have ",len(session.playlist_container)," playlists"
	i = 0
	for ea in session.playlist_container:
		print session.playlist_container[i].load().name

	session.logout()
	session.forget_me()


def playTrack(trackURI):
	#####main function to play something
	# Play a track
	#track_uri = 'spotify:track:'+trackURI
	#track_uri = trackURI
	#track = session.get_track(track_uri).load() #this is only needed if you dont use Track(u'xxxx')
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
	#except KeyboardInterrupt:
	    #pass
	except:
		session.logout()
		session.forget_me()
		print "Shit went wrong, I'm logging out..."


def getAlbum(albumURI):
	"""get the album information"""
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
	"""get the cover and show it"""
	try:
		cover_uri = 'spotify:album:'+trackURI
		cover = session.get_album(cover_uri)
		cover.load()
	except:
		print "Sorry, couldn't load the cover info..."


def getURI(searchTerm):
	"""input any search term and I'll find it for you"""
	try:
		search = session.search(searchTerm)
		print search.load()
		#(search.artist_total, search.album_total, search.track_total, track.playlist_total)
		print search.artists[0].load().name #get first result
		print len(search.tracks)
		print [a.load() for a in search.tracks] #if you leave name off, you get the uris
		trackNames = [a.load().name for a in search.tracks]
		trackURIs = [a.load() for a in search.tracks]
		return trackNames,trackURIs
		#lets play blackbird - which is 1 location

	except:
		print "sorry, I couldn't find ",searchTerm," for you..."



# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()

# Process events in the background
loop = spotify.EventLoop(session)
loop.start()

# Connect an audio sink
audio = spotify.AlsaSink(session)


# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()


# Register event listeners
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

# Assuming a previous login with remember_me=True and a proper logout
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

#play the track

#getPlaylist(trackURI)

#loop through the tracks for the Beatles and Play them all....
trackNames,trackURIs = getURI("The Beatles")
for trackName,trackURI in zip(trackNames,trackURIs):
	answer = str(raw_input("Play "+trackName+" now?(Y,N)>"))
	if answer != "N":
		print "Playing ",trackName," ..."
		playTrack(trackURI)
	else:
		pass

	session.logout()
	session.forget_me()
