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

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

global current_user


def getYCS(year, course, semester):
    ycs_list = YearCourseSemester.all()
    ycs_list.filter('year =', year)
    ycs_list.filter('course =', course)
    ycs_list.filter('semester =', semester)
    ycs = ycs_list.get()
    return ycs.modules

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
            ratings = module.lecturers
            #subscribed = module.subscribed_users

            for c in categs :
                ct = c.threads.order('-timestamp').fetch(2) #just to limit what is fetched, later change to 10
                l = [c,ct]
                complete.append(l)

            template_values= {
                    'complete' : complete,
                    'ratings' : ratings,
                    #'subscribed' : subscribed
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

	    thrd.answers += 1 
	    thrd.put()

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
    current_user = User(key_name='az2g10', full_name='Argyris Zardilis', password='1234', course='BSc Computer Science', year=3,avatar="resources/img/dio.jpg", signature="L33T 5UP4|-| H4X0|2")
    current_user.put()

    user = User(key_name='dpm3g10',full_name='dio',password='1234',course='cs',year=3)
    user.put()

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
    comp1314 = Module(key_name='comp1314', title='Introduction to Everything',
                  ecs_page='http://goo.gl/S0e62',
                  yearCourseSemester=compsci11)
    comp1314.put()
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
                                   ('/profile',ProfilePage)
                                ], debug=True)
