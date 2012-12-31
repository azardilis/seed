from functions.RetrieveFunctions import *
import os
import cgi
from populate import *
from google.appengine.api import mail
from functions.ForumFunctions import * # functions to handle posts and shit # "posts and shit" lol!
from model.base.Module import Module
from model.base.User import User
from model.base.Post import Post
from model.base.Thread import Thread
from model.base.Vote import Vote
from model.base.YearCourseSemester import YearCourseSemester
from model.base.Lecturer import Lecturer
from model.base.Rating import Rating
from model.base.Assessment import Assessment
from model.base.Grade import Grade
from model.base.Category import Category
from model.base.Subscription import Subscription
from google.appengine.ext.db import Key
from google.appengine.ext import db
from itertools import izip
from datetime import datetime
import PyRSS2Gen

def subscribe(user, module):
	Subscription(show_in_homepage=True, receive_notifications=True, subscribed_user=user, module=module).put()
	module.student_count+=1
	module.put()

def put_mark(user, assessment, mark):
 	assessment.sum_marks += mark
	assessment.count_marks += 1
	assessment.put()
	assessment.module.sum_marks += mark
	assessment.module.count_marks += 1
	assessment.module.put()

def put_difficulty(user, assessment, difficulty_outof5):
 	assessment.sum_difficulty += difficulty_outof5
	assessment.count_difficulty += 1
	assessment.put()
	assessment.module.sum_difficulty += difficulty_outof5
	assessment.module.count_difficulty += 1
	assessment.module.put()

def rate_lecturer(rating, teaching, overall, lecturerRating):
        if teaching and teaching in range(1,6) : 
		rating.teach_sum += teaching
		rating.teach_count += 1
		rating.put()
	if overall and teaching in range(1,6) :
		rating.overall_sum += overall
		rating.overall_count += 1
		rating.put()
	lecturerRating.voted = True #even if voted empty (maybe not applicable to them)
	lecturerRating.put()

def rate_assessment(assessment, interest, difficulty, grade):
        if interest and interest in range(1,6) : 
	 	assessment.sum_interest += interest
		assessment.count_interest += 1
		assessment.put()
		assessment.module.sum_interest += interest
		assessment.module.count_interest += 1
		assessment.module.put()	
	if difficulty and difficulty in range(1,6) :
	 	assessment.sum_difficulty += difficulty
		assessment.count_difficulty += 1
		assessment.put()
		assessment.module.sum_difficulty += difficulty
		assessment.module.count_difficulty += 1
		assessment.module.put()	
	grade.voted = True #even if voted empty (maybe not applicable to them)
	grade.put()

def mark_assessment(assessment, mark, grade):
	if mark and mark in range(0,101):
		assessment.sum_marks += mark
		assessment.count_marks += 1
		assessment.put()
		assessment.module.sum_marks += mark
		assessment.module.count_marks += 1
		assessment.module.put()	

	grade.marked = True
	grade.put()

