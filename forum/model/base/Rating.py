from google.appengine.ext import db
import Lecturer
import Module

class Rating(db.Model) : 
	lecturer = db.ReferenceProperty(Lecturer.Lecturer, collection_name='modules',required=True)
	module = db.ReferenceProperty(Module.Module, collection_name='lecturers',required=True)
	teach_sum = db.IntegerProperty(default=0)
	overall_count = db.IntegerProperty(default=0)
	overall_sum = db.IntegerProperty(default=0)
	teach_count = db.IntegerProperty(default=0)
