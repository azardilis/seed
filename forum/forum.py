import webapp2
import jinja2
#imported for debugging reasons
import logging
from functions.RetrieveFunctions import *
import os
import cgi
import re
from ratings import *
import populate
from google.appengine.api import mail
from functions.ForumFunctions import * # functions to handle post related things
from model import *
from webapp2_extras import sessions
from google.appengine.api import images
from google.appengine.ext.db import Key
from google.appengine.ext import db
from google.appengine.api import images
from datetime import datetime
from functions.BaseHandler import BaseHandler
import time
import operator

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def getSchoolYear(now):
    q=SchoolYear.all().run()
    for schY in q:
        if now.month > 9:
            if schY.start == now.year: return schY
        else:
            if schY.end == now.year: return schY

    return None # not found

global session_dic
session_dic={}
session_dic['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key'}
global current_user
CATEGORIES,MID='categories','mid'
EXTRA_TIME=40*24*60*60 #40 days

#encapsulated all the information needed for an rss item
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

#returns the number of occurences of search_term in thread attributes
def search_success(thread, search_term):
    success = 0
    search_places = []
    search_places.append(thread.tags)
    search_places.append(thread.poster.full_name)
    search_places.append(thread.subject)
    search_places.append(thread.poster.key().name())
    for search_place in search_places:
        if search_term in search_place: success += 1
    return success

def search_thread_tags(search_terms):
    results = {}
    threads = Thread.all()
    for thread in threads:
        for search_term in search_terms:
			succ = search_success(thread, search_term)	
			if succ > 0 and thread in results: results[thread] += succ
			elif succ > 0 and not (thread in results): results[thread] = succ
    #sort the results dict by the occurences of search_terms in tags
    sorted_results = sorted(results.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sorted_results

def getYcsFromCode(code):
    course=code.split('-')[1]
    year=code.split('-')[2]
    semester=code.split('-')[3]

#returns modules related to a specific year, course, semester
def getYCS(year, course, semester):
    ycs_list = YearCourseSemester.all()
    ycs_list.filter('year =', year)
    ycs_list.filter('course =', course)
    ycs_list.filter('semester =', semester)
    ycs = ycs_list.get()
    return ycs.modules

#Main administration page
class AdminPage(BaseHandler):

    def get(self):
    #passing variables to template
        global current_user
        if self.session.get('type')==1:
            current_user = db.get(Key.from_path('User',self.session.get('name')))
            subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            template_values = {'subscriptions':subscribed_modules,'current_user':current_user}
            template = jinja_environment.get_template('templates/admin.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/")

#Modules administration page
class AdminModules(BaseHandler):

    def get(self):
        #passing variables to template
        global current_user
        firsthalf, secondhalf, allYcsArray = [], [], []
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        if self.session.get('type')==1:
            modules=Module.all().run()
            allYcs=YearCourseSemester.all().run()
            count=Module.all().count()
            #splitting the modules array in half to be able to display it nicely on two columns in the template
            i=1
            if count%2 is 0:
                for module in modules:
                    if i<=count/2: firsthalf.append(module)
                    else: secondhalf.append(module)
                    i=i+1
            else:
                for module in modules:
                    if i<=count/2+1: firsthalf.append(module)
                    else: secondhalf.append(module)
                    i=i+1
            #copying allYcs into an array to be able to use it properly in the template
            for ycs in allYcs:
                allYcsArray.append(ycs)
            template_values={'current_user':current_user,'subscriptions':subscribed_modules,'firsthalf':firsthalf,'secondhalf':secondhalf,'allYcs':allYcsArray}
            template = jinja_environment.get_template('templates/admin-modules.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/")

    def post(self):
                error_msg = ""
                success = True
                moduleObject = None
		global current_user
		current_user = db.get(Key.from_path('User',self.session.get('name')))
                subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
		if self.session.get('type')==1:
			is_delete = self.request.POST.get('remove_module_button', None)
			is_apply = self.request.POST.get('apply_button', None)
			is_add = self.request.POST.get('add_button', None)
			if is_apply:
				#get the module object from the datastore
                                try:
				    moduleObject=Module.get(cgi.escape(self.request.get('module_key')))
                                    if cgi.escape(self.request.get('module_title')) is not None: moduleObject.title=cgi.escape(self.request.get('module_title'))
                                    if cgi.escape(self.request.get('module_code')) is not None: moduleObject.ecs_page=cgi.escape(self.request.get('module_page'))
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
                                except:
                                    success = False #something was wrong with the provided values, display error page
				    if moduleObject: moduleObject.put()
			if is_delete:
				#get the module object from the datastore
				moduleObject=Module.get(cgi.escape(self.request.get('module_key')))
				for rating in moduleObject.lecturers: rating.delete()
				for sub in moduleObject.registered_students: sub.delete()
				for category in moduleObject.categories:
					for thread in category.threads: 
						deleteThread(thread.key())
						thread.delete()
					category.delete()
				for assess in moduleObject.assessments:
					for grade in assess.grades: grade.delete()
					assess.delete()
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
					try:
                                            moduleObject=Module(key_name=self.request.get('module_code'), title=self.request.get('module_title'), ecs_page=self.request.get('module_page'), yearCourseSemester=ycs)
                                        except:
                                            success = False #something was wrong with the provided values, display error page
                                            
				if moduleObject: moduleObject.put()
                        if success:
                            subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
                            template_values = { 'current_user':current_user, 'subscriptions':subs,
                                                'message':"The changes have been successfully submited to the datastore" }
                            template = jinja_environment.get_template('templates/message-page.html')
                            self.response.out.write(template.render(template_values))
                        else:
                            self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details':'Something was wrong with the values provided!','current_user':current_user, 'subscriptions':subscribed_modules }))
		else: self.redirect("/")

#Assessments administration page
class AdminAssessment(BaseHandler):
    def get(self):
        #passing variables to template
		global current_user
		firsthalf, secondhalf=[], []
		current_user = db.get(Key.from_path('User',self.session.get('name')))
		if self.session.get('type')==1:
				cwks=Assessment.all().run()
				count=Assessment.all().count()
				#splitting the assessments array in half to be able to display it nicely on two columns in the template
				i=1
				if count%2 is 0:
					for cwk in cwks:
						if i<=count/2: firsthalf.append(cwk)
						else: secondhalf.append(cwk)
						i=i+1
				else:
					for cwk in cwks:
						if i<=count/2+1: firsthalf.append(cwk)
						else: secondhalf.append(cwk)
						i=i+1
				subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
				template_values = { 'current_user':current_user, 'firsthalf':firsthalf, 'secondhalf':secondhalf, 'subscriptions':subs }
				template = jinja_environment.get_template('templates/admin-assessments.html')
				self.response.out.write(template.render(template_values))

		else: self.redirect("/")

    def post(self):
		global current_user
                cwkObject = None
                success = True
		current_user = db.get(Key.from_path('User',self.session.get('name')))
                subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
		if self.session.get('type')==1:
			is_delete,is_apply,is_add = self.request.POST.get('remove_module_button', None),self.request.POST.get('apply_button', None), self.request.POST.get('add_button', None)
			if is_apply:
				try:
					cwkObject=Assessment.get(cgi.escape(self.request.get('cwk_key')))
					if cgi.escape(self.request.get('cwk_title')): cwkObject.title=cgi.escape(self.request.get('cwk_title'))
					if cgi.escape(self.request.get('cwk_duedate')): cwkObject.dueDate=datetime.strptime(cgi.escape(self.request.get('cwk_duedate')),'%Y-%m-%d %H:%M:%S')
					if cgi.escape(self.request.get('cwk_speclink')): cwkObject.specLink=cgi.escape(self.request.get('cwk_speclink'))
					if cgi.escape(self.request.get('cwk_handin')): cwkObject.handin=cgi.escape(self.request.get('cwk_handin'))
					if cgi.escape(self.request.get('cwk_modulecode')): cwkObject.module=Module.get(cgi.escape(self.request.get('cwk_modulecode')))
				except:
					success = False
				if cwkObject: cwkObject.put()
			if is_delete:
				#get the assessment object from the datastore
				cwkObj=Assessment.get(cgi.escape(self.request.get('cwk_key')))
				cwkObj.module.sum_marks -= cwkObj.sum_marks; cwkObj.module.count_marks -= cwkObj.count_marks;
				cwkObj.module.sum_difficulty -= cwkObj.sum_difficulty; cwkObj.module.count_difficulty -= cwkObj.count_difficulty;
				cwkObj.module.sum_interest -= cwkObj.sum_interest; cwkObj.module.count_interest -= cwkObj.count_interest;
				cwkObj.module.put()
				for grade in cwkObj.grades: grade.delete()
				cwkObj.delete()
			if is_add:
				if cgi.escape(self.request.get('cwk_title')) is not None and cgi.escape(self.request.get('cwk_duedate')) is not None and cgi.escape(self.request.get('cwk_modulecode')) is not None:
					cwk_title=cgi.escape(self.request.get('cwk_title'))
					cwk_duedate=cgi.escape(self.request.get('cwk_duedate'))
					cwk_speclink=cgi.escape(self.request.get('cwk_speclink'))
					cwk_handin=cgi.escape(self.request.get('cwk_handin'))
					try:
					  cwkObject=Assessment(title=cwk_title, dueDate=datetime.strptime(cwk_duedate, '%b %d %Y %I:%M%p'), specLink=cwk_speclink, handin=cwk_handin, module=Module.get(cgi.escape(self.request.get('cwk_modulecode'))))
					except:
					  success = False
				
					if cwkObject: cwkObject.put()
                        if success:
                            template_values = { 'current_user':current_user, 'message':"The changes have been successfully submited to the datastore" }
                            template = jinja_environment.get_template('templates/message-page.html')
                            self.response.out.write(template.render(template_values))

                        else: self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details':'Something was wrong with the values provided!','current_user':current_user, 'subscriptions':subscribed_modules }))
			
		else: self.redirect("/")

#Existing user accounts administration page
class AdminUsers(BaseHandler):
    def get(self):
        #passing variables to template
        global current_user
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        message=""
        if self.session.get('type')==1:
            users=User.all()
            users.run()

            if self.request.get('filter-username') is not "":
                if User.get_by_key_name(self.request.get('filter-username')) is not None:
                    filter=self.request.get('filter-username')
                    users=[User.get_by_key_name(filter)]
                else:
                    message="There are no users with that username, please try again!"
                    users=[]
            subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            template_values = { 'current_user':current_user, 'subscriptions':subscribed_modules, 'users':users, 'message':message }
            template = jinja_environment.get_template('templates/admin-users.html')
            self.response.out.write(template.render(template_values))
        else: self.redirect("/")

#Admin user creation page
class AdminUserCreation(BaseHandler):
    def get(self):
    #passing variables to template
        global current_user
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if 'current_user' in globals() and self.session.get('type')==1:
            if self.session.get('type')==1:
                subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
                template_values = { 'subscriptions':subscribed_modules, 'current_user':current_user }
                template = jinja_environment.get_template('templates/admin-user-creation.html')
                self.response.out.write(template.render(template_values))
        else: self.redirect("/")
    def post(self):
        #passing variables to template
        global current_user
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if 'current_user' in globals() and self.session.get('type')==1:
            new_user_fullname=self.request.get('user-fullname')
            new_user_ecsid=self.request.get('user-username')
            new_user_email=self.request.get('user-email')
            new_user_password=self.request.get('user-password')
            new_user_course=self.request.get('user-course')
            new_user_year=self.request.get('user-year')
            new_user_type=self.request.get('user-type')

            User(  password=new_user_password, key_name=new_user_ecsid, user_type=int(new_user_type), course=new_user_course, year=int(new_user_year), full_name=new_user_fullname, alternative_email=new_user_email ).put()

            subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            template_values = { 'current_user':current_user, 'subscriptions':subscribed_modules, 'message':"The user has been added to the user list." }
            template = jinja_environment.get_template('templates/message-page.html')
            self.response.out.write(template.render(template_values))
        else: self.redirect("/")

class AdminEditUser(BaseHandler):
    def get(self):
            #passing variables to template
        global current_user
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        message=""
        if 'current_user' in globals() and self.session.get('type')==1:
                #first check that the user parameter is set
            subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            if self.request.get('user') is not "":
                if User.get_by_key_name(self.request.get('user')) is not None:
                    filter=self.request.get('user')
                    users=[User.get_by_key_name(filter)]

                    template_values = { 'current_user':current_user, 'user':users[0], 'subscriptions':subscribed_modules, 'message':message }
                else:
                    message="There are no users with that username, please try again!"
                    users=[]

                    template_values = { 'current_user':current_user, 'user':None, 'subscriptions':subscribed_modules, 'message':message }
            template = jinja_environment.get_template('templates/admin-edit-user.html')
            self.response.out.write(template.render(template_values))
        else: self.redirect("/")
	
    def post(self):
        global current_user
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if 'current_user' in globals() and self.session.get('type')==1:
            #get the module object from the datastore
            userObject=User.get_by_key_name(self.request.get('user-username'))
            if cgi.escape(self.request.get('user-fullname')) is not None:
                userObject.full_name=cgi.escape(self.request.get('user-fullname'))
            if cgi.escape(self.request.get('user-course')) is not None:
                userObject.course=cgi.escape(self.request.get('user-course'))
            if cgi.escape(self.request.get('user-year')) is not None:
                userObject.year=int(cgi.escape(self.request.get('user-year')))
            if cgi.escape(self.request.get('user-type')) is not None:
                userObject.user_type=int(cgi.escape(self.request.get('user-type')))
            userObject.alternative_email=cgi.escape(self.request.get('user-email'))
            userObject.karma=int(cgi.escape(self.request.get('user-karma')))
            userObject.put()
            subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            template_values = { 'current_user':current_user, 'subscriptions':subscribed_modules, 'message':"The changes have been saved!" }
            template = jinja_environment.get_template('templates/message-page.html')
            self.response.out.write(template.render(template_values))
        else: self.redirect("/")

#Handles rendering of the signinpage and authorisation and if okay redirects to main page
class SignInPage(BaseHandler):
    def get(self):#show the initial signin page
		if  self.session.get('type') is None or self.session.get('type')==-1:
			template = jinja_environment.get_template('templates/signin.html')
			self.response.out.write(template.render({'bad_login':self.request.get('bad_login')}))
			self.session['type']=-1
			global url
			url=self.request.url
		else:self.redirect("/main")

    def post(self):
        global current_user
		
        if self.request.url==url+'?reg=yes': #try to register the user
			pot_user=self.request.get('email') 
			pot_user=pot_user[:pot_user.index('@')] 

			if User.get_by_key_name(pot_user) is not None: return 'User already exists' 
			elif self.request.get('password')!=self.request.get('retype'): return 'Your passwords do not match' 
			else: 
				fname=self.request.get('full_name') 
				course=self.request.get('course') 
				if self.request.get('year') is not int or self.request.get('year')>5: year=0 
				if fname is None or fname=='': fname=pot_user 
				if course is None or course=='': course='compsci'
				User(key_name=pot_user, full_name=fname, password=self.request.get('password'),course=course,user_type=0, year=year,).put()
        else:
			if len(self.request.get('user'))==0 or len(self.request.get('password'))==0:#check if empty form when logging in
				self.redirect('?bad_login=1')
				return

			username, password = self.request.get('user'),self.request.get('password')
			potential_user=User.get_by_key_name(cgi.escape(self.request.get('user')))
			if potential_user is not None and potential_user.password==self.request.get('password'):#check information for logging in
				current_user=potential_user
				self.session['name'],self.session['type'] = self.request.get('user'),potential_user.user_type
				self.redirect("/main")

			else: self.redirect("/?bad_login=1")

class MainPage(BaseHandler):#handles the page as soon as a user logs in
    def get(self):

        global current_user
        if 'current_user' in globals() and (self.session.get('type')==0 or self.session.get('type')==1):

            homepage_subs=[]
            current_user = db.get(Key.from_path('User',self.session.get('name')))
            homepage_subs = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
            subscribed_modules = homepage_subs

            modules = [sub.module for sub in homepage_subs]
            recent_threads = []
            for mod in modules:#makes user's info ready
                categs = mod.categories
                for cat in categs:
                    threads = cat.threads
                    threads = threads.order('-timestamp').fetch(2)
                    for thread in threads: recent_threads.append(thread)
			
            if homepage_subs.__len__()==0 or recent_threads.__len__()==0: recent_threads=[]
            template_values = { 'current_user':current_user, 'subscriptions':homepage_subs, 'threads':recent_threads }
            template = jinja_environment.get_template('templates/index.html')
            self.response.out.write(template.render(template_values))

        else: self.redirect("/")

class ForumPage(BaseHandler):#view a user's subscriptions
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        sub_to_delete=cgi.escape(self.request.get('mod'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        template = jinja_environment.get_template('templates/forum_subscriptions.html')
        subs =  current_user.subscriptions
        self.response.write(sub_to_delete)
        if sub_to_delete:
            subs.filter("__key__",Key(sub_to_delete))
            sub = subs.get()
            populate.unsubscribe(sub.subscribed_user, sub.module)
            subs =  current_user.subscriptions

        mod_info, lecturers = [], []

        for s in subs:
            ratQ=Rating.all()
            ratQ.filter("module",s.module)
            for rat in ratQ:
                lectQ=Lecturer.all()
                lectQ.filter("__key__",rat.lecturer.key())
                lec=lectQ.get()
                lecturers.append(lec)
            if s.module.assessments.count()>0: assessments_flag=1
            else: assessments_flag=0
            mod_info.append(ModuleInfo(s.key(),s.module.key().name(),s.module.title,lecturers,assessments_flag))#creates a Module info object to pass the information easier

            lecturers=[]

        template_params = { 'current_user':current_user,
                            'mod_info':mod_info,
                            'subscriptions':subscribed_modules }
        self.response.out.write(template.render(template_params))

class CategoriesPage(BaseHandler):#

    def endOfSemester(self,module):
        semester = module.yearCourseSemester.semester
        month = datetime.now().month
        if semester == 1: return month == 12
        if semester == 2: return month == 5
        return false

    def getDueAssessments(self,current_user,extraTime=0):
        mcode = self.getModuleCode()
        module = retrieve_module_name(mcode)
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        dueAssessments, correspGrades = {}, {}

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
        dueRatings,lecturerRatingObj = {}, {}

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
        template = jinja_environment.get_template('templates/forum_categories.html')
        mcode = self.getModuleCode()
        module = retrieve_module_name(mcode)
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]

        categs = module.categories
        complete = list()

        for c in categs :
            ct = c.threads.order('-timestamp').fetch(5) 
            l = [c,ct]
            complete.append(l)

        toggle = 'Subscribe'
        if module.key() in [p.module.key() for p in current_user.subscriptions]:
            toggle = 'Unsubscribe'

        template_values= { 'current_user':current_user,
                'complete' : complete,
                'ratings' : module.lecturers,
                'subscribed' : module.student_count,
                'assessments' : module.assessments,
                'module' : module,
                'currentURL' : CATEGORIES+'?'+MID+'='+mcode,
                'subscriptions':subscribed_modules,
                'toggle'  : toggle }

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
                dueAssessments, correspGrades = self.getDueAssessments(current_user, EXTRA_TIME)
                if len(dueAssessments.items()):
                    dueRatingId = '#popupMark'
                    dueRatingTitle = dueAssessments.keys()[0]

        if dueRatingId:
            template_values['dueRatingTitle']= dueRatingTitle
            template_values['dueRatingId']= dueRatingId

        self.response.out.write(template.render(template_values))

    def getModuleCode(self):
        mcode = self.request.get(MID)
        if not mcode : logging.error('module code was empty ') #does this really work ? #who the fuck knows? :P
        return mcode

    def get(self) :
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
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
        hiddenType, hiddenTitle = self.request.get('popupType'),self.request.get('dueRatingTitle')
        if hiddenType == 'deadline':
            dueAssessments,correspGrades = self.getDueAssessments(current_user)
            if hiddenTitle in dueAssessments.keys(): rate_assessment(dueAssessments[hiddenTitle],post_params['interesting'],post_params['difficult'],correspGrades[hiddenTitle])
        elif hiddenType == 'mark':
            dueAssessments,correspGrades = self.getDueAssessments(current_user, EXTRA_TIME)
            if hiddenTitle in dueAssessments.keys(): mark_assessment(dueAssessments[hiddenTitle],post_params['mark'],correspGrades[hiddenTitle])
        elif hiddenType == 'lecturer':
            dueRatings, lecturerRatingObj = self.getDueRatings(current_user)
            if hiddenTitle in dueAssessments.keys(): rate_lecturer(dueRatings[hiddenTitle],post_params['clear'],post_params['prompt'],lecturerRatingObj[hiddenTitle])

        # ReloadWe should upload the website
        self.setUp()

class ThreadPage(BaseHandler):
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
        t =retrieve_thread(self.request.get('tid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if t :
            template = jinja_environment.get_template('templates/forum_thread.html')

            l1p = get_posts(int(cgi.escape(self.request.get('tid'))))
            posts = ''
            posts = get_children(l1p,posts,1,(t.poster.key() == current_user.key()),current_user)
            subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]

            template_params = { 'user' : t.poster,
                        'nop': len([p for p in t.poster.posts]),
                        'thread': t ,
                        'posts' : posts,
                        'current_user':current_user,
                        'subscriptions':subscribed_modules }
            self.response.out.write(template.render(template_params))
        else :
            logging.error('Unable to find thread '+str(self.request.get('ti'))+'<')
            self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details':'Unable to find the specified thread.'}))

class ViewAllThreadsPage(BaseHandler):
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
        category = retrieve_category(self.request.get('cid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]

        if category :
            threads = category.threads.order('-timestamp')
            template_vars = { 'current_user':current_user,
                    'category' : category,
                    'current_user':current_user,
                    'threads':threads,
                    'subscriptions':subscribed_modules }
            template = jinja_environment.get_template('templates/forum_category_all.html')
            self.response.out.write(template.render(template_vars))
        else :
            logging.error('no category found '+str(self.request.get('cid')))
            self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details' : 'We were unable to find the specified category.'}))

class removeThread(BaseHandler):
    def get(self):
        if self.session.get('type')!=1:
            self.redirect('/')
            return
        tid= self.request.get('tid')

        if tid :
            thread=Thread.get(tid)
            deleteThread(cgi.escape(tid))
            thread.delete()
            template_values = {
						'current_user':current_user,
						'message':"The changes have been saved!"
			}
            template = jinja_environment.get_template('templates/message-page.html')
            self.response.headers.add_header("Expires","0")
            self.response.headers.add_header("Pragma","no-cache")
            self.response.headers.add_header("Cache-Control","no-cache, no-store, must-revalidate")
            self.response.out.write(template.render(template_values))
        else :
            logging.error('no category found '+str(cid))
            self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details' : 'We were unable to find the specified category.'}))

class NewThread(BaseHandler):

    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        cid = cgi.escape(self.request.get('catid'))
        template = jinja_environment.get_template('templates/newthread.html')
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]

        if cid :
            template_params = { 'cid' : cid,
                    'current_user':current_user,
                    'subscriptions':subscribed_modules }
            self.response.out.write(template.render(template_params))
        else :
            self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details' : 'We were unable to find the specified category.'}))
            logging.error('newthread : empty cid >'+str(cid)+'<')

class CreateNewThread(BaseHandler):

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
        bd = cgi.escape(self.request.get('body'))
        sbj = cgi.escape(self.request.get('subject'))
        tgs = cgi.escape(self.request.get('tags'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))

        cat = retrieve_category(self.request.get('cid'))

        if cat :
            t = Thread(category = cat,poster=current_user, tags=tgs.split(','),subject=sbj,body =bd )
            t.put()
            self.response.out.write(t.key().id())
        else : self.response.out.write(jinja_environment.get_template('templates/error_template.html').render({'error_details' : 'We were unable to find the specified category.'}))

class ReplyToThread(BaseHandler):

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
        thrd = retrieve_thread(self.request.get('tid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
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

class ReplyToPost(BaseHandler):

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('403')
            return

        pst =retrieve_post(self.request.get('r2pid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if pst :
            bd = cgi.escape(self.request.get('bd'))
            p = Post(reply=pst,poster=current_user,body=bd)
            p.put()
            self.response.out.write(serialize_ajax_info(current_user, p,str(pst.key().id())))
        else :
            self.response.out.write('Could not reply')
            logging.error('Couldnt find post, pid : '+pid+'<')

class VoteUpPost(BaseHandler):

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        pst =retrieve_post(self.request.get('pid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))

        if pst and not (pst.key() in [v.post.key() for v in current_user.votes]):
            pst.votes = pst.votes +1
            pst.put()
            Vote(user=current_user,post=pst,value=1).put()
            self.response.out.write(pst.votes)
        else :
            self.response.out.write('Didn\'t vote up')
            logging.error('unable to vote up post pid '+self.request.get('pid')+'<')


class VoteDownPost(BaseHandler):

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        pst = retrieve_post(self.request.get('pid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))

        if pst and not (pst.key() in [v.post.key() for v in current_user.votes]):
            pst.votes = pst.votes-1
            pst.put()
            Vote(user=current_user,post=pst,value=-1).put()
            self.response.out.write(pst.votes)
        else :
            self.response.out.write('Didn\'t vote down')
            logging.error('unable to vote down pid '+self.request.get('pid')+'<')

class ToggleSolution(BaseHandler) :

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
        thrd = retrieve_thread(self.request.get('tid'))
        pst = retrieve_post(self.request.get('pid'))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if thrd and pst  :
            if str(thrd.poster.key()) == str(current_user.key())  and (pst.key() in [p.key() for p in thrd.posts]):
                for ps in thrd.posts: #reset all current answers
                    if not (str(ps.key()) is str(pst.key())) :
                        ps.answer = False
                        ps.put()

                pst.answer = not pst.answer
                pst.put()

                pst_poster = pst.poster
                if pst.answer :
                    pst_poster.karma = pst_poster.karma +1
                    thrd.answered  = True
                    if not thrd.subject[:8] == '[SOLVED]': thrd.subject = '[SOLVED]'+thrd.subject
                else :
                    thrd.answered = False
                    pst_poster.karma = pst_poster.karma - 1
                    if thrd.subject[:8] == '[SOLVED]' : thrd.subject = thrd.subject[8:]
                thrd.put()
                pst_poster.put()

                self.response.out.write('ok')
                logging.info('toggled state')
            else :
                self.response.out.write('Failing checks')
                logging.error('curr_user_k :'+str(current_user.key())+', poster_k:'+str(thrd.poster.key())+', post in thrd.posts = '+str((pst.key() in [p.key() for p in thrd.posts])) )
        else : logging.error('Unable to find thread or post')

class ToggleSubscription(BaseHandler):
    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        mod = db.get(Key.from_path('Module', cgi.escape(self.request.get('mcode'))))
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        if mod :
            sub = Subscription.all()
            sub.filter('subscribed_user =', current_user)
            sub.filter('module =',mod)
            sub = sub.get()

            if sub:
                populate.unsubscribe(current_user, mod)
                self.response.out.write('Subscribe')
            else :
                populate.subscribe(current_user, mod, a=1)
                self.response.out.write('Unsubscribe')
        else: logging.error('Couldn\'t get module with mcode '+self.request.get('mcode'))


class ProfilePage(BaseHandler):

    def post(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
	'''Post Variables'''
        avatar = self.request.get('img')
        fullname = self.request.get('fullname')
	'''------------'''
	'''Get current user'''
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        user_key = current_user.key()
        user = db.get(user_key)
	'''----------------'''
        if len(avatar) >0:
            try:
                avatar=images.resize(avatar, 200, 200)#Resize and Upload Image if valid
                user.avatar = db.Blob(avatar)
            except Exception, err: self.redirect('/403')

        if len(fullname) >0: user.full_name = fullname

        user.put()
        self.redirect('/profile')

    def get(self):
	'''Check if user is logged in'''
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
	'''-------------'''
        edit_mode = False
        template = jinja_environment.get_template('templates/profile.html')

        current_user = db.get(Key.from_path('User',self.session.get('name')))
       

        sub_to_delete=cgi.escape(self.request.get('mod'))
        self.response.write(sub_to_delete)
        username = cgi.escape(self.request.get('usr'))

        if len(username) == 0:
            user_key = current_user.key()
            userQ=User.all()
            userQ=userQ.filter('__key__ = ' ,user_key)
            user = userQ.get()
            edit_mode=True
        else:
            user_key = Key.from_path('User',username)
            userQ=User.all()
            userQ=userQ.filter('__key__ = ' ,user_key)
            user = userQ.get()
            if user.key() == current_user.key(): edit_mode=True

        subs =  user.subscriptions
        mod_info=[]
        lecturers=[]
	'''Receive User Posts and Topics Created'''
        posts = Post.all()
        posts=posts.filter("poster",user_key)
        num_posts=posts.count()

        threads = Thread.all()
        threads = threads.filter("poster",user_key)
        created_threads = threads.count()
	''' ----------------------------------- '''
	
	'''Delete Module from subscription List'''
        if not sub_to_delete is '':
            subs.filter("__key__",Key(sub_to_delete))
            sub = subs.get()
            populate.unsubscribe(sub.subscribed_user, sub.module)
            subs =  current_user.subscriptions
	''' ------------------------------------ '''

	'''Retrieve User's Subscription List'''
        for s in subs:
            ratQ=Rating.all()
            ratQ.filter("module",s.module)
            for rat in ratQ:
                lectQ=Lecturer.all()
                lectQ.filter("__key__",rat.lecturer.key())
                lec=lectQ.get()
                lecturers.append(lec)
            if s.module.assessments.count()>0: assessments_flag=1
            else: assessments_flag=0
            mod_info.append(ModuleInfo(s.key(),s.module.key().name(),s.module.title,lecturers,assessments_flag))
	''' ---------------------------------- '''
        lecturers=[]

        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        template_params = { 'current_user':current_user,
                'user':user,
                'mod_info':mod_info,
                'subscriptions':subscribed_modules,
                'user_posts':num_posts,
                'user_threads':created_threads,
                'edit':edit_mode }

        self.response.out.write(template.render(template_params))

'''Displays an Image saved in the database so it can be included in an HTML Page'''
class GetImage(BaseHandler):
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        user_key = self.request.get('usr')
        user = db.get(user_key)
        if (user and user.avatar):
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(user.avatar)

class AboutPage(BaseHandler):

    def get(self):
        template = jinja_environment.get_template('templates/about.html')
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        parms = { 'current_user':current_user, 'subscriptions':subscribed_modules }
        self.response.out.write(template.render(parms))

class NotesPage(BaseHandler):

    def get(self):
        template = jinja_environment.get_template('templates/notes.html')
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]

        parms = { 'current_user':current_user, 'subscriptions':subscribed_modules }
        self.response.out.write(template.render(parms))

class ContactPage(BaseHandler):
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return
        subject=''
        current_user = db.get(Key.from_path('User',self.session.get('name')))
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        message=''
        template = jinja_environment.get_template('templates/contact.html')
        template_values = {'current_user':current_user,
                           'subject':'subject',
                           'message':'message',
                           'subscriptions':subscribed_modules }
        self.response.out.write(template.render(template_values))

class EmailSent(webapp2.RequestHandler):

    def post(self):
        self.request.get('subject')
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        template = jinja_environment.get_template('templates/something.html')
        subject = self.request.get('subject')
        message = self.request.get('message')
        mail.send_mail(sender="scriptingteamk@gmail.com", to='scriptingteamk@gmail.com', subject=subject, body=message)
        self.redirect("/contact")
       

class ModuleInfo:
    def __init__(self,sub_key,sub_code,sub_name,mod_lecturers,mod_assessments):
        self.sub_key=sub_key
        self.sub_code=sub_code
        self.sub_name=sub_name
        self.mod_lecturers=mod_lecturers
        self.mod_assessments=mod_assessments

class ModulesPage(BaseHandler):
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]

        homepage_subs = subscribed_modules

     
        course = current_user.course
        y1s1 = getYCS(1,course,1)
        y1s2 = getYCS(1,course,2)
        y2s1 = getYCS(2,course,1)
        y2s2 = getYCS(2,course,2)
        y3s1 = getYCS(3,course,1)
        y3s2 = getYCS(3,course,2)

        template_values = {'y1s1':y1s1,'y1s2':y1s2,'y2s1':y2s1,'y2s2':y2s2,'y3s1':y3s1,'y3s2':y3s2,'subscriptions':subscribed_modules,'current_user':current_user}
        template = jinja_environment.get_template('templates/modules.html')
        self.response.out.write(template.render(template_values))

class RssPage(BaseHandler):
    def get(self):
        if self.session.get('type')==-1:
            self.redirect('/403')
            return

        name, subs = current_user.full_name, current_user.subscriptions
        subs.filter('receive_notifications =', True)
        modules = [sub.module for sub in subs]
        date = time.strftime("%a, %d %b %Y %X %Z")
        items =  []
        for mod in modules:
            for cat in mod.categories:
                for thread in cat.threads:
		            items.append(rss_item(title=thread.subject, link="http://1.modulediscussionforum.appspot.com/showthread?tid="+str(thread.key().id()), description=mod.key().name(), category=cat.name, pub_date=thread.timestamp.strftime('%a, %d %b %Y %X %Z')))
        template_values = {'name':name, 'items':items, 'date':date}
        template = jinja_environment.get_template('templates/news.rss')
        self.response.headers['Content-Type'] = 'application/rss+xml'
        self.response.out.write(template.render(template_values))

class SearchPage(BaseHandler):
    def get(self):
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        template = jinja_environment.get_template('templates/search_page.html')
        self.response.out.write(template.render({'current_user':current_user, 'subscriptions':subscribed_modules}))

class SearchResults(BaseHandler):
    def get(self):
        subscribed_modules = [sub for sub in current_user.subscriptions if sub.show_in_homepage]
        query = self.request.get("search_terms")
        search_terms = query.split()
        results = search_thread_tags(search_terms)
        template = jinja_environment.get_template('templates/search_results.html')
        self.response.out.write(template.render({'current_user':current_user, 'results':results, 'subscriptions':subscribed_modules}))

class Logout(BaseHandler):
    def get(self):
        self.session.clear()
        self.redirect('/')

class FourOThree(BaseHandler):
    def get(self): self.response.out.write(""" <h1>403 Access is Forbidden</h1> <p>You are not allowed to access this webpage</p> """)

populate.populate_db()

#associate pages with classes in this file
app = webapp2.WSGIApplication([ ('/', SignInPage), ('/main', MainPage), ('/forum', ForumPage), ('/'+CATEGORIES,CategoriesPage), ('/threads',ViewAllThreadsPage), ('/showthread',ThreadPage), ('/newthread',NewThread), ('/createnewthread',CreateNewThread), ('/replythread',ReplyToThread), ('/replypost',ReplyToPost), ('/vup',VoteUpPost), ('/vdown',VoteDownPost), ('/solution',ToggleSolution), ('/subscriptions',ToggleSubscription ), ('/about', AboutPage), ('/notes', NotesPage), ('/contact',ContactPage), ('/something',EmailSent), ('/admin',AdminPage), ('/modules', ModulesPage), ('/admin-modules',AdminModules), ('/admin-users',AdminUsers), ('/profile',ProfilePage), ('/admin-user-creation',AdminUserCreation), ('/news.rss', RssPage), ('/profileimage',GetImage), ('/admin-edit-user', AdminEditUser), ('/logout',Logout), ('/403',FourOThree), ('/removeThread',removeThread), ('/search', SearchPage), ('/results',SearchResults), ('/admin-assessment',AdminAssessment) ], debug=True,config=session_dic)
