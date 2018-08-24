import os
from subprocess import call
from ideas import db

os.environ['FLASK_APP']='ideas.py'
os.environ['FLASK_DEBUG']='1'

db.drop_all()
db.create_all()

call(['flask','run'])
