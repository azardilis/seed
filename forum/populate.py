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
    current_user = User(key_name='az2g10', full_name='Argyris Zardilis', password='1234', course='compsci',user_type="moderator", year=3, signature="L33T 5UP4|-| H4X0|2")
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

    subscribe(user, comp3001)
    subscribe(current_user, comp3001)
    subscribe(current_user,comp3033)
    subscribe(current_user,comp3032)
    subscribe(current_user,comp3020)
    subscribe(current_user,comp1314)
    subscribe(current_user, info3005)
    subscribe(current_user, comp3016)

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

    Grade(student=current_user, assessment=cwk1_3001).put() 
    Grade(student=current_user, assessment=cwk2_3001).put()

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

    rating1 = Rating(lecturer=ejz,module=comp3001)
    rating1.put()
    rate_lecturer(rating1,2,1)
    rating2 = Rating(lecturer=msn,module=comp3001)
    rating2.put()
    rate_lecturer(rating2,3,4)
    rating3 = Rating(lecturer=ejz,module=info3005)
    rating3.put()
    rate_lecturer(rating3,3,2)

    LecturerRating(lecturer=ejz,module=comp3001,student=current_user).put()
    LecturerRating(lecturer=msn,module=comp3001,student=current_user).put()
    LecturerRating(lecturer=ejz,module=info3005,student=current_user).put()

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

def subscribe(user, module):
	Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=user, module=module).put()
	module.student_count+=1
	module.put()

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

