from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from projectmanagement.models import User, Project, Task
from datetime import datetime, date
from flask_login import current_user



class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('admin','Admin'),('operations','Operations'),('team_lead','Team Lead'),('developer','Developer')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    designation = StringField('Designation')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')



class ProjectForm(FlaskForm):
    users = User.query.all()
    username = []
    for user in users:
        username.append(user.username)
    username.insert(0,'None')

    title = StringField('Project Title', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Project Description')
    team_lead = SelectField('Team Lead', choices=username)
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Expected End Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Not Started','Not started'),('Ongoing','Ongoing'),
                                    ('Completed','Completed')])
    submit = SubmitField('Submit')
    
    
    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data :
            raise ValidationError('You have to choose an end date which is after the start date!')



class TaskForm(FlaskForm):
    users = User.query.all()
    username = []
    for user in users:
        username.append(user.username)
    username.insert(0,'None')

    projecthandle = Project.query.all()
    projects = []
    for project in projecthandle:
        projects.append(project.title)
    projects.insert(0,'None')

    project = SelectField('Project', choices=projects)
    title = StringField('Task', validators=[DataRequired(), Length(min=2, max=50)])
    detail = TextAreaField('Task details')
    developer = SelectField('Developer', choices=username)
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Expected End Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Not Started','Not started'),('Ongoing','Ongoing'),
                                    ('Completed','Completed')])
    submit = SubmitField('Submit')

    def validate_start_date(self, start_date):
        project = Project.query.filter_by(title=self.project.data).first()
        start = project.start_date.date()
        end = project.end_date.date()
        if start_date.data < start or start_date.data > end :
            raise ValidationError('You must choose the date within project period time!')
        
    def validate_end_date(self, end_date):
        project = Project.query.filter_by(title=self.project.data).first()
        start = project.start_date.date()
        end = project.end_date.date()
        if end_date.data < self.start_date.data :
            raise ValidationError('You have to choose an end date which is after the start date!')
        elif end_date.data < start or end_date.data > end :
            raise ValidationError('You must choose the date within project period time!')
        


class UpdateStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('Not Started','Not started'),('Ongoing','Ongoing'),
                                    ('Completed','Completed')])
    submit = SubmitField('Save')



class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')