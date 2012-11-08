import webapp2
import jinja2
import os
import cgi

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class User:
    def __init__(self, username, moduleList):
        self.username = username
        self.moduleList = moduleList

    def get_username(self):
        return self.username

    def get_modules(self):
        return self.moduleList

class Module:
    def __init__(self, name, rating, url):
        self.name = name
        self.rating = rating
        self.url = url

    def get_name(self):
        return self.name

    def get_rating(self):
        return self.rating

def create_mockup_user(username):
    m1 = Module("comp3001", 4.0, "https://secure.ecs.soton.ac.uk/module/1213/COMP3001/")
    m2 = Module("comp3033", 5.0, "https://secure.ecs.soton.ac.uk/module/1213/COMP3033/")
    m3 = Module("comp3032", 4.5, "https://secure.ecs.soton.ac.uk/module/1213/COMP3032/")
    user = User(username, [m1,m2,m3])
    return user

class SignInPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())

class MainPage(webapp2.RequestHandler):
    def get(self):
        module_list = user.get_modules()
        template_values = {
            'user':user,
            'module_list':module_list,
        }
        template = jinja_environment.get_template('templates/signin.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        username = cgi.escape(self.request.get('user'))
        module_list = user.get_modules()
        template_values = {
            'user':user,
            'module_list':module_list,
        }
        template = jinja_environment.get_template('templates/signin.html')
        self.response.out.write(template.render(template_values))

class ForumPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/forum.html')
        self.response.out.write(template.render({}))

class AboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/about.html')
        self.response.out.write(template.render({}))
        
class NotesPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/notes.html')
        self.response.out.write(template.render({}))

user = create_mockup_user("az2g10")
app = webapp2.WSGIApplication([('/'     , SignInPage),
                               ('/main' , MainPage),
                               ('/forum', ForumPage),
                               ('/about', AboutPage),
                               ('/notes', NotesPage)],
                              debug=True)
                               


    
