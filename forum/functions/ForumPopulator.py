from google.appengine.ext.db import Key
from google.appengine.ext import db
from model.base.Thread import Thread
from model.base.Post import Post
from model.base.User import User

def populate_forum():
    q = User.all();
    q.filter('__key__ =',Key.from_path('User','az2g10'))
    rg = q.get()

    for post in Post.all():
    	post.delete()

    for thread in Thread.all():
    	thread.delete()

    t = Thread(subject='Some subject',body='Some very intriguing text!',poster=rg,tags=['yada','yada'])
    t.put()
    for i in range(15):
    	p = Post(body='yada'+str(i),poster=rg, thread=t, answer = False)
	p.put()

def get_posts(tid):
    pass
