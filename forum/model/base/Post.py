from google.appengine.ext import db
import Thread
import User
import Post 

class Post(db.Model) :
	body = db.StringProperty(required=True,multiline=True)
	thread = db.ReferenceProperty(Thread.Thread, collection_name='posts')
	votes = db.IntegerProperty(default=0)
	reply = db.SelfReferenceProperty(collection_name = 'replies');
	poster = db.ReferenceProperty(User.User, collection_name='posts', required=True)
	timestamp = db.DateTimeProperty(auto_now_add=True)
	answer = db.BooleanProperty(default=False)
