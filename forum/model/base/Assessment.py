from google.appengine.ext import db
import Module

class Assessment(db.Model) :
	title = db.StringProperty(required=True)
	dueDate = db.DateTimeProperty(required=True)
	specLink = db.LinkProperty() #could be an exam
	handin = db.LinkProperty()
	module = db.ReferenceProperty(Module.Module, collection_name='assessments', required=True)
