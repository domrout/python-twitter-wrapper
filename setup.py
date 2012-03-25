#!/usr/bin/env python

from setuptools import setup

setup(name='TwitterWrapper',
      version='0.1',
      description='A slimmer wrapper to the Twitter API',
      author='Dominic Rout',
      author_email='d.rout@sheffield.ac.uk',
      url='http://staffwww.dcs.shef.ac.uk/people/D.Rout/',
      packages=['twitterwrapper'],
      scripts=['scripts/authenticate_twitter_cherrypy'],
      package_data={'twitterwrapper': ['*.yaml', 'defaults/*.yaml']},
      install_requires=["oauth2", "cherrypy", "pyyaml", "anyjson"]
     )