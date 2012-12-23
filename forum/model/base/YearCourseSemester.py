from google.appengine.ext import db

class YearCourseSemester(db.Model):
	year = db.IntegerProperty(required=True)
	semester = db.IntegerProperty(required=True)
	course = db.StringProperty(required=True)
	prettyName=db.StringProperty(required=False)
