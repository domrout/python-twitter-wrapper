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

"""Provides empty classes for the twitter data models"""

import urlparse, urllib, anyjson, sys
from twitter_exception import StreamDisconnectException
from functools import partial
import oauth2 as oauth


class _ApiModel(object):
  """Base class for a model which can be used to contain twitter data.

    Models are not generally specified in full but can instead be instantiated with 
      whatever data is available.
  """
  def __init__(self, data = dict(), api = None, **params):
    data.update(params)

    if api:
      api._bless(self)
    self.api = api
    custom_attrs = self.custom_attrs()

    self.creation_attrs = set()

    for attribute, value in data.iteritems():
      if attribute in custom_attrs:
        constructor = custom_attrs[attribute] 
        setattr(self, attribute, constructor(value))
      else:
        setattr(self, attribute, value)

      self.creation_attrs.add(attribute)


  def custom_attrs(self):
    """A function to return a dictionary of 'custom attributes'. 
      These attributes are handled specially and are usually needed to instantiate 
      inner models.
    """
    return dict()

  def to_dict(self):
    """Returns a version of the object containing the same attrs as
      were used to create it, suitable for outputting to JSON."""
    result = dict()

    for k in self.creation_attrs:
      v = getattr(self, k)

      def transform(v):
        if hasattr(v, "to_dict"):
          v = v.to_dict()

        if hasattr(v, "iteritems"):
          v = dict((a, transform(b)) for (a, b) in v.iteritems())
        elif hasattr(v, "__iter__"):
          v = [transform(w) for w in v]

        return v

      result[k] = transform(v)

    return result

  def __repr__(self):
    attr_str = [a + ":" + repr(v) for a, v in self.creation_attrs.iteritems()]
    attr_str = [a for a in attr_str if a < 140]
    attr_str = ", ".join(attr_str)

    return "<%s %s>" % (self.__class__.__name__, attr_str)

class User(_ApiModel):  
  def custom_attrs(self):
    return {"status": Status}

class SearchResult(_ApiModel):  
  def custom_attrs(self):
     return {"statuses": partial(map, partial(Status, api=self.api))}
     
  @property
  def results(self):
    # For version 1.1 compatibilitiy
    return self.statuses

  def __repr__(self):
    return "<Search with %d results>" % len(self.statuses)

class Status(_ApiModel):  
  def __init__(self, data = dict(), api = None, **params):
    self.delete = None
    super(Status, self).__init__(data, api, **params)

  def custom_attrs(self):
    return {"user": User,
      "entities": Entities,
      "delete": lambda x: Status(x["status"])
    }

  def __repr__(self):
    if self.delete:
      result =  "<Status DELETION %s>" % (self.delete.id_str)
    elif hasattr(self, "user"):
      result =  "<Status @%s '%s'>" % (self.user.screen_name, self.text[:50] + "..." if len(self.text) > 50 else self.text)
    elif hasattr(self, "from_user"):
      result =  "<Status @%s '%s'>" % (self.from_user, self.text[:50] + "..." if len(self.text) > 50 else self.text)
    else:
      result =  "<Status '%s'>" % (self.text[:50] + "..." if len(self.text) > 50 else self.text)

    return result.encode("ascii", errors="replace")

class Entities(_ApiModel):
  class Media(_ApiModel):
    pass

  class Url(_ApiModel):
    pass

  class UserMention(_ApiModel):
    pass

  class HashTag(_ApiModel):
    pass

  def custom_attrs(self):
    return {
      "media": lambda xs: [self.Media(x, self.api) for x in xs],
      "urls": lambda xs: [self.Url(x, self.api) for x in xs],
      "user_mentions": lambda xs: [self.UserMention(x, self.api) for x in xs],
      "hashtags": lambda xs: [self.HashTag(x, self.api) for x in xs]
      }

class SuggestionCategory(_ApiModel):
  pass

class List(_ApiModel):
  def custom_attrs(self):
    return {"user": User}

 
class ResultsPage(_ApiModel):
  def custom_attrs(self):
    return {
      "users": partial(map, partial(User, api=self.api)),
      "lists": partial(map, partial(List, api=self.api))}

class LimitStatus(_ApiModel):
  pass

class DirectMessage(_ApiModel):
  def __repr__(self):
    result =  "<DirectMessage @%s -> @%s '%s'>" % (self.sender.screen_name, 
      self.recipient.screen_name, 
      self.text[:50] + "..." if len(self.text) > 50 else self.text)

    return result.encode("ascii", errors="replace")
  def custom_attrs(self):
    return {
      "sender": User,
      "recipient": User}

class StreamingCommands(_ApiModel):
  """Superclass for streaming commands.
    Purely exists to make life easier for the consumer"""
  pass

class StatusDeletion(StreamingCommands):
  def __init__(self, data = dict(), api = None, **params):
    super(StatusDeletion, self).__init__(data["status"], api, **params)

class GeoDeletion(StreamingCommands):
  pass

class Limit(StreamingCommands):
  pass

class StatusWithheld(StreamingCommands):
  pass

class UserWithheld(StreamingCommands):
  pass

class SteamWarning(StreamingCommands):
  pass

class Event(StreamingCommands):
  pass


def streaming_selector(result, api = None, **params):
  """Selects from the possible models that can be generated by a stream"""
  classes = {"delete": StatusDeletion,
             "scrub_geo": GeoDeletion,
             "limit": Limit,
             "status_withheld": StatusWithheld,
             "user_withheld": UserWithheld,
             "disconnect": StreamDisconnectException.raise_for_response,
             "warning": SteamWarning,
             "friends": lambda x, y: x,
             "friends_str": lambda x, y: x,
             "event": Event,
             "sender": DirectMessage
            }

  matched_classes = set(result.keys()) & set(classes.keys())

  for key in matched_classes:
    return classes[key](result[key], api, **params)
  return Status(result, api, **params)

