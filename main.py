import os
import webapp2
import jinja2
import string
import re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#Database of blog posts
class Posts(db.Model):
    title = db.StringProperty(required = True)
    posttext = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def render_front(self, title="", posttext="", error=""):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, posttext=posttext, error=error, posts=posts)

    def get(self):
        self.render_front()
    
    def post(self):
        title = self.request.get("title")
        posttext = self.request.get("posttext")
        
        if title and posttext:
            a = posts(title = title, posttext = posttext)
            a.put()
            self.redirect("/")
            return
        else:
            error = "We need both a title and a blog post!"
            self.render_front(title, posttext, error)

#Bloghome - lists 5 most recent posts
class BlogHome(Handler):
    def render_blog(self, title="", posttext="", error=""):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 5")
        self.render("front.html", posts=posts)

    def get(self):
        self.render_blog()

#View (single) Post
class ViewPost(Handler):
    def get(self, id):
        idint = int(id)
        post = Posts.get_by_id(idint, parent=None)

        if not post:
            self.error(404)
            return

        self.render("viewpost.html", post = post)
    
#Newpost - form for submitting a new post
class NewPost(Handler):
    def render_postform(self, title="", posttext="", error=""):
        self.render("newpost.html", title=title, posttext=posttext, error=error)

    def get(self):
        self.render_postform()
    
    def post(self):
        title = self.request.get("title")
        posttext = self.request.get("posttext")
        if title and posttext:
            a = Posts(title = title, posttext = posttext)
            a.put()
            redirectlink = "/blog/" + str(a.key().id())
            self.redirect(redirectlink)
            return
        else:
            error = "We need both a title and a blog post!"
            self.render_postform(title, posttext, error)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogHome),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)
