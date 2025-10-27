# -*- coding: utf-8 -*-
"""
Created on March 11, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

from app import app, db
from flask import render_template, request, url_for, redirect, session
from models import User, Education, Project, Organization, Schedule, Account

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/display_login')
def display_login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():    
    msg = ''
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
    
        account = Account.query.filter_by(username=username, password=password).first()
        user = User.query.filter(User.account.has(id=account.id)).first()
        if account:
            session['loggedin'] = True
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            msg = 'Incorrect username/password!'    
    return render_template('login.html', msg=msg)    

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('/display_login'))
 
@app.route('/display_create_account')
def display_create_account():
    return render_template('create_account.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():    
    msg = ''
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        birthday = request.form.get("birthday")
        username = request.form.get("username")
        password = request.form.get("password")
        
        try:
            if first_name != '' and last_name != '' and birthday and username != '' and password != '':
                new_user = User(first_name=first_name, last_name=last_name, birthday=birthday)
                db.session.add(new_user)
                db.session.commit()
                
                user_id = new_user.id
                new_account = Account(username=username, password=password, user_id=user_id)
                db.session.add(new_account)
                db.session.commit()
                return redirect(url_for('index')) 
            else: 
                msg = 'Invalid first name/last name/birthday/username/password!'
                # msg = f"{first_name}, {last_name}, {birthday}, {username}, {password}"
        except:
            msg = 'Username is already taken!'
    return render_template('create_account.html', msg=msg)  

@app.route('/add_education', methods=['GET', 'POST'])
def add_education():    
    msg = ''
    if request.method == 'POST':
        name = request.form.get("name")
        degrees = request.form.get("degrees")
        fields_of_study = request.form.get("fields_of_study")
        start_date = request.form.get("start_date")
        if not start_date: 
            start_date = None
        end_date = request.form.get("end_date")
        if not end_date: 
            end_date = None
        is_ongoing = request.form.get("is_ongoing")
        if is_ongoing == "on":
            is_ongoing = True
        else:
            is_ongoing = False
        
        user_id = session['user_id']
        
        try:
            if name != '':
                new_education = Education(name=name, degrees=degrees, fields_of_study=fields_of_study, \
                start_date=start_date, end_date=end_date, is_ongoing=is_ongoing, user_id=user_id)
                db.session.add(new_education)
                db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            msg = 'Name is already taken!'
            # msg = f"{name}, {degrees}, {fields_of_study}, {start_date}, {end_date}, {is_ongoing}"
    return render_template('add_education.html', msg=msg, fields_of_study_list=fields_of_study_list, degrees_list=degrees_list) 

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():    
    msg = ''
    if request.method == 'POST':
        name = request.form.get("name")
        tags = request.form.get("tags")
        start_date = request.form.get("start_date")
        if not start_date: 
            start_date = None
        end_date = request.form.get("end_date")
        if not end_date: 
            end_date = None
        is_ongoing = request.form.get("is_ongoing")
        if is_ongoing == "on":
            is_ongoing = True
        else:
            is_ongoing = False
        
        user_id = session['user_id']
        
        try:
            if name != '':
                new_project = Project(name=name, tags=tags, start_date=start_date, \
                end_date=end_date, is_ongoing=is_ongoing, user_id=user_id)
                db.session.add(new_project)
                db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            # msg = 'Name is already taken!'
            msg = f"{name}, {tags}, {start_date}, {end_date}, {is_ongoing}"
    return render_template('add_project.html', msg=msg, project_tags_list=project_tags_list) 

@app.route('/add_organization', methods=['GET', 'POST'])
def add_organization():    
    msg = ''
    if request.method == 'POST':
        name = request.form.get("name")
        tags = request.form.get("tags")
        start_date = request.form.get("start_date")
        if not start_date: 
            start_date = None
        end_date = request.form.get("end_date")
        if not end_date: 
            end_date = None
        is_ongoing = request.form.get("is_ongoing")
        if is_ongoing == "on":
            is_ongoing = True
        else:
            is_ongoing = False
        
        user_id = session['user_id']
        
        try:
            if name != '':
                new_organization = Organization(name=name, tags=tags, start_date=start_date, \
                    end_date=end_date, is_ongoing=is_ongoing, user_id=user_id)
                db.session.add(new_organization)
                db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            msg = 'Name is already taken!'
    return render_template('add_organization.html', msg=msg, organization_tags_list=organization_tags_list) 

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():    
    msg = ''
    
    user_id = session.get('user_id')
    projects = []
    organizations = []
    if user_id:
        projects = Project.query.filter_by(user_id=user_id).all()
        organizations = Organization.query.filter_by(user_id=user_id).all()
        
    if request.method == 'POST':
        
        name = request.form.get("name")
        mo = request.form.get("Mo")
        tu = request.form.get("Tu")
        we = request.form.get("We")
        th = request.form.get("Th")
        fr = request.form.get("Fr")
        sa = request.form.get("Sa")
        su = request.form.get("Su")
        if not mo: 
            mo = ""
        if not tu: 
            tu = ""
        if not we: 
            we = ""
        if not th: 
            th = ""
        if not fr: 
            fr = ""
        if not sa: 
            sa = ""
        if not su: 
            su = ""
        days = mo + tu + we + th + fr + sa + su
            
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        if not start_time: 
            start_time = None
        if not end_time: 
            end_time = None
        
        try:
            if name != '':
                new_schedule = Schedule(name=name, days=days, start_time=start_time, \
                    end_time=end_time, user_id=user_id)
                db.session.add(new_schedule)
                db.session.commit()
                
                if projects:
                    for project in projects:
                        project.schedule_id = new_schedule.id
                        
                if organizations:
                    for organization in organizations:
                        organization.schedule_id = new_schedule.id
                        
                db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            # msg = 'Name is already taken!'
            msg = f"{name}, {days}, {start_time}, {end_time}, {user_id}"
    return render_template('add_schedule.html', msg=msg, projects=projects, organizations=organizations) 

@app.route('/delete_education/<int:id>')
def delete_education(id):
    education = Education.query.get(id)
    if education:
        db.session.delete(education)
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/delete_project/<int:id>')
def delete_project(id):
    project = Project.query.get(id)
    if project:
        db.session.delete(project)
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/delete_organization/<int:id>')
def delete_organization(id):
    organization = Organization.query.get(id)
    if organization:
        db.session.delete(organization)
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/delete_schedule/<int:id>')
def delete_schedule(id):
    schedule = Schedule.query.get(id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        account = Account.query.filter_by(user_id=user.id).first()
        if account:
            db.session.delete(account)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('index'))