from google.appengine.ext import db
import Lecturer
import User
import Module

class LecturerRating(db.Model) : 
	lecturer = db.ReferenceProperty(Lecturer.Lecturer, collection_name='lecturerRatings',required=True)
	student = db.ReferenceProperty(User.User, collection_name='lecturerRatings',required=True)
	module = db.ReferenceProperty(Module.Module, collection_name='lecturerRatings',required=True)

	voted = db.BooleanProperty(default=False)
