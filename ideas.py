import os
import datetime
from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask_user import roles_required
from flask_login import current_user
from flask_admin import Admin
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView

# Use a Class-based config to avoid needing a 2nd file - terrible idea to fix later
# os.getenv() enables configuration through OS environment variables

class ConfigClass(object):
    # Flask settings
    SECRET_KEY =              os.getenv('SECRET_KEY',       'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',     'sqlite:///single_file_app.sqlite')
    CSRF_ENABLED = True
    # Flask-Mail settings
    MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        '364142f32f4e55')
    MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        '3bce037966e65a')
    MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  '"Ideas" <noreply@example.com>')
    MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.mailtrap.io')
    MAIL_PORT =           int(os.getenv('MAIL_PORT',            '2525'))

    # Flask-User settings
    USER_APP_NAME        = "Ideas"                # Used by email templates
    # SQLAlchemy Defaults to garbage and complaining, let's stop it
    SQLALCHEMY_TRACK_MODIFICATIONS = False


#Define the app and the db

app=Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')

try: app.config.from_object('local_settings')
except: pass


mail=Mail(app)
db=SQLAlchemy(app)


# Define the User data model. Make sure to add flask_user UserMixin!!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')
    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '%s' % (self.name)

# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Idea(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(80))
    description=db.Column(db.Text)
    fullname=db.Column(db.String(80))
    email=db.Column(db.String(80))
    department=db.Column(db.String(80))
    total_votes=db.Column(db.Integer)
    canbevoted=db.Column(db.Boolean, default=False, nullable=False)
    ideaaccepted=db.Column(db.Boolean, default=False, nullable=False)
    votes=db.relationship('Vote',backref='idea',lazy=True)

    def __repr__(self):
        return '<Idea %r>' % self.title

class Vote(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    ipaddress=db.Column(db.String(80),nullable=False)
    userid=db.Column(db.Integer)
    vote_state=db.Column(db.Integer,nullable=False)
    idea_id=db.Column(db.Integer,db.ForeignKey('idea.id'),nullable=False)

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

# Hanky panky to protect the admin area
class MyView(ModelView):
    @expose('/')
    @login_required
    def index(self):
        return self.render('/admin')

# Reset the whole DATABASE
db.drop_all()
db.create_all()

# Create 'user007' user with 'secret' and 'agent' roles
if not User.query.filter(User.username=='demo').first():
    user1 = User(username='demo', email='smithe@gmail.com', active=True, confirmed_at=datetime.datetime.now(), password=user_manager.hash_password('Password1'))
    user1.roles.append(Role(name='secret'))
    user1.roles.append(Role(name='agent'))
    db.session.add(user1)
    db.session.commit()

# Flask Admin Setup
admin=Admin(app, name="Ideas", template_mode="bootstrap3")
admin.add_view(MyView(User, db.session))
admin.add_view(MyView(Idea, db.session))

""" Define the routes and mechanics """

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        title = request.form['title']
        idea = request.form['idea']
        fullname = request.form['fullname']
        email = request.form['email']
        department = request.form['department']
        total_votes = 0
        newidea = Idea(title=title,description=idea,fullname=fullname,email=email,department=department,canbevoted=False,total_votes=0,ideaaccepted=False)
        db.session.add(newidea)
        db.session.commit()
        flash('Got it!  We have added your idea.  An administrator will take a look, and if it appears authentic, it will get approved and become available for the voting process.  This step happens so we can avoid spam - it is difficult to allow anonymous submissions without getting a bit of spam.')
    return render_template('index.html')

@app.route('/active-ideas')
def activeIdeas():
    return render_template('active-ideas.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/vote', methods=['GET','POST'])
@login_required
def vote():
    ipaddr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    userid = int(current_user.get_id())
    all_ideas = Idea.query.all()
    for idea in all_ideas:
        for vote in idea.votes:
            if vote.userid == userid:
                idea.voted="yes"
    return render_template('vote.html', all_ideas = all_ideas, userid=userid, ipaddress=ipaddr)

@app.route('/makevote',)
@login_required
def makevote():
    ipaddr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    userid = int(current_user.get_id())
    idea_id = request.args.get('idea_id',0,type=int)
    vote_state = 1
    vote = Vote(ipaddress=ipaddr, userid=userid, idea_id=idea_id, vote_state=vote_state)
    thisidea = Idea.query.filter_by(id=idea_id).first()
    if thisidea.total_votes == None:
        thisidea.total_votes = 0
    thisidea.total_votes = thisidea.total_votes+1
    totalvotes = thisidea.total_votes
    db.session.add(vote)
    db.session.commit()
    return jsonify(result=idea_id, totalvotes=totalvotes)
