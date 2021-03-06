from google.appengine.ext import db
import User
import Module

class Subscription(db.Model):
	show_in_homepage = db.BooleanProperty(default=False)
	receive_notifications = db.BooleanProperty(default=True)
	subscribed_user = db.ReferenceProperty(User.User, collection_name='subscriptions', required=True)
	module = db.ReferenceProperty(Module.Module,required=True,collection_name='registered_students')
