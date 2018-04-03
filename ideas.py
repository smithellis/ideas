from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

""" Define the app and the db """

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////tmp/test.db'
# SQLAlchemy is killing me with warnings, turning track mods off
SQLALCHEMY_TRACK_MODIFICATIONS=False
db=SQLAlchemy(app)

""" Define the models """

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



""" Define the routes and mechanics """

@app.route('/')
def home():
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

@app.route('/vote.html')
def vote():
	return render_template('vote.html')
