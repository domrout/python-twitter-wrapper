import twitterwrapper 

# Please make sure you run authenticate_twitter_cherrypy first, to create the API tokens needed.
api = twitterwrapper.Api()


# Post an update
#new_status = api.statuses.update("I'm tweeting programmatically!")

# Delete that update.
#new_status.destroy()

print api.users.lookup(user_id="19738650")[0].screen_name
# Search for #FML
search_result = api.search("#FML", rpp=100)

# Print all results
print repr(search_result)
for result in search_result.results:
	print result

# Get recent mentions of myself.
mentions = api.statuses.mentions()
print mentions
# Reply to the most recent mention. Don't run this if doing so would be ridiculous.
# most_recent = mentions[0]
# # Twitter demands that we manually insert the screen_name of the sender in a reply.
# most_recent.reply("@%s I hear you..." % most_recent.user.screen_name)
