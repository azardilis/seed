#!/usr/bin/python

import webapp2
from model.base.Module import Module
from model.base.YearCourseSemester import YearCourseSemester
from model.base.Lecturer import Lecturer
from model.base.Rating import Rating
from google.appengine.ext import db
from google.appengine.ext.db import Key

class MainHandler(webapp2.RequestHandler) :
	def get(self) :
		self.response.write('''
			<h1>Add Lecturer</h1>
			<form method="POST" action="/addlecturer">
				<input type="text" placeholder="Full Name" name="full_name">
				<br/>
				<input type="text" placeholder="Lecturer code" name="code" id="code">
				<br/>
				<input type="url" placeholder="Lecturer homepage" name="lurl" id="code">
				<br/>
				<input type="submit" value="Add Lecturer">
			</form>
			<br />
			<h1>Add Module</h1>
			<form method="GET" action="/addmodule">
				<input type="text" name="code" placeholder="Module code">
				<br/>
				<input type="text" name="title" placeholder="Module title">
				
				<br/>

				<input type="url" name="murl" placeholder="Module homepage">
				<br/>
				<input type="number" name="my" placeholder="Module year">
				<br/>
				<input type="number" name="ms" placeholder="Module semester">
				<br/>
				<input type="text" name="mc" placeholder="Module course">
				<br/>
				<input type="submit" value="Add Module">
			</form>
			<br />
			<h1>Add Rating</h1>
			<form method="GET" action="/addrating">
				<input type="text" name="lcode" placeholder="Lecturer code">
				<br/>
				<input type="text" name="mcode" placeholder="Module code">
				<br/>
				<input type="submit" value="Add Module">
			</form>
			
			<br />
			<h1>Add YearCourseSemester</h1>
			<form method="POST" action="/addycs">
			<input placeholder="Year" type="number" name="year"><br/>
			<input type="number" placeholder="Semester" name="semester"><br/>
			<input type="text" placeholder="course" name="course"><br/>
			<input type="submit" value="Add YCS"><br/>
			</form>
			
			<br />
			<h1>Explore Semesters</h1>
			<form method="GET" action="/semexplorer">
			<input placeholder="Year" type="number" name="year"><br/>
			<input type="number" placeholder="Semester" name="semester"><br/>
			<input type="text" placeholder="course" name="course"><br/>
			<input type="submit" value="Explore YCS"><br/>
			</form>
			
			<br />
			<h1>Lecturer explorer</h1>
			<form method="GET" action="/lecexplorer">
			<input type="text" name="lcode">
			<input type="submit" value="Explore lecturer">
			</form>
			
			<br />
			<h1>Module Explorer</h1>
			<form method="GET" action="/modexplorer">
			<input type="text" name="mcode" placeholder="Module code">
			<input type="submit" value="Explore module">
			</form>

		''')

class AddYCS(webapp2.RequestHandler) :
	def post(self):
		yr = self.request.get('year')
		smstr = self.request.get('semester')
		crs = self.request.get('course')
		YearCourseSemester(year=int(yr), semester=int(smstr), course=crs).put()
		self.response.write('Put YCS successfully')


class AddLecturer(webapp2.RequestHandler) :
	def post(self) : #to allo post, just change this get to post 
		fullname = self.request.get('full_name')
		cd = self.request.get('code')
		lurl = self.request.get('lurl')
		self.response.write('Lecturer details :  '+fullname+'('+cd+')')
		Lecturer(key_name=cd, full_name=fullname, code = cd,home_page=lurl ).put()
		self.response.write('Put finished')

class AddModule(webapp2.RequestHandler):
	def get(self):
		mcode = self.request.get('code')
		mtitle = self.request.get('title')
		mc = self.request.get('mc')
		my = self.request.get('my')
		ms = self.request.get('ms')
		murl = self.request.get('murl')

		q = YearCourseSemester.all()
		q.filter('course =',mc)
		q.filter('year =',int(my))
		q.filter('semester =',int(ms))
		ycsa = q.get()

		Module(key_name=mcode, code=mcode,title=mtitle,home_page=murl, semester=int(ms), ycs = ycsa).put()
		self.response.write('Put module probably successful')

class AddRating (webapp2.RequestHandler):
	def get(self):
		mcode = self.request.get('mcode')
		lcode = self.request.get('lcode')
		
		q=Lecturer.all()
		q.filter('__key__ =', Key.from_path('Lecturer', lcode))
		lecturers = q.get()
		self.response.write('Lecturer with code "'+lcode+'" is called "'+lecturers.full_name+'"')
		
		q = Module.all()
		q.filter('__key__ = ', Key.from_path('Module',mcode))
		modules = q.get()
		self.response.write('<br/>Module with code "'+modules.code+'" has title "'+modules.title+'"')
		
		Rating(module=modules, lecturer =lecturers).put()
		self.response.write('<br/> Rating probably put successfully')

class LecturerView(webapp2.RequestHandler):
	def get(self):
		lcode = self.request.get('lcode')
		q=Lecturer.all()
		q.filter('__key__ =',Key.from_path('Lecturer',lcode))
		lec = q.get()
		if lec:
			self.response.write(lec.code+' teaches:<br/>')
			for i in lec.modules :
				self.response.write('<br/>--->')
				self.response.write(i.module.code+':'+i.module.title)

		else: self.response.write('Lecturer not found')

class SemesterExplorer(webapp2.RequestHandler):
	def get(self) :
		y = self.request.get('year')
		s = self.request.get('semester')
		crs = self.request.get('course')
		yr = int(y)
		sm = int(s)

		q = YearCourseSemester.all()
		q.filter('course =',crs)
		q.filter('year =',yr)
		q.filter('semester =',sm)

		ycs = q.get()
		if ycs :
			self.response.write('Found YCS object, printing  modules.<br/>')

			for i in ycs.modules :
				self.response.write(i.code+':'+i.title+'<br/>')
		else : self.response.write('Unable to find YCS entity')
		
class ModuleExplorer(webapp2.RequestHandler):
	def get(self):
		mcode = self.request.get('mcode')
		q = Module.all()
		q.filter('__key__ =',Key.from_path('Module',mcode))
		module = q.get()
		if module :
			self.response.write('Lecturers for module :<br/>')
			for i in module.lecturers :
				self.response.write('-->'+i.lecturer.full_name+'('+i.lecturer.code+')<br/>')
		else : self.response.write('Unable to find module '+mcode)

app= webapp2.WSGIApplication([
	('/', MainHandler),
	('/addmodule', AddModule),
	('/addlecturer',AddLecturer),
	('/addrating',AddRating),
	('/addycs',AddYCS),
	('/semexplorer',SemesterExplorer),
	('/modexplorer',ModuleExplorer),
	('/lecexplorer',LecturerView)
],debug=True)
