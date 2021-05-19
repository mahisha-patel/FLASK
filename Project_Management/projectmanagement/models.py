from projectmanagement import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	designation = db.Column(db.String(50), nullable=True)
	priority = db.Column(db.Integer, nullable=False)
	project = db.relationship('Project',backref='projects',lazy=True)
	user = db.relationship('Attendance',backref='users',lazy=True)

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	
	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.priority}')"


class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	title = db.Column(db.String(100), unique=True, nullable=False)
	description = db.Column(db.String(5000), unique=True, nullable=True)
	start_date = db.Column(db.DateTime)
	end_date = db.Column(db.DateTime)
	team_lead = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
	status = db.Column(db.String(40))
	date_added = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	task = db.relationship('Task',backref='tasks',lazy=True)

	def __repr__(self):
		return f"Project('{self.title}', '{self.date_added}')"



class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	title = db.Column(db.String(50), nullable=True)
	details = db.Column(db.String(5000), nullable=True)
	start_date = db.Column(db.DateTime)
	end_date = db.Column(db.DateTime)
	developer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	status = db.Column(db.String(40))
	date_added = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	
	def __repr__(self):
		return f"Task('{self.title}', '{self.date_added}')"



class Attendance(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date, nullable=False)
	start_time = db.Column(db.Time)
	end_time = db.Column(db.Time)
	break_time = db.Column(db.Time)
	total_time = db.Column(db.Time)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return f"Attendance('{self.user_id}', '{self.date}', '{self.total_time}')"