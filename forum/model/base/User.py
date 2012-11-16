from google.appengine.ext import db

class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	course = db.StringProperty(required=True)
	signature = db.StringProperty(required=False)
	user_type = db.StringProperty(required=True, choices=set(['normal','moderator']))
	#karma = db.IntegerProperty(required=True)
	#alternative_email = db.emailProperty(required=True)
	#home_page  = db.LinkProperty(required=True)
	#avatar = db.LinkProperty()
	#activated = db.BooleanProperty(default=False)
	year = db.IntegerProperty(required=True)
