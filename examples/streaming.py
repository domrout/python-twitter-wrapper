"""Connects to the streaming API and prints out results"""

import twitterwrapper 

from twitterwrapper.models import StreamingCommands, Status

# Please make sure you run authenticate_twitter_cherrypy first, to create the API tokens needed.
keep_streaming = True 
api = twitterwrapper.Api()

while keep_streaming:
	try:
		for tweet in api.user( 
			timeout=60, 
			yield_exceptions=True):

			if isinstance(tweet, Status):
				print "Real tweet:", tweet
			else:
				print "Command: ", tweet
	except twitterwrapper.TwitterException as e:
		print str(e)
		if e.code not in e.RETRY_CODES:
			keep_streaming = False


