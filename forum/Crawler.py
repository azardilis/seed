import sys
import re
import urllib
import urllib2
import cookielib
import urlparse
#need import things
tocrawl = set([])
crawled = set([])
#regular expressions for you to endulge
keywordregex = re.compile('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>')
linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
lecturer_regex = re.compile('<a href=\'(https://secure\.ecs\.soton\.ac\.uk/people/[a-zA-Z0-9]{0,5})\'>([a-zA-Z. ]*)</a></div><div>(Module Leader|Lecturer)')
cw_regex = re.compile('(Mon|Tue|Wed|Thu|Fri)&nbsp;([0-9]{1,2})&nbsp;(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep)|(Oct|Nov|Dec)),&nbsp;([0-9]{1,2}:[0-9]{2})(?:,&nbsp;(20[1-2][0-9]))?</td><td><a href=\'([A-Za-z:/\. \w#_-]*)\'>([a-zA-Z\ 0-9:_\w\-]*)</a></td><td>:&nbsp;<a href=\'(https://handin.ecs.soton.ac.uk/handin/1213/[\w/]*)\'')
title_regex = re.compile('(?:<title>ECS - ([\w: \-&,\._/\\!@#$^+=]*)[\w ()-]*</title>)')
semester_regex = re.compile('(?:Semester:(?:</strong> )?([1-3]))')
programme_regex = re.compile('([GHE][0-9GHR]{3})')
keyname_regex = re.compile('.*/(.*)$')
year_regex = re.compile('List of all modules in the ([0-9]{4}) session')
count = 0 #useless

#
#
#search for password and username fill in yours
#
#

#we like it global
global alllecturers
global allmodules
global modulename
global yearstart 
global yearend


def ret_allmodule():
    return allmodules

def ret_alllecurers():
    return alllecturers

def ret_yearstart():
    return yearstart

def ret_yearend():
    return yearend

#do not need to document these functions
def parse_modulepage(page,url,opener):
    global modulename
    global allmodules

    msg = page.read()
    result = re.search(title_regex,msg)

    if not result:
        return
    
    modulename = result.group(1)
    

    _module = TModule(modulename,url)
    allmodules[_module.code] = _module
    modulename = _module.code
    
    semesterurl = "http://www.ecs.soton.ac.uk/module/" + _module.code
    resp = opener.open(semesterurl).read()
    
    semester = get_module_semester(resp)
    year = get_module_year(_module.code)
    _module.add_semester(semester)
    _module.add_year(year)

#    msg = page
    startPos = msg.find('<!-- Main Page Begins -->')
    if startPos != -1:
        endPos = msg.find('<!-- Main Page Ends -->', startPos+25)
        if endPos != -1:
            title = msg[startPos+25:endPos]
            
    find_lecturers(title)
    find_cw(title)

def get_module_year(module_code):
    year = int(module_code[4])
    if year > 3:
        year = 4
    return year

def set_module_preogrammes(_module,resp):
    msg = resp
    result = re.search(programme_regex,msg)
    while result:
        _module.append_programme(result.group(1))
        msg = msg[result.end():]
        result = re.search(programme_regex,msg)

def get_module_semester(resp):
    result = re.search(semester_regex,resp)
    if result:
        return int(result.group(1))
    return 3 #if here, something is wrong with the thing, or old module or msc project

def find_lecturers(text):
    #    regexp = 
    result =  re.search(lecturer_regex,text)
    while result:
        parse_lecturer(result)
        text = text[result.end():]
        result =  re.search(lecturer_regex,text)

def find_cw(text):
    result =  re.search(cw_regex,text)
    while result:
        parse_cw(result)
        text = text[result.end():]
        result =  re.search(cw_regex,text)

def parse_lecturer(lect):
    global modulename
    global alllecturers
    global allmodules
    name = lect.group(2)
    role = lect.group(3)
    url = lect.group(1)
    if alllecturers.has_key(name):
        lecturer = alllecturers[name]
        lecturer.append_class(modulename,role)
    else:
        lecturer = TLecturer(name,url)
        lecturer.append_class(modulename,role)
        alllecturers[name] =lecturer 

    _module = allmodules[modulename]
    _module.append_lecturer(name)

def parse_cw(cw):
    global modulename
    global allmodules
    global yearend
    global yearstart
    handin = cw.group(9)
    spec = cw.group(7)
    title = cw.group(8)
    year = yearstart 
    ttime = cw.group(5)
    # 2 = date 3 = month 4 = time
    date = cw.group(2)
    if cw.group(3):
        month = cw.group(3)
        year = yearend
    else:
        month = cw.group(4)
        year = yearstart
    formated_date = str(month) + " " + str(date) + " " + str(year) + " " + str(ttime)
#    if(cw.group(5)):
#        date = date+"/"+cw.group(4)
    module = allmodules[modulename]
    module.append_cw(title,formated_date,handin,spec)

class TModule:
    title = ""
    code = ""
    semester = 0
    page = ""
    year = 0
    programmes = []
    cw = []
    lecturers = []

    def __init__(self,title,page):
        self.page = page
        self.code = title[0:8]
        tmp = title[8:]
        if (tmp[0]== ':'): tmp = tmp[1:]
        if (tmp[0]== ' '): tmp = tmp[1:]
        self.title = tmp
        self.semester = 0
        self.programmes = []
        self.cw = []
        self.lecturers = []
        self.year = 0;
        
    def add_year(self,year):
        self.year = year

    def add_code(self,argcode):
        self.code = argcode

    def add_semester(self,argsem):
        self.semester = argsem

    def append_lecturer(self,lecturer):
        self.lecturers.append(lecturer)

    def append_programme(self,programme):
        #look at http://www.ecs.soton.ac.uk/undergraduate/find_a_programme
        compsci = re.compile('(?:G4G6|G400|G401|G421|G450|G4GR|G600|G4G5)')#Computer Science and Software Engineering
        ito = re.compile('(?:G560|G500)')#Information Technology in Organisations LOL
        ee = re.compile('(?:H610|H611|H641|H603|H6G7|H6G4|H691)') #Electronic Engineering
        eme = re.compile('(?:H620|HH36|HHH6|H601)') #Electrical and Electromechanical Engineering
        eee = re.compile('(?:H600|H602)') #Electrical and Electronic Engineering
        course = ""
        if programme[0] is 'G':
            if re.search(compsci,programme): course = "compsci"
            elif re.search(ito,programme): course = "ito"
        else:
            if re.search(ee,programme): course = "ee"
            elif re.search(eme,programme):course = "eme"
        if course not in self.programmes:
            self.programmes.append(course)
        
    def append_cw(self,cw,deadline,handin,desc):        
        self.cw.append((cw,deadline,handin,desc))

class TLecturer:
    name = ""
    page = ""
    keyname = ""
    modules = []
    def __init__(self,name,page):
        self.name = name
        self.page = page
        result = re.search(keyname_regex,page).group(1)
        if result: self.keyname = result
        else: self.keyname = self.name
        self.modules = []
        
    def append_class(self,module,role):
        self.modules.append((module,role))



def open_link(link):
    global alllecturers
    global allmodules
    global modulename
    global yearstart 
    global yearend


    alllecturers = {}
    allmodules = {}
    modulename = ""
    yearstart = 0
    yearend = 0

    tocrawl.add(link)
    try:
        crawling = tocrawl.pop()
#		print "try"+crawling
    except KeyError:
            raise StopIteration
    
    username = 'ks6g10'
    password = 'Dr4g0nfly'
    cj = cookielib.CookieJar() #we love cookies
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode({'ecslogin_username' : username, 'ecslogin_password' : password})
    resp = opener.open('https://secure.ecs.soton.ac.uk/login/now/index.php', login_data)
    resp = resp.read()
    resp = opener.open('https://secure.ecs.soton.ac.uk/login/now/index.php', login_data) #do it twice, why not, it is needed to set cookies
    resp = resp.read()

    if re.search('LOGIN FAILED!',resp):
        sys.stdout.write("Login failed\n")
        return
            
    purl = urlparse.urlparse(crawling)
    try:
        response = opener.open(crawling)
    except:
        return
    msg = response.read()
    startPos = msg.find('<title>')#find relevant
    if startPos != -1:
        endPos = msg.find('</title>', startPos+7)
        if endPos != -1:
            title = msg[startPos+7:endPos]
            
    result = re.search(year_regex,msg)
    if result:
        yearstart = 2000+int(result.group(1)[0:2])
        yearend = 2000+int(result.group(1)[2:])

    links = linkregex.findall(msg)
    crawled.add(crawling)
    i = 0
    for link in (links.pop(0) for _ in xrange(len(links))):
            #        for link in (links.pop(0) for _ in range(100)): #only parse 100
        if not "https://secure.ecs.soton.ac.uk/module/" in link:
            continue
        if link.startswith('/'):
            link = 'http://' + purl[1] + link
        elif link.startswith('#'):
            link = 'http://' + purl[1] + purl[2] + link
        elif not link.startswith('http'):
            link = 'http://' + purl[1] + '/' + link
        if link not in crawled:
            parse_modulepage(opener.open(link),link,opener)
            crawled.add(link)       
            if i > 5:
               return
            i += 1
