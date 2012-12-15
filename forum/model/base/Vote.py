from google.appengine.ext import db
import Post
import User

class Vote(db.Model):
	user = db.ReferenceProperty(User.User,required=True,collection_name='votes')
	post = db.ReferenceProperty(Post.Post, required=True, collection_name='voters')
	value= db.IntegerProperty(required=True,choices=set([1,-1]))
