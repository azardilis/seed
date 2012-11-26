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
from model.base.Category import Category
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
	if 'current_user' not in globals():
        	template = jinja_environment.get_template('templates/index.html')
       		self.response.out.write(template.render())
	else:
		self.redirect("/main")

    
    def post(self): #authenticate the user
        global current_user
<<<<<<< HEAD
        q = User.all()
	q.filter('__key__ =', Key.from_path('User', cgi.escape(self.request.get('user'))))
	current_user = q.get()
	if current_user :
		self.response.write(current_user.username)
	else : 
		self.redirect("/")

        #self.redirect("/main")
=======
	potential_user=User.get_by_key_name(cgi.escape(self.request.get('user')))
	if potential_user is not None and potential_user.password==self.request.get('password'):
		current_user=potential_user
        	self.redirect("/main")
	else:	
		#proper error message should be displayed (some javascript or something)
		print "The username and password do not match, please try again!"
>>>>>>> e8cb4902d0ad4850fc3952620f6325bff83c6b46

class MainPage(webapp2.RequestHandler):
    def get(self):
        #passing variables to template, namely the current user and the subs that need
        #to be displayed in the homepage

	global current_user
	if 'current_user' in globals():        
		homepage_subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        	template_values = {
                           'current_user':current_user,
                           'subscriptions':homepage_subs
                           	}
        	template = jinja_environment.get_template('templates/signin.html')
        	self.response.out.write(template.render(template_values))
	else:
		self.redirect("/")
        
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

    ###### RESET #######
    reset_db()

    ###### POPULATE ######
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
    mjw = Lecturer(key_name='mjw', full_name='Mark J Weal', home_page='http://google.com')
    mjw.put()
    apb = Lecturer(key_name='apb', full_name='Adam Prugel-Bennett', home_page='http://google.com')
    apb.put()
    mn = Lecturer(key_name='mn', full_name='Mahesan Niranjan', home_page='http://google.com')
    mn.put()
    mp3 = Lecturer(key_name='mp3', full_name='Maria Polukarov', home_page='http://google.com')
    mp3.put()
    msn = Lecturer(key_name='msn', full_name='Mark S Nixon', home_page='http://google.com')
    msn.put()
    srg = Lecturer(key_name='srg', full_name='Steve R Gunn', home_page='http://google.com')
    srg.put()
    bim = Lecturer(key_name='bim', full_name='B Iain McNally', home_page='http://google.com')
    bim.put()
    mrp2 = Lecturer(key_name='mrp2', full_name='Michael R. Poppleton', home_page='http://google.com')
    mrp2.put()
    srinanda = Lecturer(key_name='srinanda', full_name='Srinandan Dasmahapatra', home_page='http://google.com')
    srinanda.put()
    lac = Lecturer(key_name='lac', full_name='Leslie Carr', home_page='http://google.com')
    lac.put()
    nmg = Lecturer(key_name='nmg', full_name='Nicholas Gibbins', home_page='http://google.com')
    nmg.put()
    
    #both ejz
    Rating(lecturer=ejz,module=comp3001).put()
    Rating(lecturer=ejz,module=info3005).put()
    #both comp3016
    Rating(lecturer=nmg,module=comp3016).put()
    Rating(lecturer=lac,module=comp3016).put()

    ###### FORUM #######
    categGeneral3001 = Category(name='General Discussion', description='blah blah', module=comp3001)
    categGeneral3001.put()
    categCoursework3001 = Category(name='Coursework Discussion', description='blah blah', module=comp3001)
    categCoursework3001.put()
    
    ## TODO ##
    #make Post to inherit from PolyModel and Thread inherit from Post
    #import Post and Thread classes in this file (look at other imports)
    #create Thread called thread1 making its category=categGeneral3001
    #create Post called t1reply1 making its post=thread1
    #create Post called t1reply1_1 making its post=t1reply1
    #create Post called t1reply1_1_1 making its post=t1reply1_1
    #create Post called t1reply2 making its post=thread1
    #create Thread called thread2 making its category=categGeneral3001 again

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
                               


    

