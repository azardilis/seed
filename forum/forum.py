import webapp2
import jinja2
#imported for debugging reasons
import logging
from functions.RetrieveFunctions import *
import os
import cgi
import re
from populate import *
import populate
from google.appengine.api import mail
from functions.ForumFunctions import * # functions to handle posts and shit # "posts and shit" lol!
from model.base.Module import Module
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
from model.base.LecturerRating import LecturerRating
from google.appengine.ext.db import Key
from google.appengine.ext import db
from itertools import izip
from datetime import datetime
import time
import PyRSS2Gen

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

global current_user
global subscribed_modules
CATEGORIES = 'categories'
MID = 'mid'
EXTRA_TIME= 40*24*60*60 # ask for mark 40 days after assessment deadline

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
					
					moduleObject=Module(key_name=self.request.get('module_code'),
										title=self.request.get('module_title'),
										ecs_page=self.request.get('module_page'), 
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
		message=""
		if 'current_user' in globals() and current_user.user_type=='moderator':
				users=User.all()
				users.run()
				
				if self.request.get('filter-username') is not "":
					if User.get_by_key_name(self.request.get('filter-username')) is not None:
						filter=self.request.get('filter-username')
						users=[User.get_by_key_name(filter)]
					else:
						message="There are no users with that username, please try again!"
						users=[]
				
				template_values = {
					'current_user':current_user,
					'users':users,
					'message':message
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
	def post(self):
		#passing variables to template
		global current_user
		if 'current_user' in globals() and current_user.user_type=='moderator':
				new_user_fullname=self.request.get('user-fullname')
				new_user_ecsid=self.request.get('user-username')
				new_user_email=self.request.get('user-email')
				new_user_password=self.request.get('user-password')
				new_user_course=self.request.get('user-course')
				new_user_year=self.request.get('user-year')
				new_user_type=self.request.get('user-type')
				
				new_user=User(	password=new_user_password,
								key_name=new_user_ecsid,
								user_type=new_user_type,
								course=new_user_course,
								year=int(new_user_year),
								full_name=new_user_fullname,
								alternative_email=new_user_email
								)
				new_user.put()
				
				
				template_values = {
						'current_user':current_user,
						'message':"'new_user_fullname' has been added to the user list."
					}
				template = jinja_environment.get_template('templates/message-page.html')
				self.response.out.write(template.render(template_values))
		else:
				self.redirect("/")

#Handles rendering of the signinpage and authorisation and if okay redirects to main page
class SignInPage(webapp2.RequestHandler):
    def get(self):
    	
	
	if 'current_user' not in globals():
            template = jinja_environment.get_template('templates/signin.html')
            self.response.out.write(template.render())
	    global url
	    url=self.request.url
        else:
            self.redirect("/main")

    def post(self): #authenticate the user
        global current_user
		
	if self.request.url==url+'?reg=yes':
		pot_user=self.request.get('email');
		if pot_user[pot_user.index('@'):]!='ecs.soton.ac.uk' or pot_user[pot_user.index('@'):]!='soton.ac.uk':
			return 'This is not a University email'

		pot_user=pot_user[:pot_user.index('@')]
		pot_user_rev=pot_user[::-1]
		if User.get_by_key_name(pot_user) is not None:
			return 'User already exists'
		elif pot_user_rev[2]!='g':
			return 'This is not a University email'
		elif self.request.get('password')!=self.request.get('retype'):
			return 'Your passwords do not match'
		else:
			year=int(self.request.get('year'))
			fname=self.request.get('full_name')
			course=self.request.get('course')
			if year is None or year=='Year' or year=='':
				year=0
			
			if fname is None or fname=='Full Name' or fname=='':
				fname=''

			if course is None or course=='Course' or course=='':
				course=''

			user=User(key_name=pot_user, full_name=fname, password=self.request.get('password'), course=course,user_type="normal", year=year,avatar=self.request.get('avatar'), signature="L33T 5UP4|-| H4X0|2")
			user.put()


	else:
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
        global subscribed_modules
        if 'current_user' in globals():
            homepage_subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            subscribed_modules = homepage_subs

            modules = [sub.module for sub in homepage_subs]
            recent_threads = []
            for mod in modules:
                categs = mod.categories
                for cat in categs:
                    threads = cat.threads
                    threads = threads.order('-timestamp').fetch(2)
                    for thread in threads:
                        recent_threads.append(thread) 
                        
                template_values = {
                    'current_user':current_user,
                    'subscriptions':homepage_subs,
                    'threads':recent_threads
                    }
            template = jinja_environment.get_template('templates/index.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/")

class ForumPage(webapp2.RequestHandler):
	#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    	def get(self):
		sub_to_delete=cgi.escape(self.request.get('mod'))
		template = jinja_environment.get_template('templates/forum_subscriptions.html')
		subs = 	current_user.subscriptions
		self.response.write(sub_to_delete)
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
			if s.module.assessments.count()>0:
				assessments_flag=1
			else:
				assessments_flag=0
			mod_info.append(ModuleInfo(s.key(),s.module.key().name(),s.module.title,lecturers,assessments_flag))
			
			lecturers=[]

		template_params = {
			'mod_info':mod_info,
            'subscriptions':subscribed_modules
		}
        	self.response.out.write(template.render(template_params))	

class CategoriesPage(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    
### TEMP ###
    def getArgyris(self):
            q = User.all()
            q = q.filter('full_name =', 'Argyris Zardilis')
            result = q.run()
            us = []
            for u in result:
		us.append(u)
            return us[0]
### END TEMP ###

    def endOfSemester(self,module):
	semester = module.yearCourseSemester.semester
	month = datetime.now().month
	if semester == 1:
		return month == 12
	if semester == 2:
		return month == 5
	return false

    def getDueAssessments(self,current_user,extraTime=0):
            mcode = self.getModuleCode()
	    module = retrieve_module_name(mcode)
            dueAssessments = {}
            correspGrades = {}

            q = Grade.all()
            q = q.filter('student =', current_user)
            userGrades = q.run()
            for assessment in module.assessments:	
		if time.time() > time.mktime(assessment.dueDate.timetuple()) + extraTime:
			for grade in userGrades:
				if str(grade.assessment.key()) == str(assessment.key()) and not (grade.voted if extraTime==0 else grade.marked):
					dueAssessments[assessment.title] = assessment
					correspGrades[assessment.title] = grade

            return dueAssessments, correspGrades

    def getDueRatings(self,current_user):
	mcode = self.getModuleCode()
	module = retrieve_module_name(mcode)
	dueRatings = {}
	lecturerRatingObj = {}

	if self.endOfSemester(module):
		# couldn't find JOINs so:
		# out of all "lecturers that the current user hasn't rated for this module"
		q = LecturerRating.all()
		q = q.filter('module =', module)
		q = q.filter('student =', current_user)
		q = q.filter('voted =', False)
		# find the Rating objects for these lecturers (this module only)
		lecturerRatings = q.run()
		q = Rating.all()
		q = q.filter('module =', module)
		ratings = q.run()
		for lectRat in lecturerRatings:
			for rat in ratings:
				if rat.lecturer.full_name == lectRat.lecturer.full_name:
					dueRatings[rat.lecturer.full_name]=rat
					lecturerRatingObj[rat.lecturer.full_name]=lectRat

	return dueRatings, lecturerRatingObj

    def setUp(self):
            current_user = self.getArgyris()
            template = jinja_environment.get_template('templates/forum_categories.html')
            mcode = self.getModuleCode()
	    module = retrieve_module_name(mcode)

            categs = module.categories
            complete = list()

            for c in categs :
                ct = c.threads.order('-timestamp').fetch(2) #just to limit what is fetched, later change to 10 TODO?
                l = [c,ct]
                complete.append(l)
            
            toggle = 'Subscribe'
            if module.key() in [p.module.key() for p in current_user.subscriptions]:
                toggle = 'Unsubscribe'
            
            template_values= {
                    'complete' : complete,
                    'ratings' : module.lecturers,
                    'subscribed' : module.student_count,
                    'assessments' : module.assessments,
                    'module' : module,
                    'currentURL' : CATEGORIES+'?'+MID+'='+mcode,
                    'subscriptions':subscribed_modules,
                    'toggle'  : toggle
            }

            dueRatingId = None
            dueAssessments, correspGrades = self.getDueAssessments(current_user)
            if len(dueAssessments.items()):
		dueRatingId = '#popupDeadline' #change to popupId
		dueRatingTitle = dueAssessments.keys()[0]
            else:
		dueRatings, lecturerRatingObj = self.getDueRatings(current_user) #relying on subscriptions??
		if len(dueRatings.items()):
			dueRatingId = '#popupLecturer' 
	       		dueRatingTitle = dueRatings.keys()[0]
            	else:
			dueAssessments, correspGrades = self.getDueAssessments(current_user, EXTRA_TIME) #TODO:after exams they won't see it => email notification?
			if len(dueAssessments.items()):
				dueRatingId = '#popupMark'
				dueRatingTitle = dueAssessments.keys()[0]
            
            if dueRatingId:
		template_values['dueRatingTitle']= dueRatingTitle
		template_values['dueRatingId']= dueRatingId

            self.response.out.write(template.render(template_values))

    def getModuleCode(self):
	mcode = self.request.get(MID)
	if not mcode :
		logging.error('module code was empty ') #does this really work ?
	return mcode

    def get(self) : 
	self.setUp()
    	
    def post(self) :

	# Define the expected POST params
	names = 'clear','prompt','difficult','interesting','mark'
	post_params={}

	# Get the expected POST params
	for name in names: post_params[name]=self.request.get(name)

	# Cast to int
	for key,value in post_params.items(): post_params[key] = int(value) if value else value

	# Rating (trying to be secure - not trusting the user)
	current_user = self.getArgyris()
	hiddenType = self.request.get('popupType')
	hiddenTitle = self.request.get('dueRatingTitle')
	if hiddenType == 'deadline':
		dueAssessments,correspGrades = self.getDueAssessments(current_user)
		rate_assessment(dueAssessments[hiddenTitle],post_params['interesting'],post_params['difficult'],correspGrades[hiddenTitle])
	elif hiddenType == 'mark':
		dueAssessments,correspGrades = self.getDueAssessments(current_user, EXTRA_TIME)
		mark_assessment(dueAssessments[hiddenTitle],post_params['mark'],correspGrades[hiddenTitle])
	elif hiddenType == 'lecturer':
		dueRatings, lecturerRatingObj = self.getDueRatings(current_user)
		rate_lecturer(dueRatings[hiddenTitle],post_params['clear'],post_params['prompt'],lecturerRatingObj[hiddenTitle])

	# Reload
	self.setUp()

class ThreadPage(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
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
                    'posts' : posts,
                    'subscriptions':subscribed_modules
            }
            self.response.out.write(template.render(template_params))
        else :
            self.response.out.write('Unable to find thread '+str(self.request.get('ti'))+'<')

class ViewAllThreadsPage(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def get(self):
        category = retrieve_category(self.request.get('cid'))

        if category :
            threads = category.threads.order('-timestamp')
            template_vars = {
                    'category' : category,
                    'threads':threads,
                    'subscriptions':subscribed_modules
            }
            template = jinja_environment.get_template('templates/forum_category_all.html')
            self.response.out.write(template.render(template_vars))
        else :
            logging.error('no category found '+str(cid))
            self.response.out.write('Couldn\'t get category')

class NewThread(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def get(self):
        cid = cgi.escape(self.request.get('catid'))
        template = jinja_environment.get_template('templates/newthread.html')

        if cid :
            template_params = {
                    'cid' : cid,
                    'subscriptions':subscribed_modules
            }
            self.response.out.write(template.render(template_params))
        else : logging.error('newthread : empty cid >'+str(cid)+'<')

class CreateNewThread(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def post(self):
        bd = cgi.escape(self.request.get('body'))
        sbj = cgi.escape(self.request.get('subject'))
        tgs = cgi.escape(self.request.get('tags'))

        cat = retrieve_category(self.request.get('cid'))

        if cat :
            t = Thread(category = cat,poster=current_user, tags=tgs.split(','),subject=sbj,body =bd )
            t.put()
            self.response.out.write(t.key().id())
        else :
            self.response.out.write('category not found')

class ReplyToThread(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def post(self):
        thrd = retrieve_thread(self.request.get('tid'))

        if thrd :
            bd = cgi.escape(self.request.get('bd'))
            sbj = cgi.escape(self.request.get('sbj'))

            p = Post(body=bd, thread = thrd, poster = current_user)
            p.put()

	    thrd.answers += 1 
	    thrd.put()

            self.response.out.write(serialize_ajax_info(current_user,p,''))
        else :
            self.response.out.write('Thread not found')
            logging.error('Thread not found, tid : '+str(tid)+'<')

class ReplyToPost(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
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
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
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
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
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
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def post(self):
        thrd = retrieve_thread(self.request.get('tid'))
        pst = retrieve_post(self.request.get('pid'))
        if thrd and pst  :
            if str(thrd.poster.key()) == str(current_user.key())  and (pst.key() in [p.key() for p in thrd.posts]):

                for ps in thrd.posts: #reset all current answers
                    if not (str(ps.key()) is str(pst.key())) :
                        ps.answer = False
                        ps.put()

                pst.answer = not pst.answer
                pst.put()

		if pst.answer :
			thrd.answered  = True
			if not thrd.subject[:8] == '[SOLVED]':
				thrd.subject = '[SOLVED]'+thrd.subject
		else :
			thrd.answered = False
			if thrd.subject[:8] == '[SOLVED]' :
				thrd.subject = thrd.subject[8:]
		thrd.put()

                self.response.out.write('ok')
                logging.info('toggled state')
            else :
                self.response.out.write('Failing checks')
                logging.error('curr_user_k :'+str(current_user.key())+', poster_k:'+str(thrd.poster.key())+', post in thrd.posts = '+str((pst.key() in [p.key() for p in thrd.posts])) )
        else :
            logging.error('Unable to find thread or post')

class ToggleSubscription(webapp2.RequestHandler):
    def post(self):
        mod = db.get(Key.from_path('Module', cgi.escape(self.request.get('mcode'))))
        if mod :
            sub = Subscription.all()
            sub.filter('subscribed_user =', current_user)
            sub.filter('module =',mod)
            sub = sub.get()

            if sub:
                sub.delete()
                self.response.out.write('Subscribe')
            else :
                Subscription(subscribed_user = current_user , module = mod).put()
                self.response.out.write('Unsubscribe')
        else:
            logging.error('Couldn\'t get module with mcode '+self.request.get('mcode'))

'''Uses User Key to query the right User Entity'''
class ProfilePage(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def get(self):
		template = jinja_environment.get_template('templates/profile.html')
		subs = 	current_user.subscriptions
		sub_to_delete=cgi.escape(self.request.get('mod'))
		self.response.write(sub_to_delete)
		
		user_key = current_user.key()
		userQ=User.all()
		userQ=userQ.filter('__key__ = ' ,user_key)
		user = userQ.get()
		mod_info=[]
		lecturers=[]
		
		if not sub_to_delete is '':
			subs.filter("__key__",Key(sub_to_delete))
			subs.get().delete()
			subs = 	current_user.subscriptions
		
		for s in subs:
			ratQ=Rating.all()
			ratQ.filter("module",s.module)
			for rat in ratQ:
				lectQ=Lecturer.all()
				lectQ.filter("__key__",rat.lecturer.key())
				lec=lectQ.get()
				lecturers.append(lec)
			if s.module.assessments.count()>0:
				assessments_flag=1
			else:
				assessments_flag=0
			mod_info.append(ModuleInfo(s.key(),s.module.key().name(),s.module.title,lecturers,assessments_flag))
			
			lecturers=[]
			
		template_params = {
			'user':user,
			'mod_info':mod_info,
            'subscriptions':subscribed_modules
		}
		self.response.out.write(template.render(template_params))


class AboutPage(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def get(self):
        template = jinja_environment.get_template('templates/about.html')
        parms = {
             'subscriptions':subscribed_modules
        }
        self.response.out.write(template.render(parms))

class NotesPage(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
    def get(self):
        template = jinja_environment.get_template('templates/notes.html')

        parms = {
             'subscriptions':subscribed_modules
        }
        self.response.out.write(template.render(parms))

class ContactPage(webapp2.RequestHandler):
    def get(self):
        subject=''
        message=''
        template = jinja_environment.get_template('templates/contact.html')
        template_values = {
                           subject:'subject',
                           message:'message',
                           'subscriptions':subscribed_modules
                           }
        self.response.out.write(template.render(template_values))

class EmailSent(webapp2.RequestHandler):
#TODO: CHECK IF USER IS LOGGED IN BEFORE DISPLAYING THE PAGE!
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
	def __init__(self,sub_key,sub_code,sub_name,mod_lecturers,mod_assessments):
		self.sub_key=sub_key
		self.sub_code=sub_code
		self.sub_name=sub_name
		self.mod_lecturers=mod_lecturers
		self.mod_assessments=mod_assessments

class ModulesPage(webapp2.RequestHandler):
    def get(self):
        if 'current_user' in globals():
            homepage_subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        else:
            self.redirect('/')
        
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
        		   'y3s2' : y3s2,
                   'subscriptions':subscribed_modules
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

class AssessmentFeedback(webapp2.RequestHandler):
    def get(self):
	template_values = {}
        template = jinja_environment.get_template('templates/feedback.html')
	self.response.headers['Content-Type'] = 'text/html'
	self.response.out.write(template.render(template_values))
    def post(self):
	template_values={
		'difficult':self.request.get('Difficult'),
		'interesting':self.request.get('Interesting')
	}
        template = jinja_environment.get_template('templates/feedback.html')
	self.response.headers['Content-Type'] = 'text/html'
	self.response.out.write(template.render(template_values))

populate.populate_db()
app = webapp2.WSGIApplication([
	('/'     , SignInPage),
	('/main' , MainPage),
	('/forum', ForumPage),
	('/'+CATEGORIES,CategoriesPage),
	('/threads',ViewAllThreadsPage),
	('/showthread',ThreadPage),
	('/newthread',NewThread),
	('/createnewthread',CreateNewThread),
	('/replythread',ReplyToThread),
	('/replypost',ReplyToPost),
	('/vup',VoteUpPost),
	('/vdown',VoteDownPost),
	('/solution',ToggleSolution),
	('/subscriptions',ToggleSubscription ),
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
	('/news.rss', RssPage),
	('/module-feedback', AssessmentFeedback)
								   
], debug=True)
