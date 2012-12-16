from google.appengine.ext import db

class User(db.Model):
	
	#implicit key_name (use for username)
	password = db.StringProperty(required=True)
	
	user_type = db.StringProperty(choices=set(['normal','moderator']), default = 'normal')
	activated = db.BooleanProperty(default=False)
	
	course = db.StringProperty(required=True)
	year = db.IntegerProperty(required=True)
	#consider reference to yearCourseSemester instead
		
	full_name = db.StringProperty(required=True)
	avatar = db.StringProperty()
	signature = db.StringProperty()
	karma = db.IntegerProperty(default=0)
	home_page  = db.LinkProperty()
	alternative_email = db.EmailProperty()
