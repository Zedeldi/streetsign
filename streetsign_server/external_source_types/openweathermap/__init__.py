# -*- coding: utf-8 -*-
#  StreetSign Digital Signage Project
#     (C) Copyright 2013 Daniel Fairhead
#
#    StreetSign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StreetSign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.
#
#    ---------------------------
#
#    Implement weather icons here at some point
'''
    Get weather data from OpenWeatherMap

'''

__NAME__ = 'OpenWeatherMap'

__MODULE__ = 'owm'

import sys
import math
import requests

from flask import render_template_string, json
from jinja2 import Template
import feedparser
import bleach
from collections import defaultdict

import streetsign_server.post_types as post_types
from streetsign_server.models import Feed, Post
from streetsign_server.logic.feeds_and_posts import delete_post_and_run_callback
from streetsign_server.external_source_types import my
from streetsign_server import app

DEFAULT_TAGS = "span,b,i,u,em,img"

def receive(request):
    ''' get data from the admin, extract the data, and return the object we
        actually need to save. '''

    return {"city": request.form.get('city', ''),
            "api_key": request.form.get('api_key', ''),
            "display_template": request.form.get('display_template', '{}'),
            "current_posts": json.loads(request.form.get('current_posts', '[]')),
            "allowed_tags": request.form.get('allowed_tags', DEFAULT_TAGS),
            }

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'),
                                  default_tags=DEFAULT_TAGS, **data)

def get_temperature(city,api_key):
  base_url = 'http://api.openweathermap.org/data/2.5/weather'
  #api_key = app.config.get('OWM_API_KEY') # get API key from config
  query = base_url + '?q=%s&units=metric&APPID=%s' % (city, api_key)
  try:
    response = requests.get(query)
    # print("[%s] %s" % (response.status_code, response.url))
    if response.status_code != 200:
      response = 'N/A'
      return response
    else:
      weather_data = response.json()
      return weather_data
  except requests.exceptions.RequestException as error:
    print(error)
    sys.exit(1)

def test(data):
    True

def get_new(data):
    ''' ok, actually go get us some new posts, alright? (return new posts, and
        update data with any hidden fields updated that we need to
        (current_posts, for instance))'''

    new_posts = []

    location = get_temperature(data['city'],data['api_key'])

    for post in Post.select().where((Post.type == 'weather') & (str(data['city'] + ' - ') in Post.content) & (str('°C') in Post.content)):
      delete_post_and_run_callback(post, post_types.load(post.type))

    # Format output below using returned json, e.g. location['weather'][0]['description']
    new_posts.append({'type': 'weather', 'content': str(location['name'] + ' - ' + str(math.ceil(location['main']['temp'])) + '°C')})

    return new_posts
