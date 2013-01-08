from google.appengine.ext import db
import Thread
import User
import Post
import Module 
import Assessment
import YearCourseSemester
from SchoolYear import SchoolYear
import Lecturer

class Post(db.Model) :
	body = db.StringProperty(required=True,multiline=True)
	thread = db.ReferenceProperty(Thread.Thread, collection_name='posts')
	votes = db.IntegerProperty(default=0)
	reply = db.SelfReferenceProperty(collection_name = 'replies');
	poster = db.ReferenceProperty(User.User, collection_name='posts', required=True)
	timestamp = db.DateTimeProperty(auto_now_add=True)
	answer = db.BooleanProperty(default=False)


class Assessment(db.Model) :
	title = db.StringProperty(required=True)
	dueDate = db.DateTimeProperty(required=True)
	specLink = db.LinkProperty() #could be an exam
	handin = db.LinkProperty()
	sum_marks = db.IntegerProperty(default=0)
	count_marks = db.IntegerProperty(default=0)
	sum_difficulty = db.IntegerProperty(default=0)
	count_difficulty = db.IntegerProperty(default=0)
	sum_interest = db.IntegerProperty(default=0)
	count_interest = db.IntegerProperty(default=0)
	module = db.ReferenceProperty(Module.Module, collection_name='assessments', required=True)


class Lecturer(db.Model) :
	full_name = db.StringProperty(required=True)
	home_page = db.LinkProperty(required=True)

class SchoolYear(db.Model) :
	start = db.IntegerProperty(required=True)
	end = db.IntegerProperty(required=True)
	pretty_print = str(start) + '/' + str(end)




class Grade(db.Model) :
    student = db.ReferenceProperty(User.User, collection_name='grades', required=True)
    assessment = db.ReferenceProperty(Assessment.Assessment, collection_name='grades',required=True)

    voted = db.BooleanProperty(default=False)
    marked = db.BooleanProperty(default=False)


class Subscription(db.Model):
	show_in_homepage = db.BooleanProperty(default=False)
	receive_notifications = db.BooleanProperty(default=True)
	subscribed_user = db.ReferenceProperty(User.User, collection_name='subscriptions', required=True)
	module = db.ReferenceProperty(Module.Module,required=True,collection_name='registered_students')


class Module(db.Model) :
	title = db.StringProperty(required=True)
	ecsCode = db.StringProperty(required=False)
	ecs_page = db.LinkProperty(required=True)
	yearCourseSemester = db.ReferenceProperty(YearCourseSemester.YearCourseSemester , collection_name='modules', required=True)
	student_count = db.IntegerProperty(default=0) #must be increamented every time a student subscribes (eg when creating Subscriptions in populate_db)
	schoolYear = db.ReferenceProperty(SchoolYear, collection_name='modules', required=False)

	sum_marks = db.IntegerProperty(default=0)
	count_marks = db.IntegerProperty(default=0)
	sum_difficulty = db.IntegerProperty(default=0)
	count_difficulty = db.IntegerProperty(default=0)
	sum_interest = db.IntegerProperty(default=0)
	count_interest = db.IntegerProperty(default=0)
	

class LecturerRating(db.Model) : 
	lecturer = db.ReferenceProperty(Lecturer.Lecturer, collection_name='lecturerRatings',required=True)
	student = db.ReferenceProperty(User.User, collection_name='lecturerRatings',required=True)
	module = db.ReferenceProperty(Module.Module, collection_name='lecturerRatings',required=True)

	voted = db.BooleanProperty(default=False)
class User(db.Model):
	
	#implicit key_name (use for username)
	password = db.StringProperty(required=True)
	
	user_type = db.IntegerProperty(choices=set([0,1,-1]), default = 0)
	#0 is for a normal user, 1 for a mod and -1 for a user who is not logged in
	activated = db.BooleanProperty(default=False)
	
	course = db.StringProperty(required=True)
	year = db.IntegerProperty(required=True)
	#consider reference to yearCourseSemester instead
		
	full_name = db.StringProperty(required=True)
	avatar = db.BlobProperty(default=None)
	signature = db.StringProperty()
	karma = db.IntegerProperty(default=0)
	home_page  = db.LinkProperty()
	alternative_email = db.EmailProperty()


class Vote(db.Model):
	user = db.ReferenceProperty(User.User,required=True,collection_name='votes')
	post = db.ReferenceProperty(Post.Post, required=True, collection_name='voters')
	value= db.IntegerProperty(required=True,choices=set([1,-1]))
