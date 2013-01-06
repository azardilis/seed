from google.appengine.ext import db

class SchoolYear(db.Model) :
	start = db.IntegerProperty(required=True)
	end = db.IntegerProperty(required=True)
	pretty_print = str(start) + '/' + str(end)
