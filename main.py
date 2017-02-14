import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class PostList(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", blogposts="", error=""):
        postlist = db.GqlQuery("SELECT * FROM PostList ORDER BY created DESC")

        self.render("front.html", title=title, postlist=postlist, error=error)

    def get(self):
        self.render_front()
    
    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")
        
        if title and blogpost:
            a = Blogpost(title = title, post = post)
            a.put()
            self.redirect("/")

        else:
            error = "We need both a title and a blog post!"
            self.render_front(title, blogpost, error)


app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
