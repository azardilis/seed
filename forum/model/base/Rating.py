from google.appengine.ext import db
import Lecturer
import Module

class Rating(db.Model) : 
	lecturer = db.ReferenceProperty(Lecturer.Lecturer, collection_name='modules',required=True)
	module = db.ReferenceProperty(Module.Module, collection_name='lecturers',required=True)
	totalSum = db.IntegerProperty(required=True)
	totalVotes = db.IntegerProperty(required=True)
