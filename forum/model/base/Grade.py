from google.appengine.ext import db
import Assessment
import User

student = db.ReferenceProperty(User.User, collection_name='grades', required=True)
assessmentSubject = db.ReferenceProperty(Assessment.Assessment, collection_name='grades',required=True)
mark = db.IntegerProperty(required=True)