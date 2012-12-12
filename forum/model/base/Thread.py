import User
import Category
from google.appengine.ext import db

class Thread(db.Model) :
	category = db.ReferenceProperty(Category.Category,required=True, collection_name='threads')
	tags = db.ListProperty(str, required=True)
	subject = db.StringProperty(required=True,multiline=True)
        body = db.StringProperty(required=True)
        votes = db.IntegerProperty(default=0)
        poster = db.ReferenceProperty(User.User, collection_name='threads', required=True)
        timestamp = db.DateTimeProperty(auto_now_add=True) 
