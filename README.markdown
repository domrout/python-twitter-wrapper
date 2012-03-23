A lighter twitter wrapper
======================

A less "heavy" implementation of the Twitter API within Python. The network code is 
taken from python-twitter, though this project is significantly smaller.

The calls allowed by the API are stated in a YAML file, which can be easily updated.

This API also supports a slightly more natural syntax than many others. 

OAuth authentication is supported by default. 

This version does not yet contain utilities to make it easy to save your Twitter objects, 
and many POST methods are currently missing. 

This is project is currently not automatically tested.

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
  
      api = twitterwrapper.TwitterAPI(connection)

However, it is not recommended for you to give the API keys this way, instead, they can be
saved in access_tokens.yaml (in your application path):
      
      some_user_name:
        access_token_key: INSERT_KEY_HERE
        access_token_secret: INSERT_SECRET_HERE
        consumer_key: INSERT_KEY_HERE
        consumer_secret: INSERT_SECRET_HERE


The tokens can then be loaded using config_connection, like so:

      connection = config_connection("some_user_name")

If you supply no username, the first api key from the file will be loaded.

For convenience, it is also possible to create an api instance with a single line:

      api = twitterwrapper.TwitterAPI()

Which will also use the first key from access_tokens.yaml
 
Getting access tokens
----------------------

To ease the creation of access tokens for the Twitter API, a script is supplied. Run:

        authenticate_twitter_cherrrypy

To create the yaml files which will hold the application configuration. You will need to edit
config.yaml to reflect you consumer key. If you do not have a consumer key, get one from twitter
at:

        https://dev.twitter.com/apps/new

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

