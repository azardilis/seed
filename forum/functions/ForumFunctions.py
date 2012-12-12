import re
from model.base.Thread import Thread
from model.base.User import User
from model.base.Post import Post

def nl2br(txt) :
	return re.sub(r'(\r\n|\n\r|\n|\r)','<br/>',txt)

def get_posts(tid):
    t = Thread.get_by_id(int(tid))
    #the bit below only fetches the 10 most recent posts 
    p = [p for p in t.posts.order('-timestamp').fetch(10)]
    return p 

def get_children(plist , posts):
	
	for p in plist :
		posts = make_article(posts)
		posts = make_post(p,posts)
		posts = make_toolbar(p,posts)

		if len(p.replies.fetch(1) ) > 0 : #little dirty hack to check if any responses exist
			posts = make_section(posts)
			for r in p.replies :
				a = list ()
				a.append(r)
				posts = get_children(a,posts)
			posts = close_section(posts)
		posts = close_article(posts)

	return posts

def make_toolbar(p,posts):
	pid = str(p.key().id())
	html =''' 
	<section id="class">
		<span class="controls">
			<p class="reply" pid="'''+pid+'''">Reply</p>
			<p class="quote" pid="'''+pid+'''">Quote</p>
			<p class="voteup" pid="'''+pid+'''">Vote Up</p>
			<p class="votedown" pid="'''+pid+'''">Vote Down</p>
		</span>
			<form id="rf'''+pid+'''" class="replyform" method="post" action="postreply">
				<input type="hidden" value="'''+pid+'''" name="r2pid">
				<textarea name="replybox" rows="5" cols="50"></textarea>
				<input type="submit" value="Reply">
			</form>
	</section>
	'''
	return posts+html

def make_article(posts):
	posts += '<section class="post">'
	return posts 

def close_article(posts):
	posts += '</section>'	
	return posts

def make_section(posts):
	posts +='<section class="posts">'	
	return posts

def close_section(posts) :
	posts += '</section>'
	return posts

#make show all the deatils here)
def make_post(p,posts) :
	posts += '<article class="art" poster="'+p.poster.key().name()+'" pid='+str(p.key().id())+' id="'+str(p.key().id())+'">'+nl2br(p.body)+'</article>'
	return posts
	
