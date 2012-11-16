from google.appengine.ext import db
import Module

class Assessment(db.Model) :
	title = db.StringProperty(required=True)
	dueDate = db.DateTimeProperty(required=True)
	specLink = db.LinkProperty(required=True)
	handin = db.LinkProperty(required=True)
	module = db.ReferenceProperty(Module.Module, collection_name='assessments', required=True)
