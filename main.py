#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import os
import webapp2
import jinja2
import re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
  """docstring for Handler"""
  def write(self, *a, **kw):
    self.response.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **params):
    self.write(self.render_str(template, **params))


class Blog(db.Model):
  subject = db.StringProperty(required=True)
  blog = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)


class MainHandler(Handler):
    def get(self):
      blog = db.GqlQuery("SELECT * FROM Blog "
                      "ORDER BY created DESC")
      self.render("home.html", blog=blog)


class NewPostHandler(Handler):
  def render_front(self, subject="", blog="", errors=""):
    self.render('newpost.html', subject=subject, blog=blog, errors=errors)

  def get(self):
    self.render_front()

  def post(self):
    subject = self.request.get("subject")
    blog = self.request.get("blog")

    if subject and blog:
      entry = Blog(subject = subject, blog = blog)
      entry.put()

      self.redirect('/%s' % str(entry.key().id()))
    else:
      error = "Insert both subject and content please"
      self.render_front(subject, blog, error)


class PermalinkHandler(Handler):
  def get(self, entry_id):
      entry = Blog.get_by_id(int(entry_id))
      if entry:
        self.render("single_entry.html", subject=entry.subject, blog=entry.blog, error="")
      else:
        self.render("single_entery.html", subject="", body="", error="Blog post %s not found" % entry_id)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPostHandler),
    ('/(\d+)', PermalinkHandler)
], debug=True)
