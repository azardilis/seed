from google.appengine.ext import db

class User(db.Model):
	
	#implicit key_name (use for username)
	password = db.StringProperty(required=True)
	
	user_type = db.IntegerProperty(choices=set([0,1,-1]), default = 0)
	#0 is for a normal user, 1 for a mod and -1 for a user who is not logged in
	activated = db.BooleanProperty(default=False)
	
	course = db.StringProperty(required=True)
	year = db.IntegerProperty(required=True)
	#consider reference to yearCourseSemester instead
		
	full_name = db.StringProperty(required=True)
	avatar = db.BlobProperty(default=None)
	signature = db.StringProperty()
	karma = db.IntegerProperty(default=0)
	home_page  = db.LinkProperty()
	alternative_email = db.EmailProperty()
