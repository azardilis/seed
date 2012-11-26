from model.base.User import User
from google.appengine.ext.db import Key
from google.appengine.ext import db


def get_modules(user) : 
	subjects = [sub for sub in user.subscriptions if sub.show_in_homepage ]

