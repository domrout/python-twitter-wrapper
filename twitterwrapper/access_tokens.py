#!/usr/bin/env python
#
# Copyright 2012 Dominic Rout
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
  Classes to assist with reading and writing API keys.

  Keys are by default stored in the file access_tokens.yaml, and loaded from there.

  The location of the key file can be altered by supplying a different location.

  Consumer and access tokens can also be supplied programmatically if desired. They 
  should be supplied in a dictionary of the following form:

  {
    "access_token_key": "INSERT_KEY_HERE",
    "access_token_secret": "INSERT_SECRET_HERE",
    "consumer_key": "INSERT_KEY_HERE",
    "consumer_secret": "INSERT_SECRET_HERE"
  }
"""
import oauth2, urlparse, urllib, yaml
from _connection import Connection

DEFAULT_ACCESS_TOKENS_FILE = "access_tokens.yaml"

class AccessTokenStore(object):
  def __init__(self, filename = DEFAULT_ACCESS_TOKENS_FILE):
    self.filename = filename
    self.tokens = dict()

  def load(self):
    """Reads any tokens not already in memory from the specified file"""
    try:
      with open(self.filename) as f:
        result = yaml.load(f.read())
    except IOError:
      raise IOError("Access token file %s couldn't be opened. Try running authenticate_twitter_cherrypy ?" % self.filename)

    if result:
      self.tokens.update(result)

  def save(self):
    """Overwrites the filestore and saves all tokens"""
    try:
      with open(self.filename, "w") as f:
        yaml.dump(self.tokens, f, default_flow_style=False)

    except IOError:
      raise IOError("Access token file %s couldn't be opened." % self.filename)


  def get_auth(self, screen_name = None):
    """
      Gives the authentication parameters needed to create a connnection object.

      Auth params are in the form:        
        {
          "access_token_key": "INSERT_KEY_HERE",
          "access_token_secret": "INSERT_SECRET_HERE",
          "consumer_key": "INSERT_KEY_HERE",
          "consumer_secret": "INSERT_SECRET_HERE"
        }
    """
    if screen_name:
      if screen_name in self.tokens:
        return self.tokens[screen_name]
      else:
        raise Exception("Screen name not found in access token file")
    elif len(self.tokens) > 0:
      screen_name = self.tokens.keys()[0]
      return self.tokens[screen_name]
    else:
      raise Exception("No access tokens available")

  def get_connection(self, screen_name = None):
    """Loads authentication tokens and creates a connection to the twitter API.

      Screen name is optional, if not supplied the first set of tokens will be used."""
    auth = self.get_auth(screen_name)

    if not "connection" in auth:
      auth["connection"] = Connection(**auth)

    return auth["connection"]

  def add_auth(self, 
    screen_name,
    access_token_key, 
    access_token_secret, 
    consumer_key, 
    consumer_secret):
    """Add a new token to the filestore."""
    self.tokens[screen_name] = {
          "access_token_key": access_token_key,
          "access_token_secret": access_token_secret,
          "consumer_key": consumer_key,
          "consumer_secret": consumer_secret
        }

def config_connection(username = None, filename=DEFAULT_ACCESS_TOKENS_FILE):
  """
    Convenience method to load the access tokens and create a connection.

    If used repeatedly this will load the file many times. If that's not what
    you want, use AccessTokenStore directly.
  """
  store = AccessTokenStore(filename)
  store.load()

  return store.get_connection(username)

def get_auth(username = None, filename=DEFAULT_ACCESS_TOKENS_FILE):
  """
    Convenience method to load the access tokens.

    If used repeatedly this will load the file many times. If that's not what
    you want, use AccessTokenStore directly.
  """
  store = AccessTokenStore(filename)
  store.load()

  return store.get_auth(username)

class AuthenticationProcess(object):
  """
    Provides some of the fundamentals of the authentication process.

    Should be subclassed to provide actual practical methods for authentication
  """
  REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
  ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
  AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'

  def __init__(self, config):
    self.configure_auth(config)
    self.request_tokens = {}
    self.initialize_token_store()

  def configure_auth(self, config):
    """Loads necessary parameters from a dictionary representing the 
      configuration for the authentication process."""
    self.oauth_consumer_token = config["consumer_token"]
    self.oauth_consumer_secret = config["consumer_secret"]

    self.request_token_url = config.get("request_token_url", self.REQUEST_TOKEN_URL)
    self.access_token_url = config.get("access_token_url", self.ACCESS_TOKEN_URL)
    self.authorize_url = config.get("authorize_url", self.AUTHORIZE_URL)

    self.consumer = oauth2.Consumer(self.oauth_consumer_token, self.oauth_consumer_secret)

  def initialize_token_store(self):
    """Loads the token store. If you want to support using other token stores,
      overwrite with something more sensible."""
    self.token_store = AccessTokenStore()
    self.token_store.load()

  def generate_authorize_url(self, callback="oob"):
    """Uses the given config to connect to the API and get a token with which
      to authorise the app; redirect the user to the URL returned."""
    client = oauth2.Client(self.consumer)
    if callback:
      params = {
        'oauth_callback':callback
      }
    else:
      params = dict()

    resp, content = client.request(self.request_token_url, "POST", body=urllib.urlencode(params))
    request_token = dict(urlparse.parse_qsl(content))

    if "oauth_token" in request_token:
      oauth_token = request_token['oauth_token']
      self.request_tokens[oauth_token] = request_token
      return "%s?oauth_token=%s" % (self.authorize_url, oauth_token)
    else:
      print content
      if "Desktop applications only support the oauth_callback" in content:
        raise Exception("Twitter thinks this is a desktop app. Set a fake callback URL for the app at dev.twitter.com")
      else:
        raise Exception("Could not generate request token for authentication. Are the keys correct?")

  def verify_authorization(self, oauth_verifier, oauth_token = None):
    """Verifies the authentication given by a user after they've been
      to twitter.

      Adds the new token to the store and saves.

      Returns a complete set of auth data."""

    # Hack to maintain backwards compatibility when only one token is used.
    if oauth_token == None:
      try:
        oauth_token = self.request_tokens.keys()[0]
      except IndexError:
        raise Exception("No access token exists currently")

    try:
      # Get the actual token for this request
      request_token = self.request_tokens[oauth_token]
    except KeyError:
      raise Exception("Supplied access token has not been seen before")

    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(self.consumer, token)
    resp, content = client.request(self.access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    return {
        "screen_name": access_token['screen_name'],
        "access_token_key": access_token['oauth_token'],
        "access_token_secret": access_token['oauth_token_secret'], 
        "consumer_key": self.oauth_consumer_token,
        "consumer_secret": self.oauth_consumer_secret
      }

