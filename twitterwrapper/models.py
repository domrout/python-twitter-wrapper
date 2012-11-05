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

      if hasattr(v, "to_dict"):
        v = v.to_dict()

      result[k] = v

    return result

class User(_ApiModel):  
  def custom_attrs(self):
    return {"status": Status}

class SearchResult(_ApiModel):  
  def custom_attrs(self):
    return {"results": partial(map, partial(Status, api=self.api))}

  def __repr__(self):
    return "<Search '%s' %d results>" % (self.query, len(self.results))
class Status(_ApiModel):  
  def custom_attrs(self):
    return {"user": User,
    "entities": Entities
    }
  def __repr__(self):
    if hasattr(self, "user"):
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


