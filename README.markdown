A lighter twitter wrapper
======================

A pythonic implication of the Twitter API designed to more closely match the semantics
of the actual api documentation (https://dev.twitter.com/docs/api). Available calls are 
specified using YAML and loaded using reflection. 

This implementation is as small as possible. It is deliberately easy to maintain, and it should be trivial for users
to add their own API calls if the specification provided goes out of date.

Network code is based on requests. Scripts are provided to assist with creating API tokens. Both the streaming and REST API are supported. 

Unit tests have been provided for the ability
to correctly load API specifications. 

Getting started
----------------------

All connections to the Twitter API must be authenticated with OAuth. If you already have
a consumer token and an access token, you may create a connection and load the API as 
follows:

    import twitterwrapper 

    connection = twitterwrapper.Connection(
      consumer_key="REDACTED",
      consumer_secret="NULLILIED",
      access_token_key="ANONYMISED",
      access_token_secret="MYSTERIOUSLY_ABSENT")

    api = twitterwrapper.Api(connection)

However, it is not recommended for you to give the API keys this way, instead, they can be
saved in access_tokens.yaml (in your application path):
      
    some_user_name:
      access_token_key: INSERT_KEY_HERE
      access_token_secret: INSERT_SECRET_HERE
      consumer_key: INSERT_KEY_HERE
      consumer_secret: INSERT_SECRET_HERE

The tokens can then be loaded from that filestore like so:

    connection = twitterwrapper.config_connection("some_user_name")
    api = twitterwrapper.Api(connection)

Omitting the username parameter will cause the first key from the file to be loaded.

For convenience, it is also possible to create an api instance with a single line:

    api = twitterwrapper.Api()

Which is equivalent to:

    connection =  twitterwrapper.config_connection()
    api = twitterwrapper.Api(connection)
   
Getting access tokens
----------------------

To ease the creation of access tokens for the Twitter API, a script is supplied. Run:

    authenticate_twitter_cherrypy

To create the yaml files which will hold the application configuration. You will need to edit
config.yaml to reflect your consumer key. If you do not have a consumer key, get one from twitter
at https://dev.twitter.com/apps/new

Run the script again; a web browser should open for you to authenticate with Twitter. After 
authenticating, the resulting token will be saved in access_tokens.yaml

Using the API
----------------------

The structure of the API calls available closely matches that provided by Twitter at:
    https://dev.twitter.com/docs/api

For example, with a TwitterApi object called "api", to access 'statuses/home_timeline' call:

    api.statuses.home_timeline()

Some parts of the API are callable, but also have callable sub-methods, such as:

    statuses.retweeted_by(id) and
    statuses.retweeted_by.ids(id)

Methods with ID parameters in the URL, such as "statuses/show/:id", can be accessed via 
the path as normal, with the ID as a parameter, such as:

    statuses.show(id)

Objects returned will usually be ApiModel objects, representing the relevant data structures.

Some objects which are returned from the API will be "blessed" and can access the API themselves.
 
In this case, the relevant ID will be automatically supplied:

    l = api.lists.all()[0]
    l.statuses # Call to list.statuses with id l.id

For a full specification of the parts of the API implemented here, please see api.yaml

