from model.base.Thread import Thread
from model.base.User import User 
from model.base.Post import Post
from google.appengine.ext.db import Key
from google.appengine.ext import db
import cgi

def retrieve_post(pid):
	pid = int(cgi.escape(pid))
	p_k = Key.from_path('Post',pid)
	pst = db.get(p_k)
	return pst

def retrieve_thread(tid):
	tid = int(cgi.escape(tid))
	t_k  = Key.from_path('Thread',tid)
	t = db.get(t_k)
	return t

def retrieve_category(cid):
	cid = int(cgi.escape(cid))
	c_k = Key.from_path('Category', cid)
	cat = db.get(c_k)
	return cat 
	
