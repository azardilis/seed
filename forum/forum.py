import webapp2
import jinja2
import os
import cgi
from google.appengine.api import mail
from model.base.Module import Module
from model.base.User import User
from model.base.YearCourseSemester import YearCourseSemester
from model.base.Lecturer import Lecturer
from model.base.Rating import Rating
from model.base.Subscription import Subscription
from google.appengine.ext.db import Key
from itertools import izip

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

global current_user

#Handles rendering of the signinpage and authorisation and if okay redirects to main page
class SignInPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())
    
    def post(self): #proper authorisation should go here
        global current_user
        q = User.all()
        q.filter('username',cgi.escape(self.request.get('user')))
        current_user = q.get()
        self.redirect("/main")

class MainPage(webapp2.RequestHandler):
    def get(self):
        #passing variables to template, namely the current user and the subs that need
        #to be displayed in the homepage
        homepage_subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        template_values = {
                           'current_user':current_user,
                           'subscriptions':homepage_subs
                           }
        template = jinja_environment.get_template('templates/signin.html')
        self.response.out.write(template.render(template_values))
        
class ForumPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/forum.html')
        self.response.out.write(template.render({}))

class AboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/about.html')
        self.response.out.write(template.render({}))
        
class NotesPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/notes.html')
        self.response.out.write(template.render({}))

class ContactPage(webapp2.RequestHandler):
    def get(self):
        subject=''
        message=''
        template = jinja_environment.get_template('templates/contact.html')
        template_values = {
                           subject:'subject',
                           message:'message'
                           }
        self.response.out.write(template.render(template_values))

class EmailSent(webapp2.RequestHandler):
    def post(self):
        self.request.get('subject')
        template = jinja_environment.get_template('templates/something.html')
        subject = self.response.write(self.request.get('subject'))
        message = self.response.write(self.request.get('message'))
        mail.send_mail(sender='alex.pana.oikonomou@gmail.com',#user google email
                       to='scriptingteamk@gmail.com',
                       subject=subject,
                       body=message)        
        self.response.out.write(template.render({}))


def reset_db():
    for user in User.all():
        user.delete()

    for ycs in YearCourseSemester.all():
        ycs.delete()

    for mod in Module.all():
        mod.delete()

    for sub in Subscription.all():
        sub.delete()
        
#function to populate the db at the start of the app,
#that is if you don't have your own copy locally
def populate_db():

    reset_db()

    current_user = User(key_name='az2g10', full_name='argyris', password='1234', course='cs', year=3)
    current_user.put()

    compsci11 = YearCourseSemester(year=int(1), semester=int(1), course='compsci')
    compsci11.put()
    compsci12 = YearCourseSemester(year=int(1), semester=int(2), course='compsci')
    compsci12.put()
    compsci21 = YearCourseSemester(year=int(2), semester=int(1), course='compsci')
    compsci21.put()
    compsci22 = YearCourseSemester(year=int(2), semester=int(2), course='compsci')
    compsci22.put()
    compsci31 = YearCourseSemester(year=int(3), semester=int(1), course='compsci')
    compsci31.put()
    compsci32 = YearCourseSemester(year=int(3), semester=int(2), course='compsci')
    compsci32.put()

    mod1 = Module(key_name='comp3001', code='comp3001', title='Scripting Languages',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3001/", semester=1,
                  yearCourseSemester=compsci31)
    mod1.put()
    mod2 = Module(key_name='comp3033', code='comp3033', title='Computational Biology',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3033/", semester=1,
                  yearCourseSemester=compsci31)
    mod2.put()
    mod3 = Module(key_name='comp3032', code='comp3032', title='Intelligent Algorithms',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3032/", semester=1,
                  yearCourseSemester=compsci31)
    mod3.put()

    sub1 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=mod1)
    sub2 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=mod2)
    sub3 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=mod3)
    sub1.put()
    sub2.put()
    sub3.put()


populate_db()
app = webapp2.WSGIApplication([
                                   ('/'     , SignInPage),
                                   ('/main' , MainPage),
                                   ('/forum', ForumPage),
                                   ('/about', AboutPage),
                                   ('/notes', NotesPage),
                                   ('/contact',ContactPage),
                                   ('/something',EmailSent)                                 
                                ], debug=True)
                               


    

