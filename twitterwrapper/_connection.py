#!/usr/bin/python2.4
#
# Copyright 2007 The Python-Twitter Developers
# Modified heavily under the terms of the Apache license by Dominic Rout
# 
# This file used to be twitter.py
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

"""A connection to the Twitter API"""
import base64
import calendar
import datetime
import httplib
import os
import rfc822
import sys
import tempfile
import textwrap
import time
import calendar
import urllib
import urllib2
import urlparse
import gzip
import StringIO
import anyjson

from functools import partial

# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl, parse_qs
except ImportError:
  from cgi import parse_qsl, parse_qs

try:
  from hashlib import md5
except ImportError:
  from md5 import md5

import oauth2 as oauth

# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()


class Connection:
  DEFAULT_CACHE_TIMEOUT = 60 # cache for 1 minute
  _API_REALM = 'Twitter API'


  def __init__(self,
               consumer_key=None,
               consumer_secret=None,
               access_token_key=None,
               access_token_secret=None,
               input_encoding=None,
               request_headers=None,
               cache=DEFAULT_CACHE,
               shortner=None,
               base_url=None,
               use_gzip_compression=False,
               debugHTTP=False):

      if cache == DEFAULT_CACHE:
        self._cache = _FileCache()
      else:
        self._cache = cache

      self._urllib         = urllib2
      self._cache_timeout  = Connection.DEFAULT_CACHE_TIMEOUT
      self._input_encoding = input_encoding
      self._use_gzip       = use_gzip_compression
      self._debugHTTP      = debugHTTP
      self._oauth_consumer = None
      self._shortlink_size = 19

      if request_headers:
        self._request_headers = request_headers
      else:
        self._request_headers = {}


      self._request_headers['User-Agent'] = 'Python-urllib/%s' % \
                   (self._urllib.__version__)

      self._default_params = {}

      if base_url is None:
        self.base_url = 'https://api.twitter.com/1'
      else:
        self.base_url = base_url

      if consumer_key is not None and (access_token_key is None or
                                       access_token_secret is None):
        print >> sys.stderr, 'Twitter now requires an oAuth Access Token for API calls.'
        print >> sys.stderr, 'If your using this library from a command line utility, please'
        print >> sys.stderr, 'run the the included get_access_token.py tool to generate one.'

        raise Exception('Twitter requires oAuth Access Token for all API access')

      self.SetCredentials(consumer_key, consumer_secret, access_token_key, access_token_secret)

  def SetCredentials(self,
                     consumer_key,
                     consumer_secret,
                     access_token_key=None,
                     access_token_secret=None):
    '''Set the consumer_key and consumer_secret for this instance

    Args:
      consumer_key:
        The consumer_key of the twitter account.
      consumer_secret:
        The consumer_secret for the twitter account.
      access_token_key:
        The oAuth access token key value you retrieved
        from running get_access_token.py.
      access_token_secret:
        The oAuth access token's secret, also retrieved
        from the get_access_token.py run.
    '''
    self._consumer_key        = consumer_key
    self._consumer_secret     = consumer_secret
    self._access_token_key    = access_token_key
    self._access_token_secret = access_token_secret
    self._oauth_consumer      = None

    if consumer_key is not None and consumer_secret is not None and \
       access_token_key is not None and access_token_secret is not None:
      self._signature_method_plaintext = oauth.SignatureMethod_PLAINTEXT()
      self._signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

      self._oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
      self._oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

  def ClearCredentials(self):
    '''Clear the any credentials for this instance
    '''
    self._consumer_key        = None
    self._consumer_secret     = None
    self._access_token_key    = None
    self._access_token_secret = None
    self._oauth_consumer      = None

  def _BuildUrl(self, url, path_elements=None, extra_params=None):
    # Break url into consituent parts
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

    # Add any additional path elements to the path
    if path_elements:
      # Filter out the path elements that have a value of None
      p = [i for i in path_elements if i]
      if not path.endswith('/'):
        path += '/'
      path += '/'.join(p)

    # Add any additional query parameters to the query string
    if extra_params and len(extra_params) > 0:
      # Create the query string to go on the end of the URL, encoding all parameters as UTF-8
      extra_query = urllib.urlencode(dict([(k, self._Encode(v)) for k, v in parameters.items() if v is not None]))
      # Add it to the existing query
      if query:
        query += '&' + extra_query
      else:
        query = extra_query

    # Return the rebuilt URL
    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))


  def _DecompressGzippedResponse(self, response):
    raw_data = response.read()
    if response.headers.get('content-encoding', None) == 'gzip':
      url_data = gzip.GzipFile(fileobj=StringIO.StringIO(raw_data)).read()
    else:
      url_data = raw_data
    return url_data

  def _Encode(self, s):
    if self._input_encoding:
      return unicode(s, self._input_encoding).encode('utf-8')
    else:
      return unicode(s).encode('utf-8')

  def _UnicodeURLEncode(self, post_data):
    '''Return a string in key=value&key=value form

    Values are assumed to be encoded in the format specified by self._encoding,
    and are subsequently URL encoded.

    Args:
      post_data:
        A dict of (key, value) tuples, where value is encoded as
        specified by self._encoding

    Returns:
      A URL-encoded string in "key=value&key=value" form
    '''
    if post_data is None:
      return None
    else:
      data = dict((k, self._encode(v)) for k, v in post_data.iteritems() if v is not None)
      return urllib.urlencode(data)

  def _ParseAndCheckTwitter(self, json):
    """Try and parse the JSON returned from Twitter and return
    an empty dictionary if there is any error. This is a purely
    defensive check because during some Twitter network outages
    it will return an HTML failwhale page."""
    try:
      data = anyjson.deserialize(json)

      # Check for error fields in the data.
      if 'error' in data:
        raise Exception(data['error'])
      if 'errors' in data:
        raise Exception(data['errors'])

    except ValueError:
      if "<title>Twitter / Over capacity</title>" in json:
        raise Exception("Capacity Error")
      if "<title>Twitter / Error</title>" in json:
        raise Exception("Technical Error")
      print json
      raise Exception("json decoding")

    return data

  def FetchUrl(self,
                url,
                post_data=None,
                parameters=None,
                no_cache=None,
                use_gzip_compression=None):
    '''Fetch a URL, optionally caching for a specified time.

    Args:
      url:
        The URL to retrieve
      post_data:
        A dict of (str, unicode) key/value pairs.
        If set, POST will be used.
      parameters:
        A dict whose key/value pairs should encoded and added
        to the query string. [Optional]
      no_cache:
        If true, overrides the cache on the current request
      use_gzip_compression:
        If True, tells the server to gzip-compress the response.
        It does not apply to POST requests.
        Defaults to None, which will get the value to use from
        the instance variable self._use_gzip [Optional]

    Returns:
      A string containing the body of the response.
    '''
    # Build the extra parameters dict
    extra_params = {}
    if self._default_params:
      extra_params.update(self._default_params)
    if parameters:
      extra_params.update(parameters)

    if post_data:
      http_method = "POST"
    else:
      http_method = "GET"

    if self._debugHTTP:
      _debug = 1
    else:
      _debug = 0

    http_handler  = self._urllib.HTTPHandler(debuglevel=_debug)
    https_handler = self._urllib.HTTPSHandler(debuglevel=_debug)

    opener = self._urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)

    if use_gzip_compression is None:
      use_gzip = self._use_gzip
    else:
      use_gzip = use_gzip_compression

    # Set up compression
    if use_gzip and not post_data:
      opener.addheaders.append(('Accept-Encoding', 'gzip'))

    if self._oauth_consumer is not None:
      if post_data and http_method == "POST":
        parameters = post_data.copy()

      req = oauth.Request.from_consumer_and_token(self._oauth_consumer,
                                                  token=self._oauth_token,
                                                  http_method=http_method,
                                                  http_url=url, parameters=parameters)

      req.sign_request(self._signature_method_hmac_sha1, self._oauth_consumer, self._oauth_token)

      headers = req.to_header()

      if http_method == "POST":
        encoded_post_data = req.to_postdata()
      else:
        encoded_post_data = None
        url = req.to_url()
    else:
      url = self._BuildUrl(url, extra_params=extra_params)
      encoded_post_data = self._EncodePostData(post_data)

    # Open and return the URL immediately if we're not going to cache
    if encoded_post_data or no_cache or not self._cache or not self._cache_timeout:
      response = opener.open(url, encoded_post_data)
      url_data = self._DecompressGzippedResponse(response)
      opener.close()
    else:
      # Unique keys are a combination of the url and the oAuth Consumer Key
      if self._consumer_key:
        key = self._consumer_key + ':' + url
      else:
        key = url

      # See if it has been cached before
      last_cached = self._cache.GetCachedTime(key)

      # If the cached version is outdated then fetch another and store it
      if not last_cached or time.time() >= last_cached + self._cache_timeout:
        try:
          response = opener.open(url, encoded_post_data)
          url_data = self._DecompressGzippedResponse(response)
          self._cache.Set(key, url_data)
        except urllib2.HTTPError, e:
          print e
        opener.close()
      else:
        url_data = self._cache.Get(key)

    # Always return the latest version
    return self._ParseAndCheckTwitter(url_data)

  def PrefixURL(self, url):
    return '%s/%s.json' % (self.base_url, url)


  # def FetchURLBound(self,
  #               url,
  #               post_data=None,
  #               default_parameters=dict(),
  #               process_params=None,
  #               no_cache=None,
  #               use_gzip_compression=None, 
  #               process=None,
  #               **parameters):
  #   """Provides an extra argument to allow an endpoint to add default parameters
  #     when partially applying"""

  #   if not isinstance(post_data, dict):
  #     default_parameters["id"] = post_data # Not always ideal, but a sensible default.
  #     post_data = None

  #   if parameters:
  #     default_parameters.update(parameters)

  #   if process_params:
  #     default_parameters = dict(map(process_params, default_parameters.iteritems()))

  #   result = self.FetchUrl(url, post_data, default_parameters, no_cache, use_gzip_compression)

  #   if process:
  #     result = process(result)

  #   return result

  # def BindRequest(self, url, params = dict(), process = None, process_params = None):
  #   '''Uses partial application to bind a URL and some parameters.

  #   Calling the method will then respond with the API request, data processed
  #   according to the given function.'''
  #   url = '%s/%s.json' % (self.base_url, url)

  #   return partial(self.FetchURLBound, 
  #     url, default_parameters=params, 
  #     process=process, 
  #     process_params=process_params)

class _FileCacheError(Exception):
  '''Base exception class for FileCache related errors'''

class _FileCache(object):

  DEPTH = 3

  def __init__(self,root_directory=None):
    self._InitializeRootDirectory(root_directory)

  def Get(self,key):
    path = self._GetPath(key)
    if os.path.exists(path):
      return open(path).read()
    else:
      return None

  def Set(self,key,data):
    path = self._GetPath(key)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
      os.makedirs(directory)
    if not os.path.isdir(directory):
      raise _FileCacheError('%s exists but is not a directory' % directory)
    temp_fd, temp_path = tempfile.mkstemp()
    temp_fp = os.fdopen(temp_fd, 'w')
    temp_fp.write(data)
    temp_fp.close()
    if not path.startswith(self._root_directory):
      raise _FileCacheError('%s does not appear to live under %s' %
                            (path, self._root_directory))
    if os.path.exists(path):
      os.remove(path)
    os.rename(temp_path, path)

  def Remove(self,key):
    path = self._GetPath(key)
    if not path.startswith(self._root_directory):
      raise _FileCacheError('%s does not appear to live under %s' %
                            (path, self._root_directory ))
    if os.path.exists(path):
      os.remove(path)

  def GetCachedTime(self,key):
    path = self._GetPath(key)
    if os.path.exists(path):
      return os.path.getmtime(path)
    else:
      return None

  def _GetUsername(self):
    '''Attempt to find the username in a cross-platform fashion.'''
    try:
      return os.getenv('USER') or \
             os.getenv('LOGNAME') or \
             os.getenv('USERNAME') or \
             os.getlogin() or \
             'nobody'
    except (AttributeError, IOError, OSError), e:
      return 'nobody'

  def _GetTmpCachePath(self):
    username = self._GetUsername()
    cache_directory = 'python.cache_' + username
    return os.path.join(tempfile.gettempdir(), cache_directory)

  def _InitializeRootDirectory(self, root_directory):
    if not root_directory:
      root_directory = self._GetTmpCachePath()
    root_directory = os.path.abspath(root_directory)
    if not os.path.exists(root_directory):
      os.mkdir(root_directory)
    if not os.path.isdir(root_directory):
      raise _FileCacheError('%s exists but is not a directory' %
                            root_directory)
    self._root_directory = root_directory

  def _GetPath(self,key):
    try:
        hashed_key = md5(key).hexdigest()
    except TypeError:
        hashed_key = md5.new(key).hexdigest()

    return os.path.join(self._root_directory,
                        self._GetPrefix(hashed_key),
                        hashed_key)

  def _GetPrefix(self,hashed_key):
    return os.path.sep.join(hashed_key[0:_FileCache.DEPTH])
