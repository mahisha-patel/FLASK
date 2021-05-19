from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from projectmanagement import app, db
from projectmanagement import bcrypt
from projectmanagement.forms import (LoginForm, RegistrationForm, ProjectForm, TaskForm,
                                    UpdateAccountForm, UpdateStatusForm, RequestResetForm, 
                                    ResetPasswordForm)
from projectmanagement.models import User, Project, Task, Attendance
from datetime import date, datetime, timedelta
from projectmanagement import mail
from flask_mail import Message



@app.route('/')
@app.route('/home', methods=['GET','POST'])
def home():
    projects = Project.query.all()
    users = User.query.all()
    tasks = Task.query.all()

    if request.method == 'POST':

        user = Attendance.query.filter_by(user_id=session['user_id'], date=date.today()).first()
        result = request.form.to_dict()

        if result.get('pause'):
            session['start'] = ''
            session['stop'] = ''
            session['pause'] = result.get('pause')
            session['break_start_time'] = datetime.now().time().isoformat()
            session['break_start_time'] = session['break_start_time'][:8]
            print(session['break_start_time'])

        if result.get('start'):    
            session['stop'] = ''
            session['pause'] = ''
            session['start'] = result.get('start') 
            if user:
                pass
            else:
                add_user = Attendance(user_id=session['user_id'],date=date.today(),
                    start_time=datetime.now().time())
                db.session.add(add_user)
                db.session.commit()

            if session.get('break_start_time'):

                if user.break_time:
                    bst = datetime.strptime(session['break_start_time'], '%H:%M:%S').time()
                    bet = datetime.now().time()
                    h1, m1, s1 = bet.hour, bet.minute, bet.second
                    h2, m2, s2 = bst.hour, bst.minute, bst.second
                    t1_secs = s1 + 60 * (m1 + 60*h1)
                    t2_secs = s2 + 60 * (m2 + 60*h2)
                    breaktime = t1_secs - t2_secs
                    bt = user.break_time
                    h, m, s = bt.hour, bt.minute, bt.second
                    add_time = s + 60 * (m + 60*h)
                    user.break_time = timedelta(seconds=add_time + breaktime)
                    db.session.commit()
                    session.pop('break_start_time')
                
                else:
                    bst = datetime.strptime(session['break_start_time'], '%H:%M:%S').time()
                    bet = datetime.now().time()
                    h1, m1, s1 = bet.hour, bet.minute, bet.second
                    h2, m2, s2 = bst.hour, bst.minute, bst.second
                    t1_secs = s1 + 60 * (m1 + 60*h1)
                    t2_secs = s2 + 60 * (m2 + 60*h2)
                    user.break_time = timedelta(seconds= t1_secs - t2_secs)
                    db.session.commit()
                    session.pop('break_start_time')
                

        if result.get('stop'):
            session['start'] = ''
            session['pause'] = ''
            session['stop'] = result.get('stop')
            if user.end_time:
                pass
            else:
                user.end_time = datetime.now().time()
                db.session.commit()
            if user.total_time:
                pass
            else:
                h1, m1, s1 = user.end_time.hour, user.end_time.minute, user.end_time.second
                h2, m2, s2 = user.start_time.hour, user.start_time.minute, user.start_time.second
                t1_secs = s1 + 60 * (m1 + 60*h1)
                t2_secs = s2 + 60 * (m2 + 60*h2)
                user.total_time = timedelta(seconds= t1_secs - t2_secs)
                db.session.commit()

        return render_template('home.html',title='Home', projects=projects, users=users, tasks=tasks)
    
    else:
        return render_template('home.html',title='Home', projects=projects, users=users, tasks=tasks)




@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.role.data == 'admin':
            role = 1
        elif form.role.data == 'operations':
            role = 2
        elif form.role.data == 'team_lead':
            role = 3
        elif form.role.data == 'developer':
            role = 4
        
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, priority=role)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            
            session['email'] = user.email
            session['user_id'] = user.id
            session['username'] = user.username            


            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.designation = form.designation.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if current_user.designation:
            form.designation.data = current_user.designation
    return render_template('account.html', title='Account', form=form)



@login_required
@app.route("/project", methods=['GET', 'POST'])
def project():
    form = ProjectForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.team_lead.data).first()
        user_id = user.id

        project = Project(title=form.title.data, description=form.description.data,
                team_lead=user_id, start_date=form.start_date.data,
                end_date=form.end_date.data, status=form.status.data)
        db.session.add(project)
        db.session.commit()
        flash('Congratulations, Your project has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('project.html', title='Project', form=form)


@login_required
@app.route("/project/<int:project_id>", methods=['GET', 'POST'])
def project_task(project_id):
    project = Project.query.filter_by(id=project_id).first()
    tasks = Task.query.filter_by(project_id=project_id)
    users = User.query.all()
    return render_template('project_task.html', title='Task', tasks=tasks, users=users, project=project)


@login_required
@app.route("/project_update/<int:project_id>", methods=['GET', 'POST'])
def project_update(project_id):
    form = ProjectForm()
    project = Project.query.get(project_id)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.team_lead.data).first()
        user_id = user.id

        project.title = form.title.data
        project.description = form.description.data
        project.team_lead = user_id
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.status = form.status.data
        db.session.commit()
        flash('Your project has been updated!', 'success')
        return redirect(url_for('home'))

    elif request.method == 'GET':
        user = User.query.filter_by(id=project.team_lead).first()

        form.title.data = project.title
        form.description.data = project.description
        form.team_lead.data = user.username
        form.start_date.data = project.start_date
        form.end_date.data = project.end_date
        form.status.data = project.status 
        
    return render_template('project_update.html', title='Project Update', form=form)


@login_required
@app.route("/task", methods=['GET', 'POST'])
def task():
    form = TaskForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.developer.data).first()
        user_id = user.id

        project = Project.query.filter_by(title=form.project.data).first()
        project_id = project.id

        task = Task(project_id=project_id ,title=form.title.data, details=form.detail.data,
                developer=user_id, start_date=form.start_date.data,
                end_date=form.end_date.data, status=form.status.data)
        db.session.add(task)
        db.session.commit()
        flash('Congratulations, Your task has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('task.html', title='Task', form=form)



@login_required
@app.route("/task_update/<int:task_id>", methods=['GET', 'POST'])
def task_update(task_id):
    form = TaskForm()
    task = Task.query.get(task_id)
    project = Project.query.filter_by(id=task.project_id).first()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.developer.data).first()
        user_id = user.id

        project = Project.query.filter_by(title=form.project.data).first()
        project_id = project.id

        task.project = project_id
        task.title = form.title.data
        task.details = form.detail.data
        task.developer = user_id
        task.start_date = form.start_date.data
        task.end_date = form.end_date.data
        task.status = form.status.data
        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('project_task', project_id=project_id))

    elif request.method == 'GET':
        user = User.query.filter_by(id=task.developer).first()
        project1 = Project.query.get(project.id)
        project_title = project1.title
        form.project.data = project_title
        form.title.data = task.title
        form.detail.data = task.details
        form.developer.data = user.username
        form.start_date.data = task.start_date
        form.end_date.data = task.end_date
        form.status.data = task.status 
        
    return render_template('task_update.html', title='Task Update', form=form)


@login_required
@app.route('/status_update/<int:task_id>', methods=['GET', 'POST'])
def status_update(task_id):
    form = UpdateStatusForm()
    task = Task.query.get(task_id)
    project = Project.query.get(task.project_id)

    if form.validate_on_submit():
        task.status = form.status.data
        db.session.commit()
        flash('Your status has been updated!', 'success')
        return redirect(url_for('home'))

    elif request.method == 'GET':
        form.status.data = task.status

    return render_template('status_update.html', title='Update Status', form=form, task=task, project=project) 


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)




@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@login_required
@app.route('/attendance')
def attendance():
    attendance = Attendance.query.all()
    return render_template('attendance.html', title='Attendance', attendance=attendance)