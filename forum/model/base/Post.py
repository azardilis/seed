from google.appengine.ext import db
import Thread
import User




class Post(db.Model) :
	subject = db.StringProperty(required=True)
	body = db.StringProperty(required=True)
	thread = db.ReferenceProperty(Thread.Thread, collection_name='posts', required=True)
	votes = db.IntegerProperty(required=True)
	poster = db.ReferenceProperty(User.User, collection_name='posts', required=True)
	timestamp = db.DateTimeProperty(auto_now_add=True, required=True)
	answer = db.BooleanProperty(required=True)
	
	
