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

"""Exceptions which may be created by the Twitter API"""

import requests

class TwitterException(Exception):
	def __init__(self, message, code):
		self.message = message
		self.code = code

	def __str__(self):
		return "Error %d: %s" % (self.code, self.message)

	@staticmethod
	def raise_for_response(result):
		"""Inspects the given result and raises an exception if needed"""
		# Don't do anything if we have the right status code.
		if result.status_code != 200:
			try: 
				result_json = result.json()
				if "errors" in result_json:
					for error in result_json["errors"]:
						raise TwitterException(**error)

			except ValueError:
				# Back off to just raising the error for the request.
				result.raise_for_response()

