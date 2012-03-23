#!/usr/bin/env python

from distutils.core import setup

setup(name='Twitter Wrapper',
      version='0.1',
      description='A slimmer wrapper to the Twitter API',
      author='Dominic Rout',
      author_email='d.rout@sheffield.ac.uk',
      url='http://staffwww.dcs.shef.ac.uk/people/D.Rout/',
      packages=['twitterwrapper'],
      scripts=['scripts/authenticate_twitter_cherrypy'],
      data_files=[('twitter', ["twitterwrapper/api.yaml"]),
      	('twitter/defaults', ["config.yaml", "access_tokens.yaml"])
      ],
      requires=["oauth2", "cherrypy", "pyyaml", "anyjson"]
     )