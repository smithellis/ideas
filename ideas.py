import os
from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask_user import roles_required

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


""" Define the app and the db """

app=Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')

try: app.config.from_object('local_settings')
except: pass

mail=Mail(app)
db=SQLAlchemy(app)

""" Define the models """
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

# Define the UserRoles data model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Idea(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	description=db.Column(db.Text)
	fullname=db.Column(db.String(80))
	email=db.Column(db.String(80))
	department=db.Column(db.String(80))
	total_votes=db.Column(db.Integer)
	votes=db.relationship('Vote',backref='idea',lazy=True)

	def __repr__(self):
		return '<Idea %r>' % self.descritption

class Vote(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	ipaddress=db.Column(db.String(80),nullable=False)
	vote_state=db.Column(db.Integer,nullable=False)
	idea_id=db.Column(db.Integer,db.ForeignKey('idea.id'),nullable=False)

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User


    # Create 'user007' user with 'secret' and 'agent' roles
if not User.query.filter(User.username=='user007').first():
	user1 = User(username='user007', email='user007@example.com', active=True,password=user_manager.hash_password('Password1'))
	user1.roles.append(Role(name='secret'))
	user1.roles.append(Role(name='agent'))
	db.session.add(user1)
	db.session.commit()

""" Define the routes and mechanics """

@app.route('/', methods=['GET','POST'])
def home():
	if request.method=='POST':
		idea = request.form['idea']
		fullname = request.form['fullname']
		email = request.form['email']
		department = request.form['department']
		newidea = Idea(description=idea,fullname=fullname,email=email,department=department)
		db.session.add(newidea)
		db.session.commit()
		flash('Idea added!  Thanks!')
	return render_template('index.html')

@app.route('/active-ideas')
@login_required
def activeIdeas():
	return render_template('active-ideas.html')

@app.route('/faq')
def faq():
	return render_template('faq.html')

@app.route('/feedback')
def feedback():
	return render_template('feedback.html')

@app.route('/vote.html')
def vote():
	all_ideas = Idea.query.all()
	return render_template('vote.html', all_ideas = all_ideas)
