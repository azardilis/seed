from google.appengine.ext import db
import YearCourseSemester

class Module(db.Model) :
	title = db.StringProperty(required=True)
	ecs_page = db.LinkProperty(required=True)
	yearCourseSemester = db.ReferenceProperty(YearCourseSemester.YearCourseSemester , collection_name='modules', required=True)
