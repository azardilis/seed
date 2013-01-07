from google.appengine.ext import db
import YearCourseSemester
from SchoolYear import SchoolYear

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
	
