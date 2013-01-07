from google.appengine.ext import db

class Lecturer(db.Model) :
	full_name = db.StringProperty(required=True)
	home_page = db.LinkProperty(required=True)
