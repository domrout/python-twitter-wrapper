#API calls
API calls are as detailed at 
		[https://dev.twitter.com/docs/api](https://dev.twitter.com/docs/api)

##account
Account-level configuration settings for users


###account.rate\_limit\_status
[GET account/rate\_limit\_status](https://dev.twitter.com/docs/api/1/get/account/rate_limit_status)

Returns the remaining number of API requests available to the requesting
user before the API limit is reached for the current hour. Calls to
rate\_limit\_status do not count against the rate limit.


Example use: api.account.rate\_limit\_status()

Returns **LimitStatus** object
###account.verify\_credentials
[GET account/verify\_credentials](https://dev.twitter.com/docs/api/1/get/account/verify_credentials)

Returns an HTTP 200 OK response code and a representation of the requesting
user if authentication was successful; returns a 401 status code and an error
message if not.


Example use: api.account.verify\_credentials()

Returns **User** object
###account.totals
[GET account/totals](https://dev.twitter.com/docs/api/1/get/account/totals)

Returns the current count of friends, followers, 
updates (statuses) and favorites of the authenticating user.


Example use: api.account.totals()

##direct\_messages
[GET direct\_messages](https://dev.twitter.com/docs/api/1/get/direct_messages)

Direct Messages are short, non-public messages sent between two users.
Returns the 20 most recent direct messages sent to the authenticating user.


Example use: api.direct\_messages()

Returns **DirectMessage** object
###direct\_messages.destroy
[POST direct\_messages/destroy/:id](https://dev.twitter.com/docs/api/1/post/direct_messages/destroy/:id)

Destroys the direct message specified in the required ID parameter. 
The authenticating user must be the recipient of the specified direct message.


Example use: api.direct\_messages.destroy(id)

Returns **DirectMessage** object
###direct\_messages.show
[GET direct\_messages/show](https://dev.twitter.com/docs/api/1/get/direct_messages/show)

Returns a single direct message, specified by an id parameter


Example use: api.direct\_messages.show(id)

Returns **DirectMessage** object
###direct\_messages.sent
[GET direct\_messages/sent](https://dev.twitter.com/docs/api/1/get/direct_messages/sent)

Returns the 20 most recent direct messages sent by the authenticating user


Example use: api.direct\_messages.sent()

Returns **DirectMessage** object
###direct\_messages.new
[POST direct\_messages/new](https://dev.twitter.com/docs/api/1/post/direct_messages/new)

Sends a new direct message to the specified user from the authenticating user. 
Requires both the user and text parameters. 
Returns the sent message if successful.


Example use: api.direct\_messages.new(screen\_name, text)

Returns **DirectMessage** object
##favorites
[GET favorites](https://dev.twitter.com/docs/api/1/get/favorites)

Returns the 20 most recent favorite statuses for the authenticating user or 
user specified by the ID parameter.


Example use: api.favorites()

Returns **Status** object
###favorites.destroy
[POST favorites/destroy/:id](https://dev.twitter.com/docs/api/1/post/favorites/destroy/:id)

Un-favorites the status specified in the ID parameter as the authenticating user.
Returns the un-favorited status in the requested format when successful.
This process invoked by this method is asynchronous.


Example use: api.favorites.destroy(id)

Returns **Status** object
###favorites.create
[POST favorites/create/:id](https://dev.twitter.com/docs/api/1/post/favorites/create/:id)

Favorites the status specified in the ID parameter as the authenticating user.
Returns the favorite status when successful. 
This process invoked by this method is asynchronous.


Example use: api.favorites.create(id)

Returns **Status** object
##followers\_ids
[GET followers/ids](https://dev.twitter.com/docs/api/1/get/followers/ids)

Example use: api.followers\_ids()

##friends\_ids
[GET friends/ids](https://dev.twitter.com/docs/api/1/get/friends/ids)

Example use: api.friends\_ids()

##friendships
###friendships.outgoing
[GET friendships/outgoing](https://dev.twitter.com/docs/api/1/get/friendships/outgoing)

Returns an array of numeric IDs for every protected user for whom the 
authenticating user has a pending follow request.


Example use: api.friendships.outgoing()

###friendships.no\_retweet\_ids
[GET friendships/no\_retweet\_ids](https://dev.twitter.com/docs/api/1/get/friendships/no_retweet_ids)

Returns an array of user\_ids that the currently authenticated user does not want
to see retweets from.


Example use: api.friendships.no\_retweet\_ids()

###friendships.incoming
[GET friendships/incoming](https://dev.twitter.com/docs/api/1/get/friendships/incoming)

Returns an array of numeric IDs for every user who has a pending request
to follow the authenticating user.


Example use: api.friendships.incoming()

###friendships.exists
[GET friendships/exists](https://dev.twitter.com/docs/api/1/get/friendships/exists)

Test for the existence of friendship between two users. 
Will return true if user\_a follows user\_b, otherwise will return false.
The authenticating user must be a follower of the protected user.

Users are identified using user\_id\_a and user\_id\_b or screen\_name\_a
and screen\_name\_b


Example use: api.friendships.exists(user\_id\_a, user\_id\_b)

###friendships.show
[GET friendships/show](https://dev.twitter.com/docs/api/1/get/friendships/show)

Returns detailed information about the relationship between two users.


Example use: api.friendships.show()

###friendships.lookup
[GET friendships/lookup](https://dev.twitter.com/docs/api/1/get/friendships/lookup)

Returns the relationship of the authenticating user to the comma separated 
list of up to 100 screen\_names or user\_ids provided. Values for connections 
can be: following, following\_requested, followed\_by, none.


Example use: api.friendships.lookup()

##lists
[GET lists](https://dev.twitter.com/docs/api/1/get/lists)

Example use: api.lists()

Returns **List** object
###lists.all
[GET lists/all](https://dev.twitter.com/docs/api/1/get/lists/all)

Returns all lists the authenticating or specified user subscribes to, including their own.
The user is specified using the user\_id or screen\_name parameters. 
If no user is given, the authenticating user is used.


Example use: api.lists.all()

Returns **List** object
###lists.members
[GET lists/members](https://dev.twitter.com/docs/api/1/get/lists/members)

Example use: api.lists.members()

Returns **User** object
####lists.members.show
[GET lists/members/show](https://dev.twitter.com/docs/api/1/get/lists/members/show)

Example use: api.lists.members.show(user\_id)

Returns **User** object
###lists.subscriptions
[GET lists/subscriptions](https://dev.twitter.com/docs/api/1/get/lists/subscriptions)

Example use: api.lists.subscriptions(user\_id)

Returns **List** object
###lists.show
[GET lists/show](https://dev.twitter.com/docs/api/1/get/lists/show)

Example use: api.lists.show(list\_id)

Returns **List** object
###lists.memberships
[GET lists/memberships](https://dev.twitter.com/docs/api/1/get/lists/memberships)

Returns the lists the specified user has been added to. If user\_id or screen\_name are not
provided the memberships for the authenticating user are returned.


Example use: api.lists.memberships(screen\_name)

Returns **List** object
###lists.subscribers
[GET lists/subscribers](https://dev.twitter.com/docs/api/1/get/lists/subscribers)

Returns the subscribers of the specified list. Private list subscribers will only be 
shown if the authenticated user owns the specified list.


Example use: api.lists.subscribers()

Returns **User** object
####lists.subscribers.show
[GET lists/subscribers/show](https://dev.twitter.com/docs/api/1/get/lists/subscribers/show)

Check if the specified user is a subscriber of the specified list. 
Returns the user if they are subscriber.


Example use: api.lists.subscribers.show()

Returns **User** object
###lists.destroy
[POST lists/destroy](https://dev.twitter.com/docs/api/1/post/lists/destroy)

Deletes the specified list. The authenticated user must own the list to be able to 
destroy it.


Example use: api.lists.destroy(list\_id)

Returns **List** object
###lists.statuses
[GET lists/statuses](https://dev.twitter.com/docs/api/1/get/lists/statuses)

Returns tweet timeline for members of the specified list.
Historically, retweets were not available in list timeline responses but you can now use
the include\_rts=true parameter to additionally receive retweet objects.


Example use: api.lists.statuses(list\_id)

Returns **List** object
##search
[GET search](https://dev.twitter.com/docs/api/1/get/search)

Example use: api.search(q)

Returns **SearchResult** object
##statuses
###statuses.user\_timeline
[GET statuses/user\_timeline](https://dev.twitter.com/docs/api/1/get/statuses/user_timeline)

Example use: api.statuses.user\_timeline()

Returns **Status** object
###statuses.retweeted\_by\_user
[GET statuses/retweeted\_by\_user](https://dev.twitter.com/docs/api/1/get/statuses/retweeted_by_user)

Example use: api.statuses.retweeted\_by\_user(screen\_name)

Returns **Status** object
###statuses.retweeted\_by
[GET statuses/:id/retweeted\_by](https://dev.twitter.com/docs/api/1/get/statuses/:id/retweeted_by)

Example use: api.statuses.retweeted\_by(id)

Returns **User** object
####statuses.retweeted\_by.ids
[GET statuses/:id/retweeted\_by/ids](https://dev.twitter.com/docs/api/1/get/statuses/:id/retweeted_by/ids)

Example use: api.statuses.retweeted\_by.ids()

###statuses.retweets\_of\_me
[GET statuses/retweets\_of\_me](https://dev.twitter.com/docs/api/1/get/statuses/retweets_of_me)

Example use: api.statuses.retweets\_of\_me()

Returns **Status** object
###statuses.retweeted\_to\_me
[GET statuses/retweeted\_to\_me](https://dev.twitter.com/docs/api/1/get/statuses/retweeted_to_me)

Example use: api.statuses.retweeted\_to\_me()

Returns **Status** object
###statuses.show
[GET statuses/show](https://dev.twitter.com/docs/api/1/get/statuses/show)

Example use: api.statuses.show(id)

Returns **Status** object
###statuses.update
[POST statuses/update](https://dev.twitter.com/docs/api/1/post/statuses/update)

Example use: api.statuses.update(status)

Returns **Status** object
###statuses.home\_timeline
[GET statuses/home\_timeline](https://dev.twitter.com/docs/api/1/get/statuses/home_timeline)

Example use: api.statuses.home\_timeline()

Returns **Status** object
###statuses.retweets
[GET statuses/retweets/:id](https://dev.twitter.com/docs/api/1/get/statuses/retweets/:id)

Example use: api.statuses.retweets(id)

Returns **Status** object
###statuses.retweeted\_to\_user
[GET statuses/retweeted\_to\_user](https://dev.twitter.com/docs/api/1/get/statuses/retweeted_to_user)

Example use: api.statuses.retweeted\_to\_user(screen\_name)

Returns **Status** object
###statuses.mentions
[GET statuses/mentions](https://dev.twitter.com/docs/api/1/get/statuses/mentions)

Example use: api.statuses.mentions()

Returns **Status** object
###statuses.retweeted\_by\_me
[GET statuses/retweeted\_by\_me](https://dev.twitter.com/docs/api/1/get/statuses/retweeted_by_me)

Example use: api.statuses.retweeted\_by\_me()

Returns **Status** object
###statuses.retweet
[POST statuses/retweet/:id](https://dev.twitter.com/docs/api/1/post/statuses/retweet/:id)

Example use: api.statuses.retweet(id)

Returns **Status** object
##users
###users.search
[GET users/search](https://dev.twitter.com/docs/api/1/get/users/search)

Example use: api.users.search(q)

Returns **User** object
###users.lookup
[GET users/lookup](https://dev.twitter.com/docs/api/1/get/users/lookup)

Example use: api.users.lookup(screen\_name)

Returns **User** object
###users.contributors
[GET users/contributors](https://dev.twitter.com/docs/api/1/get/users/contributors)

Example use: api.users.contributors(screen\_name)

Returns **User** object
###users.show
[GET users/show](https://dev.twitter.com/docs/api/1/get/users/show)

Example use: api.users.show(screen\_name)

Returns **User** object
###users.suggestions
[GET users/suggestions](https://dev.twitter.com/docs/api/1/get/users/suggestions)

Example use: api.users.suggestions()

Returns **SuggestionCategory** object
###users.contributees
[GET users/contributees](https://dev.twitter.com/docs/api/1/get/users/contributees)

Example use: api.users.contributees(screen\_name)

Returns **User** object
