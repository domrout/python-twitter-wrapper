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
  Dynamically generated API for Twitter.

  Methods are described in api.yaml
  The call structure should roughly match https://dev.twitter.com/docs/api

"""

from functools import partial
from contextlib import closing
from _connection import Connection
from access_tokens import config_connection
import anyjson, yaml, string, models, os, sys
from copy import copy
from _utils import *

class _ApiMethodSpec(object):
  def __init__(self,
      method,
      url = None, 
      doc = None,
      model = None, 
      contains = dict(), 
      default_param = None,
      example_params = None,
      container_id = None,
      default = None, 
      post = False
    ):

    self.method   = method     
    self.url  = url          
    self.doc   = doc          
    self.model  =  model        
    self.default_param   = default_param
    self.container_id  = container_id 
    self.post = post
    self.initialize_model()

    self.contains = list()

    for name, structure in contains.iteritems():
      self.add_child(name, structure)

  def initialize_model(self):
    if isinstance(self.model, str):
      if self.model == "None":
        self.model = None 
      else:
        self.model = getattr(models, self.model)

  def add_child(self, method, structure):
    parent_structure = {
      "doc": self.doc,
      "model": self.model
    }

    structure["method"] = method

    parent_structure.update(structure)

    self.contains.append(_ApiMethodSpec(**parent_structure))


class ApiMethod(object):
  """A method representing a part of the Twitter API.

    Some methods are callable, just use methodname().

    Methods can also be nested arbitrarily. For more information see 
      Api  
      api.yaml
      https://dev.twitter.com/docs/api
  """
  def __init__(self, 
      connection, 
      api,
      spec, 
      container = None):
    self._api = api # needed to bless objects
    self._connection = connection

    self._spec = spec

    self.__doc__ = spec.doc
    self._container = container

    # Instantiate all contained specifications
    for spec in spec.contains:
      setattr(self, spec.method, ApiMethod(connection, api, spec, container))

  def _process_result(self, result):
    if isinstance(result, dict) and "previous_cursor" in result:
      return models.ResultsPage(result, self._api)

    if self._spec.model == None:
      return result
    else:     
      if isinstance(result, list):
        return [self._spec.model(r, self._api) for r in result]
      else:
        return self._spec.model(result, self._api)

  def _prepare_url(self, params):
    url = self.url()

    # Combine my parent with the parameters for string substitution.
    p = copy(params)
    if self._container:
      p.update(self._container.__dict__)

    url = url % p
	
    
    return self._connection.PrefixURL(url)
  
  def url(self):
    return self._spec.url

  def _model(self):
    return self._spec.model

  def __call__(self, default = None, **params):
    """
      Make the specified call to the Twitter API.
    """
    # Options that will be used during execution
    spec = self._spec

    if spec.url is None:
      raise TypeError("API method is not callable")
    else:      
      # Place the default option into params properly.
      if default and spec.default_param:
        params[spec.default_param] = default

      # Allow an ID to be specified by the containing class.
      if self._container and spec.container_id:
        params[spec.container_id] = self._container.id

      if spec.post:
        result = self._connection.FetchUrl(
          self._prepare_url(params), 
          post_data=params)
      else:
        result = self._connection.FetchUrl(
          self._prepare_url(params), 
          parameters=params)

      return self._process_result(result)

  def __repr__(self):
    if self._spec.url:
      return "<ApiMethod:%s URL:%s>" % (self._spec.method, self._spec.url)
    else:
      return "<ApiMethod:%s (NOT CALLABLE)>" % (self._spec.method)


class Api(object):
  """An instance of the Twitter API bound to a specific connection.

    The structure of the API calls available closely matches that provided by Twitter at:
      https://dev.twitter.com/docs/api

    For example, with an Api object called "api", to access 'statuses/home_timeline' call:

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
  """
  def __init__(self, connection=None, specification = None):
    self._model_apis = {}

    connection = connection if connection else config_connection()

    if specification == None:
      with closing(open_data("api.yaml")) as f:
        specification = yaml.load(f)

    self._connection = connection

    # Now look through all immediate attributes
    for attribute, value in specification.iteritems():
      if hasattr(models, attribute):
        # The element matches a model object, so it will be used to bless objects of that type.
        target_class = getattr(models, attribute)
        self._model_apis[target_class] = dict()

        # Instantiate the specificatons for all the relevant methods
        for inner_attribute, inner_value in value.iteritems():
          inner_value["method"] = inner_attribute
          self._model_apis[target_class][inner_attribute] = _ApiMethodSpec(**inner_value)
      else:
        # Otherwise, add it to the tree of API calls.
        value["method"] = attribute
        setattr(self, attribute, ApiMethod(self._connection, self, _ApiMethodSpec(**value)))

  def _bless(self, target):
    """Will 'bless' an object with any API calls matching its class"""
    if target.__class__ in self._model_apis:
      for method, method_spec in self._model_apis[target.__class__].iteritems():
        api_object = ApiMethod(self._connection, self, method_spec, target)
        setattr(target, method, api_object)

    return target
