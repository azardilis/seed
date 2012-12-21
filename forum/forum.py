import webapp2
import jinja2
#imported for debugging reasons
import logging
from functions.RetrieveFunctions import *
import os
import cgi
from google.appengine.api import mail
from model.base.Module import Module
from functions.ForumFunctions import * # functions to handle posts and shit
from model.base.User import User
from model.base.Post import Post
from model.base.Thread import Thread
from model.base.Vote import Vote
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
import PyRSS2Gen

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

global current_user

class rss_item:
    def __init__(self, title, link, description, category, pub_date):
        self.title = title
        self.link = link
        self.description = description
	self.category = category
        self.pub_date = pub_date	
	
	
def cloneEntity(e, **extra_args):

	klass = e.__class__
	props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
	props.update(extra_args)
	return klass(**props)
	
def getYcsFromCode(code):
	course=code.split('-')[1]
	year=code.split('-')[2]
	semester=code.split('-')[3]

def getYCS(year, course, semester):
    ycs_list = YearCourseSemester.all()
    ycs_list.filter('year =', year)
    ycs_list.filter('course =', course)
    ycs_list.filter('semester =', semester)
    ycs = ycs_list.get()
    return ycs.modules

#Main administration page
class AdminPage(webapp2.RequestHandler):
    def get(self):
        #passing variables to template
        global current_user
        if 'current_user' in globals() and current_user.user_type=='moderator':
			
            template_values = {
				'current_user':current_user
			}
            template = jinja_environment.get_template('templates/admin.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/")
			
#Modules administration page
class AdminModules(webapp2.RequestHandler):
    def get(self):
        #passing variables to template
		global current_user
		firsthalf=[]
		secondhalf=[]
		allYcsArray=[]
		if 'current_user' in globals() and current_user.user_type=='moderator':
				modules=Module.all().run()
				allYcs=YearCourseSemester.all().run()
				count=Module.all().count()
				#splitting the modules array in half to be able to display it nicely on two columns in the template
				i=1
				if count%2 is 0:
					for module in modules:
						if i<=count/2:
							firsthalf.append(module)
						else:
							secondhalf.append(module)
						i=i+1
				else:
					for module in modules:
						if i<=count/2+1:
							firsthalf.append(module)
						else:
							secondhalf.append(module)
						i=i+1
				#copying allYcs into an array to be able to use it properly in the template
				for ycs in allYcs:
					allYcsArray.append(ycs)
				template_values = {
					'current_user':current_user,
					'firsthalf':firsthalf,
					'secondhalf':secondhalf,
					'allYcs':allYcsArray
				}
				template = jinja_environment.get_template('templates/admin-modules.html')
				self.response.out.write(template.render(template_values))
		else:
				self.redirect("/")
    def post(self):
		global current_user
		if 'current_user' in globals() and current_user.user_type=='moderator':
			is_delete = self.request.POST.get('remove_module_button', None)
			is_apply = self.request.POST.get('apply_button', None)
			is_add = self.request.POST.get('add_button', None)
			if is_apply:
				#get the module object from the datastore
				moduleObject=Module.get(cgi.escape(self.request.get('module_key')))
				if cgi.escape(self.request.get('module_title')) is not None:
					moduleObject.title=cgi.escape(self.request.get('module_title'))
				if cgi.escape(self.request.get('module_code')) is not None:
					moduleObject.ecs_page=cgi.escape(self.request.get('module_page'))
				if cgi.escape(self.request.get('ycs')) is not None:
					ycs=cgi.escape(self.request.get('ycs'))
					#get the course, year and semester out of the value that comes in
					course=ycs.split('-')[0]
					year=ycs.split('-')[1]
					semester=ycs.split('-')[2]
					#get all YCS values and then filter to get only the right one
					ycs_list = YearCourseSemester.all()
					ycs_list.filter('year =', int(year))
					ycs_list.filter('course =', course)
					ycs_list.filter('semester =', int(semester))
					ycs=ycs_list.get()
					moduleObject.yearCourseSemester=ycs
				moduleObject.put()
			if is_delete:
				#get the module object from the datastore
				moduleObject=Module.get(cgi.escape(self.request.get('module_key')))
				moduleObject.delete()
			if is_add:
				if cgi.escape(self.request.get('ycs')) is not None and cgi.escape(self.request.get('module_code')) is not None and cgi.escape(self.request.get('module_title')) is not None:
					ycs=cgi.escape(self.request.get('ycs'))
					#get the course, year and semester out of the value that comes in
					course=ycs.split('-')[0]
					year=ycs.split('-')[1]
					semester=ycs.split('-')[2]
					#get all YCS values and then filter to get only the right one
					ycs_list = YearCourseSemester.all()
					ycs_list.filter('year =', int(year))
					ycs_list.filter('course =', course)
					ycs_list.filter('semester =', int(semester))
					ycs=ycs_list.get()
					
					moduleObject=Module(key_name=cgi.escape(self.request.get('module_code')),
										title=cgi.escape(self.request.get('module_title')),
										ecs_page=cgi.escape(self.request.get('module_page')), 
										yearCourseSemester=ycs
										)
				
				moduleObject.put()
			template_values = {
						'current_user':current_user,
						'message':"The changes have been successfully submited to the datastore"
					}
			template = jinja_environment.get_template('templates/message-page.html')
			self.response.out.write(template.render(template_values))
				
			
		else:
			#proper error message should be displayed (some javascript or something)
			self.redirect("/")
		
#Existing user accounts administration page
class AdminUsers(webapp2.RequestHandler):
    def get(self):
        #passing variables to template
		global current_user
		if 'current_user' in globals() and current_user.user_type=='moderator':
				template_values = {
					'current_user':current_user
				}
				template = jinja_environment.get_template('templates/admin-users.html')
				self.response.out.write(template.render(template_values))
		else:
				self.redirect("/")

#Admin user creation page
class AdminUserCreation(webapp2.RequestHandler):
    def get(self):
        #passing variables to template
		global current_user
		if 'current_user' in globals() and current_user.user_type=='moderator':
				template_values = {
					'current_user':current_user
				}
				template = jinja_environment.get_template('templates/admin-user-creation.html')
				self.response.out.write(template.render(template_values))
		else:
				self.redirect("/")

#Handles rendering of the signinpage and authorisation and if okay redirects to main page
class SignInPage(webapp2.RequestHandler):
    def get(self):
        if 'current_user' not in globals():
            template = jinja_environment.get_template('templates/signin.html')
            self.response.out.write(template.render())
        else:
            self.redirect("/main")


    def post(self): #authenticate the user
        global current_user
        potential_user=User.get_by_key_name(cgi.escape(self.request.get('user')))
        if potential_user is not None and potential_user.password==self.request.get('password'):
            current_user=potential_user
            self.redirect("/main")
        else:
            #proper error message should be displayed (some javascript or something)
            print "The username and password do not match, please try again!"

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
            template = jinja_environment.get_template('templates/index.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/")

class ForumPage(webapp2.RequestHandler):
	
    	def get(self):
		sub_to_delete=cgi.escape(self.request.get('mod'))
		template = jinja_environment.get_template('templates/forum_subscriptions.html')
		subs = 	current_user.subscriptions
		
		if not sub_to_delete is '':
			subs.filter("__key__",Key(sub_to_delete))
			subs.get().delete()
			subs = 	current_user.subscriptions
		
		mod_info=[]
		lecturers=[]
	

		for s in subs:
			ratQ=Rating.all()
			ratQ.filter("module",s.module)
			for rat in ratQ:
				lectQ=Lecturer.all()
				lectQ.filter("__key__",rat.lecturer.key())
				lec=lectQ.get()
				lecturers.append(lec)
			mod_info.append(ModuleInfo(s.key(),s.module.key().name(),s.module.title,lecturers))
			lecturers=[]

		template_params = {
			'mod_info':mod_info
		}
        	self.response.out.write(template.render(template_params))	

class CategoriesPage(webapp2.RequestHandler):
    def get(self) : 
    	mcode = self.request.get('mid')
	if not mcode is '' :
            template = jinja_environment.get_template('templates/forum_categories.html')
	    module = retrieve_module_name(mcode)

            categs = module.categories
            complete = list()

            for c in categs :
                ct = c.threads.order('-timestamp').fetch(2) #just to limit what is fetched, later change to 10
                l = [c,ct]
                complete.append(l)

            template_values= {
                    'complete' : complete,
                    'ratings' : module.lecturers,
                    'subscribed' : module.student_count,
                    'assessments' : module.assessments,
                    'module' : module
            }

            self.response.out.write(template.render(template_values))

        else :
		logging.error('module code was empty ')
class ThreadPage(webapp2.RequestHandler):
    def get(self):
        t =retrieve_thread(self.request.get('tid'))
        if t :
            template = jinja_environment.get_template('templates/forum_thread.html')

            l1p = get_posts(int(cgi.escape(self.request.get('tid'))))
            posts = ''
            posts = get_children(l1p,posts,1,(t.poster.key() == current_user.key()),current_user)

            template_params = {
	    	    'user' : t.poster,
		    'nop': len([p for p in t.poster.posts]),
                    'thread': t ,
                    'posts' : posts
            }
            self.response.out.write(template.render(template_params))
        else :
            self.response.out.write('Unable to find thread '+str(self.request.get('ti'))+'<')

class ViewAllThreadsPage(webapp2.RequestHandler):
    def get(self):
        category = retrieve_category(self.request.get('cid'))

        if category :
            threads = category.threads.order('-timestamp')
            template_vars = {
                    'category' : category,
                    'threads':threads
            }
            template = jinja_environment.get_template('templates/forum_category_all.html')
            self.response.out.write(template.render(template_vars))
        else :
            logging.error('no category found '+str(cid))
            self.response.out.write('Couldn\'t get category')

class NewThread(webapp2.RequestHandler):
    def get(self):
        cid = cgi.escape(self.request.get('catid'))
        template = jinja_environment.get_template('templates/newthread.html')

        if cid :
            template_params = {
                    'cid' : cid
            }
            self.response.out.write(template.render(template_params))
        else : logging.error('newthread : empty cid >'+str(cid)+'<')

class CreateNewThread(webapp2.RequestHandler):
    def post(self):
        bd = cgi.escape(self.request.get('body'))
        sbj = cgi.escape(self.request.get('subject'))
        tgs = cgi.escape(self.request.get('tags'))

        cat = retrieve_category(self.request.get('cid'))

        if cat :
            t = Thread(category = cat,poster=current_user, tags=tgs.split(','),subject=sbj,body =bd )
            t.put()
            self.redirect('/showthread?tid='+str(t.key().id()))

        else :
            self.response.out.write('category not found')

class ReplyToThread(webapp2.RequestHandler):
    def post(self):
        thrd = retrieve_thread(self.request.get('tid'))

        if thrd :
            bd = cgi.escape(self.request.get('bd'))
            sbj = cgi.escape(self.request.get('sbj'))

            p = Post(body=bd, thread = thrd, poster = current_user)
            p.put()

            self.response.out.write(serialize_ajax_info(current_user,p,''))
        else :
            self.response.out.write('Thread not found')
            logging.error('Thread not found, tid : '+str(tid)+'<')

class ReplyToPost(webapp2.RequestHandler):
    def post(self):
        pst =retrieve_post(self.request.get('r2pid'))
        if pst :
            bd = cgi.escape(self.request.get('bd'))
            p = Post(reply=pst,poster=current_user,body=bd)
            p.put()
            self.response.out.write(serialize_ajax_info(current_user, p,str(pst.key().id())))
        else :
            self.response.out.write('Could not reply')
            logging.error('Couldnt find post, pid : '+pid+'<')

class VoteUpPost(webapp2.RequestHandler):
    def post(self):
        pst =retrieve_post(self.request.get('pid'))

        if pst and not (pst.key() in [v.post.key() for v in current_user.votes]):
            pst.votes = pst.votes +1
            pst.put()
            v = Vote(user=current_user,post=pst,value=1)
            v.put()
            self.response.out.write(pst.votes)
        else :
            self.response.out.write('Didn\'t vote up')
            logging.error('unable to vote up post pid '+self.request.get('pid')+'<')


class VoteDownPost(webapp2.RequestHandler):
    def post(self):
        pst = retrieve_post(self.request.get('pid'))

        if pst and not (pst.key() in [v.post.key() for v in current_user.votes]):
            pst.votes = pst.votes-1
            pst.put()
            v = Vote(user=current_user,post=pst,value=-1)
            v.put()
            self.response.out.write(pst.votes)
        else :
            self.response.out.write('Didn\'t vote down')
            logging.error('unable to vote down pid '+self.request.get('pid')+'<')

class ToggleSolution(webapp2.RequestHandler) :
    def post(self):
        thrd = retrieve_thread(self.request.get('tid'))
        pst = retrieve_post(self.request.get('pid'))
        if thrd and pst  :
            if str(thrd.poster.key()) == str(current_user.key())  and (pst.key() in [p.key() for p in thrd.posts]):

                for ps in thrd.posts: #reset all current answers
                    if not (ps.key() is pst.key()) :
                        ps.answer = False
                        ps.put()

                pst.answer = not pst.answer
                pst.put()
                self.response.out.write('ok')
                logging.info('toggled state')
            else :
                self.response.out.write('Failing checks')
                logging.error('curr_user_k :'+str(current_user.key())+', poster_k:'+str(thrd.poster.key())+', post in thrd.posts = '+(pst.key() in [p.key() for p in thrd.posts]) )
        else :
            logging.error('Unable to find thread or post')

'''Uses User Key to query the right User Entity'''
class ProfilePage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/profile.html')
        user_key = current_user.key()
        userQ=User.all()
        userQ=userQ.filter('__key__ = ' ,user_key)
        user = userQ.get()

        subsQ = Subscription.all()
        subsQ=subsQ.filter('subscribed_user',user.key())
        template_values={
                        'user':user,
                        'subscriptions':subsQ
                        }
        self.response.out.write(template.render(template_values))

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

class ModuleInfo:
	def __init__(self,sub_key,sub_code,sub_name,mod_lecturers):
		self.sub_key=sub_key
		self.sub_code=sub_code
		self.sub_name=sub_name
		self.mod_lecturers=mod_lecturers
class ModulesPage(webapp2.RequestHandler):
    def get(self):
        course = "compsci"
        y1s1 = getYCS(1, course, 1)
        y1s2 = getYCS(1, course, 2)
        y2s1 = getYCS(2, course, 1)
        y2s2 = getYCS(2, course, 2)
        y3s1 = getYCS(3, course, 1)
        y3s2 = getYCS(3, course, 2)
        template_values = {'y1s1' : y1s1,
           		   'y1s2' : y1s2,
         		   'y2s1' : y2s1,
         		   'y2s2' : y2s2,
        		   'y3s1' : y3s1,
        		   'y3s2' : y3s2
			   }
        template = jinja_environment.get_template('templates/modules.html')
        self.response.out.write(template.render(template_values))
	
class RssPage(webapp2.RequestHandler):
    def get(self):
        subs = current_user.subscriptions
        subs.filter('receive_notifications =', True)
        modules = [sub.module for sub in subs]
        name = current_user.full_name
	date = datetime.now()
        items =  []
        for mod in modules:
            for cat in mod.categories:
                for thread in cat.threads:
                    item = rss_item(title=thread.subject,
				    link="http://localhost:9999/showthread?tid=910",
				    description=mod.key().name(),
				    category=cat.name,
				    pub_date=datetime.now())
		    items.append(item)
	template_values = {'name':name,
			   'items':items,
			   'date':date}
	template = jinja_environment.get_template('templates/news.rss')
	self.response.headers['Content-Type'] = 'application/rss+xml'
        self.response.out.write(template.render(template_values))
			    
	    
def reset_db():
    for user in User.all():
        user.delete()

    for ycs in YearCourseSemester.all():
        ycs.delete()

    for mod in Module.all():
        mod.delete()

    for sub in Subscription.all():
        sub.delete()

    for sub in Category.all() :
        sub.delete()

    for i in Thread.all():
        i.delete()

    for i in Post.all():
        i.delete()

    for i in Rating.all():
        i.delete()

    for i in Assessment.all():
        i.delete()

    for i in Grade.all():
        i.delete()

    for i in Lecturer.all():
        i.delete()

    for i in Vote.all():
        i.delete()


#function to populate the db at the start of the app,
#that is if you don't have your own copy locally

def populate_db():

    ###### RESET #######
    reset_db()

    ###### POPULATE ######
    current_user = User(key_name='az2g10', full_name='Argyris Zardilis', password='1234', course='compsci',user_type="moderator", year=3,avatar="resources/img/dio.jpg", signature="L33T 5UP4|-| H4X0|2")
    current_user.put()

    user = User(key_name='dpm3g10',full_name='dio',password='1234',course='compsci',year=3)
    user.put()

    compsci11 = YearCourseSemester(year=int(1), semester=int(1), course="compsci",prettyName="Computer Science Year 1, Semester 1")
    compsci11.put()
    compsci12 = YearCourseSemester(year=int(1), semester=int(2), course="compsci",prettyName="Computer Science Year 1, Semester 2")
    compsci12.put()
    compsci21 = YearCourseSemester(year=int(2), semester=int(1), course="compsci",prettyName="Computer Science Year 2, Semester 1")
    compsci21.put()
    compsci22 = YearCourseSemester(year=int(2), semester=int(2), course="compsci",prettyName="Computer Science Year 2, Semester 2")
    compsci22.put()
    compsci31 = YearCourseSemester(year=int(3), semester=int(1), course="compsci",prettyName="Computer Science Year 3, Semester 1")
    compsci31.put()
    compsci32 = YearCourseSemester(year=int(3), semester=int(2), course="compsci",prettyName="Computer Science Year 3, Semester 2")
    compsci32.put()

    comp3001 = Module(key_name='COMP3001', title='Scripting Languages',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3001/",
                  yearCourseSemester=compsci31)
    comp3001.put()
    comp3033 = Module(key_name='COMP3033', title='Computational Biology',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3033/",
                  yearCourseSemester=compsci31)
    comp3033.put()
    comp3032 = Module(key_name='COMP3032', title='Intelligent Algorithms',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3032/",
                  yearCourseSemester=compsci31)
    comp3032.put()
    comp3016 = Module(key_name='COMP3016', title='Hypertext and Web Technologies',
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31)
    comp3016.put()
    comp3020 = Module(key_name='COMP3020', title='Individual Project',
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31)
    comp1314 = Module(key_name='COMP1314', title='Introduction to Everything',
                  ecs_page='http://goo.gl/S0e62',
                  yearCourseSemester=compsci11)
    comp1314.put()
    info3005 = Module(key_name='INFO3005', title='Security & Information Technology',
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31)
    info3005.put()

    sub1 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=comp3001)
    sub2 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=info3005)
    sub3 = Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=current_user, module=comp3016)
    sub1.put()
    sub2.put()
    sub3.put()
    comp3001.student_count = 1
    info3005.student_count = 1
    comp3016.student_count = 1
    comp3001.put()
    info3005.put()
    comp3016.put()
    # notice: must put() modules again
    ##### TODO: when done formally, increament counter for each subsribtion
    #### also do NOT remove subscribed students when year ends (needed for templates/forum_categories.html)

    assesCwk3001 = Assessment(title='Perl Coursework',
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
    assesCwk3001.sum_marks = comp3001.sum_marks = 100
    assesCwk3001.count_marks += 1
    comp3001.count_marks += 1
    assesCwk3001.put() # notice: must put again
    ##### TODO: when done formally, update sum_marks for each entry

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
    Rating(lecturer=msn,module=comp3001).put()
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

    #dios scripts for polulation
    q = User.all();
    q.filter('__key__ =',Key.from_path('User','az2g10'))
    rg = q.get()


    t = Thread(category=categGeneral3001,subject='Busy thread',body='Some very intriguing text!',poster=rg,tags=['yada','yada'])
    t.put()

    for d in range (0,10) :
        if d%2 == 0 :
            t = Thread(category=categGeneral3001,subject='Some subject number -> '+str(d),body='Some very intriguing text!',poster=rg,tags=['yada','yada'])
        else :
            t = Thread(category=categCoursework3001,subject='Some subject',body='Some very intriguing text!',poster=rg,tags=['yada','yada'])
        t.put()

    for i in range(3):
        p = Post(body='yada'+str(i),poster=rg, thread=t, answer = False)
        p.put()
        for g in range(1,4) :
            n = Post(body='yada2'+str(g),poster=rg,reply=p ,  answer = False)
            n.put()
            o = Post(body='yada2'+str(g),poster=rg,reply=p ,  answer = False)
            o.put()

            r = Post(body='yadayada3',poster=rg, reply=n, answer = False)
            r.put()
    r = Post(body='#This has no replies ',poster=rg, thread = t, answer = False)
    r.put()


populate_db()
app = webapp2.WSGIApplication([
                                   ('/'     , SignInPage),
                                   ('/main' , MainPage),
                                   ('/forum', ForumPage),
                                   ('/categories',CategoriesPage),
                                   ('/threads',ViewAllThreadsPage),
                                   ('/showthread',ThreadPage),
                                   ('/newthread',NewThread),
                                   ('/createnewthread',CreateNewThread),
                                   ('/replythread',ReplyToThread),
                                   ('/replypost',ReplyToPost),
                                   ('/vup',VoteUpPost),
                                   ('/vdown',VoteDownPost),
                                   ('/solution',ToggleSolution),
                                   ('/about', AboutPage),
                                   ('/notes', NotesPage),
                                   ('/contact',ContactPage),
                                   ('/something',EmailSent),
                                   ('/admin',AdminPage),
				   ('/modules', ModulesPage),
								   ('/admin-modules',AdminModules),
								   ('/admin-users',AdminUsers),
								   ('/profile',ProfilePage),
								   ('/admin-user-creation',AdminUserCreation),
				   ('/news.rss', RssPage)
								   
                                ], debug=True)
