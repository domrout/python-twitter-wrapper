#Model objects
This calls, detailed at
		[https://dev.twitter.com/docs/api](https://dev.twitter.com/docs/api)
		will be available for use inside objects returned by the API.

##List
###members
[GET lists/members](https://dev.twitter.com/docs/api/1/get/lists/members)

Example use: list.members()

Returns **User** object
####members.show
[GET lists/members/show](https://dev.twitter.com/docs/api/1/get/lists/members/show)

Example use: list.members.show()

Returns **User** object
###statuses
[GET lists/statuses](https://dev.twitter.com/docs/api/1/get/lists/statuses)

Example use: list.statuses()

Returns **Status** object
###subscribers
[GET lists/subscribers](https://dev.twitter.com/docs/api/1/get/lists/subscribers)

Example use: list.subscribers()

Returns **User** object
####subscribers.show
[GET lists/subscribers/show](https://dev.twitter.com/docs/api/1/get/lists/subscribers/show)

Example use: list.subscribers.show()

Returns **User** object
##Status
###destroy
[POST statuses/destroy](https://dev.twitter.com/docs/api/1/post/statuses/destroy)

Destroys the status specified by the required ID parameter. The authenticating user must be the author of the specified status. Returns the destroyed status if successful.

Example use: status.destroy()

Returns **Status** object
###favorite
[POST favorites/create/:id](https://dev.twitter.com/docs/api/1/post/favorites/create/:id)

Favorites the status specified as the authenticating user.
Returns the favorite status when successful. 
This process invoked by this method is asynchronous.


Example use: status.favorite()

Returns **Status** object
###reply
[POST statuses/update](https://dev.twitter.com/docs/api/1/post/statuses/update)

Post a reply to the public status - reply element will be ignored unless you @mention the original poster.

Example use: status.reply(status)

Returns **Status** object
###retweet
[POST statuses/retweet/:id](https://dev.twitter.com/docs/api/1/post/statuses/retweet/:id)

Example use: status.retweet()

Returns **Status** object
###retweeted\_by
[GET statuses/:id/retweeted\_by](https://dev.twitter.com/docs/api/1/get/statuses/:id/retweeted_by)

Example use: status.retweeted\_by()

Returns **User** object
####retweeted\_by.ids
[GET statuses/:id/retweeted\_by/ids](https://dev.twitter.com/docs/api/1/get/statuses/:id/retweeted_by/ids)

Example use: status.retweeted\_by.ids()

###retweets
[GET statuses/retweets/:id](https://dev.twitter.com/docs/api/1/get/statuses/retweets/:id)

Example use: status.retweets()

Returns **Status** object
###unfavourite
[POST favorites/destroy/:id](https://dev.twitter.com/docs/api/1/post/favorites/destroy/:id)

Unfavorites the status specified as the authenticating user.
This process invoked by this method is asynchronous.


Example use: status.unfavourite()

Returns **Status** object
##SuggestionCategory
###members
[GET users/suggestions/:slug/members](https://dev.twitter.com/docs/api/1/get/users/suggestions/:slug/members)

Example use: suggestioncategory.members()

Returns **User** object
###users
[GET users/suggestions/:slug](https://dev.twitter.com/docs/api/1/get/users/suggestions/:slug)

Example use: suggestioncategory.users()

Returns **User** object
##User
###lists
####lists.subscriptions
[GET lists/subscriptions](https://dev.twitter.com/docs/api/1/get/lists/subscriptions)

Example use: user.lists.subscriptions()

Returns **List** object
