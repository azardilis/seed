import re
from model.base.Thread import Thread
from model.base.User import User
from model.base.Post import Post

def nl2br(txt) :
	return re.sub(r'(\n|\r|\r\n|\n\r)','<br/>',txt)

def get_posts(tid):
    t = Thread.get_by_id(int(tid))
    #the bit below only fetches the 10 most recent posts 
    p = [p for p in t.posts.order('-timestamp').fetch(10)]
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
	posts += nl2br(p.body)
	return posts
	
