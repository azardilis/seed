from model.base.Module import Module
from model.base.User import User
from model.base.Post import Post
from model.base.Thread import Thread
from model.base.YearCourseSemester import YearCourseSemester
from model.base.Lecturer import Lecturer
from model.base.Rating import Rating
from model.base.Assessment import Assessment
from model.base.Grade import Grade
from model.base.Category import Category
from model.base.Subscription import Subscription
from model.base.LecturerRating import LecturerRating
from google.appengine.ext import db
from google.appengine.ext.db import Key
from datetime import datetime

def reset_db():
    for user in User.all(): user.delete()

    for ycs in YearCourseSemester.all(): ycs.delete()

    for mod in Module.all(): mod.delete()

    for sub in Subscription.all(): sub.delete()

    for sub in Category.all(): sub.delete()

    for i in Thread.all(): i.delete()

    for i in Post.all(): i.delete()

    for i in Rating.all(): i.delete()

    for i in Assessment.all(): i.delete()

    for i in Grade.all(): i.delete()

    for i in Lecturer.all(): i.delete()

    for i in LecturerRating.all(): i.delete()

def populate_db():

    ###### RESET #######
    reset_db()

    ###### POPULATE ######
    # create admins (course should match course in YearCourseSemester objects)
    current_user = User(key_name='az2g10', full_name='Argyris Zardilis', password='1234', course='compsci',user_type=1, year=3, signature="L33T 5UP4|-| H4X0|2")
    current_user.put()

    # create yearCourseSemester objects
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

    # create modules
    comp3001 = Module(key_name = 'COMP3001', ecsCode='COMP3001', title='Scripting Languages',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP3001/", yearCourseSemester=compsci31)
    comp3001.put()
    info3005 = Module(key_name = 'INFO3005', ecsCode='INFO3005', title='Security & Information Technology',
                  ecs_page='http://www.google.com',  yearCourseSemester=compsci31)
    info3005.put()
    comp3033 = Module(key_name = 'COMP1202', ecsCode='COMP1202', title='Programming 1',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP1202/", yearCourseSemester=compsci11)
    comp3033.put()
    comp3033 = Module(key_name = 'COMP1201', ecsCode='COMP1201', title='Algorithmics',
                  ecs_page="https://secure.ecs.soton.ac.uk/module/1213/COMP1201/", yearCourseSemester=compsci12)
    comp3033.put()

    # put assessments on modules
    cwk1_3001 = Assessment(title='Perl Coursework',  module=comp3001,
                        dueDate=datetime.strptime('Nov 1 2013  1:33PM', '%b %d %Y %I:%M%p'),
                        specLink=db.Link("https://secure.ecs.soton.ac.uk/noteswiki/w/COMP3001-1213-cw1-spec"),
                        handin=db.Link("https://handin.ecs.soton.ac.uk/handin/1213/COMP3001/1/"))
    cwk1_3001.put()
    cwk2_3001 = Assessment(title='Python/JS Group',  module=comp3001,
                        dueDate=datetime.strptime('Nov 1 2013  2:00PM', '%b %d %Y %I:%M%p'),
                        specLink=db.Link("https://secure.ecs.soton.ac.uk/noteswiki/w/COMP3001-1213-cw2-spec"),
                        handin=db.Link("https://handin.ecs.soton.ac.uk/handin/1213/COMP3001/2/"))
    cwk2_3001.put()
    infocwk = Assessment(title='Assignment',  module=info3005,
                        dueDate=datetime.strptime('Nov 1 2012  2:00PM', '%b %d %Y %I:%M%p'),
                        specLink=db.Link("https://secure.ecs.soton.ac.uk/noteswiki/w/INFO3005-1213-assign2"),
                        handin=db.Link("https://handin.ecs.soton.ac.uk/handin/1213/INFO3005/2/"))
    infocwk.put()

    # create lecturers
    ejz = Lecturer(key_name='ejz1', full_name='Ed J Zaluska', home_page='https://secure.ecs.soton.ac.uk/people/ejz')
    ejz.put()
    jsh2 = Lecturer(key_name='jsh2', full_name='Dr Jonathon S Hare', home_page='https://secure.ecs.soton.ac.uk/people/jsh2')
    jsh2.put()

    # associate them to modules they teach
    associate(lecturer=ejz, module=comp3001)
    associate(lecturer=jsh2,module=comp3001)
    associate(lecturer=ejz,module=info3005)

    # create categories
    categGeneral3001 = Category(name='General Discussion', description='Discuss general issues with the module', module=comp3001)
    categGeneral3001.put()
    categCoursework3001 = Category(name='Coursework Discussion', description='Questions related to coursework', module=comp3001)
    categCoursework3001.put()
    categGeneral3005 = Category(name='General Discussion', description='Discuss general issues with the module', module=info3005)
    categGeneral3005.put()
    categCoursework3005 = Category(name='Coursework Discussion', description='Questions related to coursework', module=info3005)
    categCoursework3005.put()

    # sample threads
    Thread(category=categGeneral3001,subject='Java support functional',body='Does Java support functional programming?',poster=current_user,tags=['java','functional']).put()

    Thread(category=categGeneral3001,subject='Python typing',body='Is Python strongly typed?',poster=current_user,tags=['python','strongly typed']).put()

    Thread(category=categCoursework3001,subject='Deadline',body='Hi guys. When is the deadline for Javascript?',poster=current_user,tags=['deadline'])

def subscribe(user, module, a=0):
	Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=user, module=module).put()

	module.student_count+=1
	module.put()

	for assessm in module.assessments: Grade(student=user,assessment=assessm).put() 
	
	ratings=Rating.all().filter('module =', module).run()
	for rating in ratings: LecturerRating(lecturer=rating.lecturer,module=module,student=user).put()

def unsubscribe(user, module):
	subs=Subscription.all().filter('subscribed_user =', user).filter('module =', module).run()
	for s in subs: s.delete()

	module.student_count-=1
	module.put()

	grades=Grade.all().filter('student =', user).run()

	for assessm in module.assessments:
		for grade in grades:
			if grade.assessment.key() == assessm.key(): 
				grade.delete()

	lectRats=LecturerRating.all().filter('module =',module).filter('user =',user).run()
        for lectRat in lectRats: lectRat.delete()

def associate(lecturer, module):
	Rating(lecturer=lecturer,module=module).put()

def associate(lecturer, module):
	rating = Rating(lecturer=lecturer,module=module)
	rating.teach_sum = 5
	rating.overall_sum = 4
	rating.teach_count = rating.overall_count = 1
	rating.put()
