import sys
import re
import urllib
import urllib2
import cookielib
import urlparse
#need import things
tocrawl = set([sys.argv[1]])
crawled = set([])
#regular expressions for you to endulge
keywordregex = re.compile('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>')
linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
lecturer_regex = re.compile('<a href=\'(https://secure\.ecs\.soton\.ac\.uk/people/[a-zA-Z0-9]{0,5})\'>([a-zA-Z. ]*)</a></div><div>(Moderator|Module Leader|Lecturer)')
cw_regex = re.compile('(Mon|Tue|Wed|Thu|Fri)&nbsp;([0-9]{1,2})&nbsp;(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec),&nbsp;[0-9]{1,2}:[0-9]{2}(?:,&nbsp;(20[1-2][0-9]))?</td><td><a href=\'([A-Za-z:/\. \w#_-]*)\'>([a-zA-Z\ 0-9:_\w]*)</a></td><td>:&nbsp;<a href=\'(https://handin.ecs.soton.ac.uk/handin/1213/[\w/]*)\'')
title_regex = re.compile('(?:<title>ECS - ([\w: \-&,\._/\\!@#$^+=]*)[\w ()-]*</title>)')
semester_regex = re.compile('(?:Semester:(?:</strong> )?([1-3]))')
count = 0 #useless

#
#
#search for password and username fill in yours
#
#

#we like it global
alllecturers = {}
allmodules = {}
modulename = ""
#do not need to document these functions
def parse_modulepage(page,url):
    global modulename
    global allmodules

    msg = page.read()
    result = re.search(title_regex,msg)

    if not result:
        sys.stdout.write(url+" - no title in page\n")
        return
    
    modulename = result.group(1)
    sys.stdout.write(modulename+"\n")

    _module = TModule(modulename,url)
    allmodules[modulename] = _module

    semester = get_module_semester(_module.code)
    _module.add_semester(semester)

#    msg = page
    startPos = msg.find('<!-- Main Page Begins -->')
    if startPos != -1:
        endPos = msg.find('<!-- Main Page Ends -->', startPos+25)
        if endPos != -1:
            title = msg[startPos+25:endPos]
            
    find_lecturers(title)
    find_cw(title)

def get_module_semester(modulecode):
    semesterurl = "http://www.ecs.soton.ac.uk/module/" + modulecode
    resp = opener.open(semesterurl).read()
    result = re.search(semester_regex,resp)
    if result:
        return result.group(1)
    return 0 #if here, something is wrong with the thing, or old module

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
        lecturer = Lecturer(name,url)
        lecturer.append_class(modulename,role)
        alllecturers[name] =lecturer 

    _module = allmodules[modulename]
    _module.append_lecturer(name,role)

def parse_cw(cw):
    global modulename
    global allmodules
    handin = cw.group(7)
    spec = cw.group(5)
    title = cw.group(6)
    date = cw.group(2)+"/"+cw.group(3)
    if(cw.group(4)):
        date = date+"/"+cw.group(4)
    module = allmodules[modulename]
    module.append_cw(title,date,handin,spec)

class TModule:
    title = ""
    code = ""
    semester = ""
    page = ""
    cw = []
    lecturers = []

    def __init__(self,title,page):
        self.page = page
        self.code = title[0:8]
        tmp = title[8:]
        if (tmp[0]== ':'):
            tmp = tmp[1:]
        if (tmp[0]== ' '):
            tmp = tmp[1:]
        self.title = tmp
        
        self.cw = []
        self.lecturers = []

    def add_code(self,argcode):
        self.code = argcode

    def add_semester(self,argsem):
        self.semester = argsem

    def append_lecturer(self,lecturer,role):
        self.lecturers.append((lecturer,role))
    
    def append_cw(self,cw,deadline,handin,desc):
        self.cw.append((cw,deadline,handin,desc))



class Lecturer:
    name = ""
    page = ""
    modules = []
    def __init__(self,name,page):
        self.name = name
        self.page = page
        self.modules = []
        
    def append_class(self,module,role):
        self.modules.append((module,role))



for i in range(1):
    try:
        crawling = tocrawl.pop()
#		print "try"+crawling
    except KeyError:
            raise StopIteration
        break
    username = 'ks6g10'
    password = 'your mother is so fat she causes stack overflow'
    cj = cookielib.CookieJar() #we love cookies
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode({'ecslogin_username' : username, 'ecslogin_password' : password})
    resp = opener.open('https://secure.ecs.soton.ac.uk/login/now/index.php', login_data)
    print 'hello'
    resp = resp.read()
    resp = opener.open('https://secure.ecs.soton.ac.uk/login/now/index.php', login_data) #do it twice, why not, it is needed to set cookies
    resp = resp.read()

    if re.search('LOGIN FAILED!',resp):
        sys.stdout.write("Login failed\n")
        break
    else:
        sys.stdout.write("Login successfull\n")
        
    purl = urlparse.urlparse(crawling)
    try:
        response = opener.open(crawling)
    except:
        continue
    msg = response.read()
    startPos = msg.find('<title>')#find relevant
    if startPos != -1:
        endPos = msg.find('</title>', startPos+7)
        if endPos != -1:
            title = msg[startPos+7:endPos]
            

    links = linkregex.findall(msg)
    crawled.add(crawling)
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
            parse_modulepage(opener.open(link),link)
            crawled.add(link)
            break
                
            #finished
    sys.stdout.write("\n")
    while len(alllecturers):
        (key, val) = alllecturers.popitem()
        if len(val.modules) > 1:
            sys.stdout.write(" "+str(len(val.modules))) #some output of module
            sys.stdout.write(val.name)
            sys.stdout.write(val.modules[0][0])
            sys.stdout.write("\n")

    while len(allmodules):
        (key, val) = allmodules.popitem()
        print val.name +" " + val.code + " " + str(val.semester) + "\n"
#need finish these
#def Populate_lecturers():
#    global alllecturers
#    while len(alllecturers):
#        (key, val) = alllecturers.popitem()
#        temp = Lecturer(key_name=val.name, full_name=val.name,home_page=va#l.page)
#        temp.put()
#def Populate_modules():
#    global allmodules
#    while len(allmodules):
#        (key, val) = allmodules.popitem()
#        temp = Module(key_name=val.code, title=val.title,ecs_page=val.page#,yearCourseSemester=compsci31)
#        temp.put()
#        cw = val.cw
#        while len(cw):
#            #title date handin spec
#            (ttitle, tdate,thandin,tspec) = cw.popitem()
#            tempcw = Assessment(title=ttitle,dueDate=datetime.strptime('No#v 1 2005  1:33PM', '%b %d %Y %I:%M%p'), specLink=db.link(tspec),handin=db.#link(thandin),module=temp)
#            tempcw.put()
#            
#                tocrawl.add(link)
