from google.appengine.ext import db
import Assessment
import User

class Grade(db.Model) :
    student = db.ReferenceProperty(User.User, collection_name='grades', required=True)
    assessment = db.ReferenceProperty(Assessment.Assessment, collection_name='grades',required=True)

    voted = db.BooleanProperty(default=False)
    marked = db.BooleanProperty(default=False)

