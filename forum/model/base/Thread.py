import Post
import Category
from google.appengine.ext import db

class Thread(db.Model) :
	category = db.ReferenceProperty(Category.Category, collection_name='threads' ,required=True)
	tags = db.ListProperty(str, required=True)
	subject = db.StringProperty(required=True)
        body = db.StringProperty(required=True)
        thread = db.ReferenceProperty(Thread.Thread, collection_name='posts', required=True)
        votes = db.IntegerProperty(required=True)
        poster = db.ReferenceProperty(User.User, collection_name='posts', required=True)
        timestamp = db.DateTimeProperty(auto_now_add=True, required=True) 
