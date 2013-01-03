import re
from model.base.Thread import Thread
from model.base.User import User
from model.base.Post import Post

def nl2br(txt) :
	return re.sub(r'(\r\n|\n\r|\n|\r)','<br/>',txt)

def get_posts(tid):
    t = Thread.get_by_id(int(tid))
    #the bit below only fetches the 10 most recent posts 
    p = [p for p in t.posts.order('-answer').order('-timestamp').fetch(10)]
    return p 

def get_children(plist , posts, lvl,usrstat,user):
	
	for p in plist :
		cls = 'post'
		if p.answer :
			cls = 'ans'
		posts = make_article(posts,cls,p)
		posts = make_post(p,posts)
		posts = make_toolbar(p,posts,lvl,usrstat,user.key().name())

		if len(p.replies.fetch(1) ) > 0 : #little dirty hack to check if any responses exist
			posts = make_section(str(p.key().id()),posts)
			for r in p.replies :
				a = list ()
				a.append(r)
				posts = get_children(a,posts, lvl+1,usrstat,user)
			posts = close_section(posts)
		posts = close_article(posts)

	return posts

def make_toolbar(p,posts,lvl,userstat,uname):
	pid = str(p.key().id())

	html =''' 
		<section id="controls">
			<section class="controlButtons">
				<p class="score" pid="'''+pid+'''">'''+str(p.votes)+'''</p>
				<p class="reply" pid="'''+pid+'''">Reply</p>
				<p class="quote" pid="'''+pid+'''">Quote</p>
				<p class="vote" url="/vup" pid="'''+pid+'''" >Vote-Up</p>
				<p class="vote" url="/vdown" pid="'''+pid+'''" >Vote-Down</p>
		'''
	if lvl == 1 and userstat:
		html +=' <p class="ans" pid="'+pid+'" >Answer?</p> '
	html += '''
			</section>
			<form id="rf'''+pid+'''" class="psreplyform" method="post" action="/replypost">
				<input type="hidden" value="'''+pid+'''" name="r2pid">
				<input type="hidden" name="poster" value="'''+uname+'''">
				<textarea name="bd" rows="5" cols="50"></textarea>
				<input type="submit" value="Reply">
			</form>
		</section>
		'''
	
	return posts+html

def make_article(posts,cls,p):
	pid = str(p.key().id())
	posts += '<section class="'+cls+'" pid="'+pid+'" id="pstsec'+pid+'">'
	return posts 

def close_article(posts):
	posts += '</section>'	
	return posts

def make_section(pid,posts):
	posts +='<section class="posts" id="replies'+pid+'" >'	
	return posts

def close_section(posts) :
	posts += '</section>'
	return posts

#make show all the deatils here)
def make_post(p,posts) :
	html = '''
		<section class="userDetails">
		<img src="/getImage" class="pstimg" >
		<p class="username">'''+p.poster.key().name()+'''</p>
		<p class="degree">'''+p.poster.course+'''</p>
		<p class="karma">Karma : '''+str(p.poster.karma)+'''</p>
		<p class="replydate">'''+str(p.timestamp.date())+'''</p>
		</section>
	''' #the count fo posts is a performance drawback I think
	pst_bd = '<section class="pstbd">'
	pst_bd += '<article poster="'+ p.poster.key().name()+'" pid="'+str(p.key().id())+'" id="pst'+str(p.key().id())+'">'+parse_quotes(nl2br(p.body))+'</article>'
	pst_bd +='</section>'
	pst_bd +='''
		<section class="signature">
			<article class="signature">
				'''+p.poster.signature+'''
			</article>
		</section>
	'''

	posts += html+pst_bd
	return posts
	
#this is buggy as hell !
def parse_quotes(p):
	bd = p 
	exp = re.compile(r'''
			\[quote=([a-z0-9]{6,8})
			\]
			(.+)
			\[\/quote\]
			''',re.VERBOSE)
	res = exp.search(bd)
	while res :
		grps = res.groups()
		det = '<blockquote>'
		det += '<p class="details">'+grps[0]+' wrote : </p>'
		det += '<hr/>'
		det+= '<p class="quotext">'+grps[1]+'</p>'
		det += '</blockquote>'
		bd = re.sub(r'\[quote=([a-z0-9]{6,8})\](.+)\[\/quote\]',det, bd)
		res = exp.search(bd)
		
	return bd 

#look into implementing this with proper data serialization
def serialize_ajax_info(u , p,r2pid ):
	resp = 'poster='+str(u.key().name())
	resp += '&'
	resp += 'r2pid='+r2pid
	resp += '&'
	resp += 'usrkarma='+str(u.karma)
	resp += '&'
	resp += 'usrdegree='+u.course
	resp += '&'
	resp += 'usrrdate='+str(p.timestamp.date())
	resp += '&'
	resp += 'usrsig='+'signature'#u.signature
	resp += '&'
	resp += 'usrimg=/profileimage'
	resp += '&'
	resp += 'bd='+p.body
	resp += '&'
	resp += 'newID='+str(p.key().id())

	return resp

