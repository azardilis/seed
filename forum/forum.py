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
from model.base.Assessment import Assessment
from model.base.Grade import Grade
from model.base.Subscription import Subscription
from google.appengine.ext.db import Key
from google.appengine.ext import db
from itertools import izip
from datetime import datetime

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

    comp3001 = Module(key_name='comp3001', title='Scripting Languages',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3001/",
                  yearCourseSemester=compsci31)
    comp3001.put()
    comp3033 = Module(key_name='comp3033', title='Computational Biology',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3033/",
                  yearCourseSemester=compsci31)
    comp3033.put()
    comp3032 = Module(key_name='comp3032', title='Intelligent Algorithms',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3032/",
                  yearCourseSemester=compsci31)
    comp3032.put()
    comp3016 = Module(key_name='comp3016', title='Hypertext and Web Technologies', 
                  ecs_page='http://www.google.com', 
                  yearCourseSemester=compsci31)
    comp3016.put()
    comp3020 = Module(key_name='comp3020', title='Individual Project', 
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31)
    comp3020.put()
    info3005 = Module(key_name='info3005', title='Security & Information Technology', 
                  ecs_page='http://www.google.com', 
                  yearCourseSemester=compsci31)
    info3005.put()

    sub1 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=comp3001)
    sub2 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=info3005)
    sub3 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=comp3016)
    sub1.put()
    sub2.put()
    sub3.put()

    assesCwk3001 = Assessment(title='perl assignment',
                        dueDate=datetime.strptime('Nov 1 2005  1:33PM', '%b %d %Y %I:%M%p'), 
                        specLink=db.Link("http://www.google.com/"), 
                        handin=db.Link("http://www.google.com/"), 
                        module=comp3001)
    assesCwk3001.put()
    assesCwk3005 = Assessment(title='security assignment 2',
                        dueDate=datetime.strptime('Nov 1 2005  1:33PM', '%b %d %Y %I:%M%p'), 
                        specLink=db.Link("http://www.google.com/"), 
                        handin=db.Link("http://www.google.com/"), 
                        module=comp3001)
    assesCwk3005.put()

    grade1 = Grade(student=current_user, assessment=assesCwk3001, mark=100)
    grade1.put()

    ejz = Lecturer(key_name='ejz', full_name='Ed J Zaluska', home_page='http://google.com')
    ejz.put()

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
                               


    

