from google.appengine.ext import db
import YearCourseSemester

class Module(db.Model) :
	code = db.StringProperty(required=True)
	title = db.StringProperty(required=True)
	ecs_page = db.LinkProperty(required=True)
	semester = db.IntegerProperty(required=True)
	yearCourseSemester = db.ReferenceProperty(YearCourseSemester.YearCourseSemester , collection_name='modules', required=True)