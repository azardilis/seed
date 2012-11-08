from google.appengine.ext import db

class Module(db.Model) :
	code = db.StringProperty(required=True)
	title = db.StringProperty(required=True)
	home_page = db.LinkProperty(required=True)
	semester = db.IntegerProperty(required=True)
	year = db.IntegerProperty(required=True)
	#what should we put for course ?
	#course = db.StringProperty(required=True)
