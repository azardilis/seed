import Post
import Category
from google.appengine.ext import db

class Thread(Post.Post) :
	category = db.ReferenceProperty(Category.Category, collection_name='threads' ,required=True)
	tags = db.ListProperty(str, required=True)
