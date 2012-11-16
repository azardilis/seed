from google.appengine.ext import db
import Module

class Category(db.Model) :
	name = db.StringProperty(required=True)
	description = db.StringProperty(required=True)
	module = db.ReferenceProperty(Module.Module, collection_name='categories',required=True)
