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

"""A connection to the Twitter API"""

from requests_oauthlib import OAuth1Session

def Connection(consumer_key, 
               consumer_secret, 
               access_token_key, 
               access_token_secret):
  """Simply wraps an OAuth1Session initialiser with the correct argument names.

    Purely for compatibility with the existing API"""

  return OAuth1Session(consumer_key,
                       client_secret=consumer_secret,
                       resource_owner_key=access_token_key,
                       resource_owner_secret=access_token_secret)
