from google.appengine.ext import db
import YearCourseSemester

class Module(db.Model) :
	title = db.StringProperty(required=True)
	ecs_page = db.LinkProperty(required=True)
	yearCourseSemester = db.ReferenceProperty(YearCourseSemester.YearCourseSemester , collection_name='modules', required=True)
	student_count = db.IntegerProperty(default=0) #must be increamented every time a student subscribes (eg when creating Subscriptions in populate_db)
	sum_marks = db.IntegerProperty(default=0) #must be updated at every student's mark entry
