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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

global current_user


class SignInPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/index.html')
        
        self.response.out.write(template.render())
    
    def post(self):
        global current_user
        
        #checking if the typed in username is actually in the database, and retrieving the user object
        #This needs to be implemented as a proper login function, I have only done the basic, so we can have our global current user variable
        q = User.all()
        q.filter('username',cgi.escape(self.request.get('user')))
        
        current_user = q.get()
        
        self.redirect("/main")
        
        

class MainPage(webapp2.RequestHandler):
    def get(self):
        #building query to get only the current user's modules
        q= Subscription.all().filter('subscribed_user',current_user).filter('show_in_homepage',True)
        q=q.run()
  
        #passing variables to template
        template_values = {
                           
                           'user':current_user,
                           'query':q
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
        #mail.send_mail(sender='alex.pana.oikonomou@gmail.com',
         #         to='ao2g10@soton.ac.uk',
          #        subject='asddsa',
           #       body='asdad')
        
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

















app = webapp2.WSGIApplication([
                                   ('/'     , SignInPage),
                                   ('/main' , MainPage),
                                   ('/forum', ForumPage),
                                   ('/about', AboutPage),
                                   ('/notes', NotesPage),
                                   ('/contact',ContactPage),
                                   ('/something',EmailSent)                                 
                                ], debug=True)
                               


    

