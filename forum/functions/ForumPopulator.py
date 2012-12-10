import logging
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
    for i in range(3):
    	p = Post(body='yada'+str(i),poster=rg, thread=t, answer = False)
	p.put()
	for g in range(1,4) :
    		n = Post(body='yada2'+str(g),poster=rg,reply=p ,  answer = False)
		n.put()
    		o = Post(body='yada2'+str(g),poster=rg,reply=p ,  answer = False)
		o.put()

    		r = Post(body='yadayada3',poster=rg, reply=n, answer = False)
		r.put()
    r = Post(body='#This has no replies ',poster=rg, thread = t, answer = False)
    r.put()
		

#this function will handle the parent child relationships and git out 
def get_posts(tid):
    t = Thread.get_by_id(int(tid))
    p = [p for p in t.posts]
    return p 

def get_children(plist , posts):
	
	for p in plist :
		posts = make_article(posts)
		posts = make_post(p,posts)

		if p.replies : 
			posts = make_section(posts)
			for r in p.replies :
				a = list ()
				a.append(r)
				posts = get_children(a,posts)
			posts = close_section(posts)
		posts = close_article(posts)

	return posts

def make_article(posts):
	posts += '<article class="post">'
	return posts 

def close_article(posts):
	posts += '</article>'	
	return posts

def make_section(posts):
	posts +='<section class="posts">'	
	return posts

def close_section(posts) :
	posts += '</section>'
	return posts

def make_post(p,posts) :
	posts += p.body
	return posts
	
