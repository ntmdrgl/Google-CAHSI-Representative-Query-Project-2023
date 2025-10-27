# -*- coding: utf-8 -*-
"""
Created on March 11, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    
    account = db.relationship('Account', backref='user', uselist=False)
    educations = db.relationship('Education', backref='user')
    projects = db.relationship('Project', backref='user')
    organizations = db.relationship('Organization', backref='user')
    schedules = db.relationship('Schedule', backref='user')
    
degrees_set = 'Associate', 'Bachelor', 'Graduate', 'Professional', 'Doctoral'
degrees_list = ['Associate', 'Bachelor', 'Graduate', 'Professional', 'Doctoral']

fields_of_study_set =\
    'Theory of computation', \
    'Information and coding theory', \
    'Data structures and algorithms', \
    'Programming language theory and formal methods',\
    'Computer graphics and visualization', \
    'Image and sound processing', \
    'Computational science finance and engineering', \
    'Social computing and human–computer interaction', \
    'Software engineering', \
    'Artificial intelligence', \
    'Computer architecture and organization', \
    'Concurrent, parallel and distributed computing', \
    'Computer networks', \
    'Computer security and cryptography', \
    'Databases and data mining'
    
fields_of_study_list = [
    'Theory of computation', 
    'Information and coding theory', 
    'Data structures and algorithms', 
    'Programming language theory and formal methods',
    'Computer graphics and visualization', 
    'Image and sound processing', 
    'Computational science finance and engineering', 
    'Social computing and human–computer interaction', 
    'Software engineering', 
    'Artificial intelligence', 
    'Computer architecture and organization', 
    'Concurrent, parallel and distributed computing', 
    'Computer networks', 
    'Computer security and cryptography', 
    'Databases and data mining'
]
    
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    days = db.Column(db.String(50), nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    
    # events = db.relationship('Event', backref='schedule')
    projects = db.relationship('Project', backref='schedule')
    organizations = db.relationship('Organization', backref='schedule')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
# Foreign keys must be declared after the models are created
    
class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    degrees = db.Column(db.Enum('Associate', 'Bachelor', 'Graduate', 'Professional', 'Doctoral'), nullable=True)
    fields_of_study = db.Column(db.Enum('Theory of computation', \
    'Information and coding theory', \
    'Data structures and algorithms', \
    'Programming language theory and formal methods',\
    'Computer graphics and visualization', \
    'Image and sound processing', \
    'Computational science finance and engineering', \
    'Social computing and human–computer interaction', \
    'Software engineering', \
    'Artificial intelligence', \
    'Computer architecture and organization', \
    'Concurrent, parallel and distributed computing', \
    'Computer networks', \
    'Computer security and cryptography', \
    'Databases and data mining'), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_ongoing = db.Column(db.Boolean, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
project_tags_set =\
    'Publication', \
    'Presentation', \
    'Software', \
    'Dataset'
project_tags_list = [
    'Publication', 
    'Presentation', 
    'Software', 
    'Dataset'
]

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    tags = db.Column(db.Enum('Publication', \
    'Presentation', \
    'Software', \
    'Dataset'), nullable=True)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_ongoing = db.Column(db.Boolean, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)
    
organization_tags_set =\
    'Academic', \
    'Industry', \
    'Non-Profit', \
    'State', \
    'Federal', \
    'International', \
    'Educational', \
    'Agricultural', \
    'Third Party', \
    'Charity'

organization_tags_list = [
    'Academic', 
    'Industry', 
    'Non-Profit', 
    'State', 
    'Federal', 
    'International', 
    'Educational', 
    'Agricultural', 
    'Third Party', 
    'Charity'
]

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    tags = db.Column(db.Enum('Academic', \
    'Industry', \
    'Non-Profit', \
    'State', \
    'Federal', \
    'International', \
    'Educational', \
    'Agricultural', \
    'Third Party', \
    'Charity'), nullable=True)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_ongoing = db.Column(db.Boolean, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)

# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     days = db.Column(db.Enum('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'), nullable=True)
#     start_time = db.Column(db.Time, nullable=True)
#     end_time = db.Column(db.Time, nullable=True)
    
    # schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)