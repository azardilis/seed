from functions.RetrieveFunctions import *
import os
import cgi
from populate import *
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
from model.base.SchoolYear import SchoolYear
from google.appengine.ext.db import Key
from google.appengine.ext import db
from itertools import izip
from datetime import datetime
import PyRSS2Gen


def reset_db():
    for user in User.all():
        user.delete()

    for ycs in YearCourseSemester.all():
        ycs.delete()

    for i in SchoolYear.all():
        i.delete()

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

    for i in LecturerRating.all():
        i.delete()

def populate_db():

    ###### RESET #######
    reset_db()

    ###### POPULATE ######

    # create admins (course should match course in YearCourseSemester objects)
    current_user = User(key_name='az2g10', full_name='Argyris Zardilis', password='1234', course='compsci',user_type=1, year=3, signature="L33T 5UP4|-| H4X0|2")
    current_user.put()

    #temp:
    user = User(key_name='dpm3g10',full_name='dio',password='1234',course='compsci',year=3,user_type=0)
    user.put()
    #end_temp

    # create yearCourseSemester objects (how about semester 3 - individual project for masters ??)
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
    # +year 4 

    #temp:
    y1213 = SchoolYear(start=int(2012), end=int(2013))
    y1213.put()

    y1112 = SchoolYear(start=int(2011), end=int(2012))
    y1112.put()
    #end_temp

    # create modules (schoolYear, ecsCode ??)
    comp3001 = Module(key_name = 'COMP3001', ecsCode='COMP3001', title='Scripting Languages',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3001/",
                  yearCourseSemester=compsci31, schoolYear=y1213)
    comp3001.put()
    comp3033 = Module(key_name = 'COMP3033', ecsCode='COMP3033', title='Computational Biology',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3033/",
                  yearCourseSemester=compsci31, schoolYear=y1213)
    comp3033.put()
    comp3032 = Module(key_name = 'COMP3032', ecsCode='COMP3032', title='Intelligent Algorithms',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3032/",
                  yearCourseSemester=compsci31, schoolYear=y1213)
    comp3032.put()
    comp3016 = Module(key_name = 'COMP3016', ecsCode='COMP3016', title='Hypertext and Web Technologies',
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31, schoolYear=y1213)
    comp3016.put()
    comp3020 = Module(key_name = 'COMP3020', ecsCode='COMP3020', title='Individual Project',
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31, schoolYear=y1213)
    comp3020.put()
    comp1314 = Module(key_name = 'COMP1314', ecsCode='COMP1314', title='Introduction to Everything',
                  ecs_page='http://goo.gl/S0e62',
                  yearCourseSemester=compsci11, schoolYear=y1213)
    comp1314.put()
    info3005 = Module(key_name = 'INFO3005', ecsCode='INFO3005', title='Security & Information Technology',
                  ecs_page='http://www.google.com',
                  yearCourseSemester=compsci31, schoolYear=y1213)
    info3005.put()

# what happens if we put some modules for more than one years:
#    old3001 = Module(key_name = 'other3001', ecsCode='COMP3001', title='Scripting Languages',
#                  ecs_page="https://secure.ecs.soton.ac.uk/module/1112/COMP3001/",
#                  yearCourseSemester=compsci31, schoolYear=y1112)
#    old3001.put()
#    old3033 = Module(key_name = 'other3033', ecsCode='COMP3033', title='Computational Biology',
#                 ecs_page="https://secure.ecs.soton.ac.uk/module/1112/COMP3033/",
#                  yearCourseSemester=compsci31, schoolYear=y1112)
#    old3033.put()
#    subscribe(current_user, old3001)
#    subscribe(current_user, old3033)
#############################################################

    # put assessments on modules
    cwk1_3001 = Assessment(title='Perl Coursework',
                        dueDate=datetime.strptime('Nov 1 2005  1:33PM', '%b %d %Y %I:%M%p'),
                        specLink=db.Link("http://www.google.com/"),
                        handin=db.Link("http://www.google.com/"),
                        module=comp3001)
    cwk1_3001.put()
    cwk2_3001 = Assessment(title='Python/JS Group',
                        dueDate=datetime.strptime('Nov 1 2005  1:33PM', '%b %d %Y %I:%M%p'),
                        specLink=db.Link("http://www.google.com/"),
                        handin=db.Link("http://www.google.com/"),
                        module=comp3001)
    cwk2_3001.put()

    #temp: 
    put_mark(current_user, cwk1_3001, 83)
    put_difficulty(current_user, cwk1_3001, 3)
    put_interest(current_user, cwk1_3001, 3)
    put_mark(user, cwk1_3001, 56)
    put_difficulty(user, cwk1_3001, 2)
    put_interest(user, cwk1_3001, 2)
    put_mark(current_user, cwk2_3001, 40)
    put_difficulty(current_user, cwk2_3001, 4)
    put_interest(current_user, cwk2_3001, 4)
    put_mark(user, cwk2_3001, 65)
    put_difficulty(user, cwk2_3001, 5)
    put_interest(user, cwk2_3001, 5)
    #end_temp

    # create lecturers
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

    # associate them to modules they teach
    rating1 = associate(lecturer=ejz, module=comp3001)
    rating2 = associate(lecturer=msn,module=comp3001)
    rating3 = associate(lecturer=ejz,module=info3005)

    #temp:
    rate_lecturer(rating1,2,1)
    rate_lecturer(rating2,3,4)
    rate_lecturer(rating3,3,2)
    #end_temp

    # when user subscribes to amodule, call this function (make sure it's after lecturer-module associations (ie. Ratings) have been created)
    subscribe(user, comp3001)
    subscribe(current_user, comp3001)
    subscribe(current_user,comp3033)
    subscribe(current_user,comp3032)
    subscribe(current_user,comp3020)
    subscribe(current_user,comp1314)
    subscribe(current_user, info3005)
    subscribe(current_user, comp3016)

    #temp:
    LecturerRating(lecturer=ejz,module=comp3001,student=current_user).put()
    LecturerRating(lecturer=msn,module=comp3001,student=current_user).put()
    LecturerRating(lecturer=ejz,module=info3005,student=current_user).put()
    #end_temp

    ###### FORUM #######
#TODO iterate over all assessments in each module and create one category for each + 1 general category at the end
#when the above todo is done, make sure that when the admin adds a new module they call a function to add categories to it as well
    categGeneral3001 = Category(name='General Discussion', description='blah blah', module=comp3001)
    categGeneral3001.put()
    categCoursework3001 = Category(name='Coursework Discussion', description='blah blah', module=comp3001)
    categCoursework3001.put()

    #temp:
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
    #end_temp

def subscribe(user, module, a=0):
	Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=user, module=module).put()

	module.student_count+=1
	module.put()

	for assessm in module.assessments:
		Grade(student=user,assessment=assessm).put() 
	
	q=Rating.all()
	q=q.filter('module =', module)
	ratings=q.run()
	for rating in ratings:
		LecturerRating(lecturer=rating.lecturer,module=module,student=user).put()

def unsubscribe(user, module):
	q=Subscription.all()
	q=q.filter('subscribed_user =', user)
	q=q.filter('module =', module)
	subs=q.run()
	for s in subs:
		s.delete()

	module.student_count-=1
	module.put()

	q=Grade.all()
	q=q.filter('student =', user)
	grades=q.run()

	for assessm in module.assessments:
		for grade in grades:
			if grade.assessment.key() == assessm.key():
				grade.delete()

	q=LecturerRating.all()
        q=q.filter('module =', module)
	q=q.filter('user =', user)
        lectRats=q.run()
        for lectRat in lectRats:
		lectRat.delete()

def associate(lecturer, module):
	rating = Rating(lecturer=lecturer,module=module)
	rating.put()
	return rating #temp

#temp:
def put_mark(user, assessment, mark):
 	assessment.sum_marks += mark
	assessment.count_marks += 1
	assessment.put()
	assessment.module.sum_marks += mark
	assessment.module.count_marks += 1
	assessment.module.put()

def put_difficulty(user, assessment, difficulty_outof5):
 	assessment.sum_difficulty += difficulty_outof5
	assessment.count_difficulty += 1
	assessment.put()
	assessment.module.sum_difficulty += difficulty_outof5
	assessment.module.count_difficulty += 1
	assessment.module.put()

def put_interest(user, assessment, interest_outof5):
 	assessment.sum_interest += interest_outof5
	assessment.count_interest += 1
	assessment.put()
	assessment.module.sum_interest += interest_outof5
	assessment.module.count_interest += 1
	assessment.module.put()

def rate_lecturer(rating, teaching_outof5, overall_outof5):
	rating.teach_sum += teaching_outof5
	rating.teach_count += 1
	rating.overall_sum += overall_outof5
	rating.overall_count += 1
	rating.put()
#end_temp
