# -*- coding: utf-8 -*-
"""
Created on March 11, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

import os
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from flask_migrate import Migrate, migrate

import networkx as nx
import matplotlib.pyplot as plt

import pickle

# Open directory to app.py and env
# Activate env: artifactenv\scripts\activate 
# Run app: python app.py

# from app import app, db
# with app.app_context():
#     db.create_all()

# flask db migrate
# flask db upgrade

# sqlalchemy.url = mysql+pymysql://root:Password123!@localhost:3306/artifactdb


# basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'my secret key'
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Password123!@localhost:3306/artifactdb' # + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)


# CATEGORIES

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


# TABLES

project_connection = db.Table('project_connection',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('connection_id', db.Integer, db.ForeignKey('connection.id'), primary_key=True)
)

organization_connection = db.Table('organization_connection',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
    db.Column('connection_id', db.Integer, db.ForeignKey('connection.id'), primary_key=True)
)

project_schedule = db.Table('project_schedule',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.id'), primary_key=True)
)

organization_schedule = db.Table('organization_schedule',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
    db.Column('connection_id', db.Integer, db.ForeignKey('schedule.id'), primary_key=True)
)

# MODELS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    private = db.Column(db.Boolean, nullable=True)
    
    account = db.relationship('Account', backref='user', uselist=False)
    connections = db.relationship('Connection', foreign_keys="[Connection.user_id]", backref='user')
    educations = db.relationship('Education', backref='user')
    projects = db.relationship('Project', backref='user')
    organizations = db.relationship('Organization', backref='user')
    schedules = db.relationship('Schedule', backref='user')
    requests = db.relationship('Request', foreign_keys="[Request.recipient_id]", backref='user')
    
# Foreign keys must be declared after the models are created
    
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    days = db.Column(db.String(50), nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    private = db.Column(db.Boolean, nullable=True)
    
    # projects = db.relationship('Project', backref='schedule')
    # organizations = db.relationship('Organization', backref='schedule')
    
    projects = db.relationship('Project', secondary=project_schedule, lazy='subquery', 
        backref=db.backref('schedules', lazy=True))
    organizations = db.relationship('Organization', secondary=organization_schedule, lazy='subquery', 
        backref=db.backref('schedules', lazy=True))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    # projects = db.relationship('Project', backref='project')
    # organizations = db.relationship('Organization', backref='organization')
    
    projects = db.relationship('Project', secondary=project_connection, lazy='subquery', 
        backref=db.backref('connections', lazy=True))
    organizations = db.relationship('Organization', secondary=organization_connection, lazy='subquery', 
        backref=db.backref('connections', lazy=True))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connection_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
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
    private = db.Column(db.Boolean, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
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
    private = db.Column(db.Boolean, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)
    # connection_id = db.Column(db.Integer, db.ForeignKey('connection.id'), nullable=True)

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
    private = db.Column(db.Boolean, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)
    # connection_id = db.Column(db.Integer, db.ForeignKey('connection.id'), nullable=True)
    
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(150), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    

# ROUTES
    
@app.route('/')
def index():
    users = User.query.all()
    
    return render_template('index.html', users=users)

@app.route('/graph')
def graph():
    G = nx.Graph()
    
    # # open('graph.pickle', 'wb').close()
    
    # # File path for pickle file
    # pickle_file_path = 'graph.pickle'
    
    # # Clear the existing pickle file
    # with open(pickle_file_path, 'wb') as open_file:
    #     open_file.truncate(0)
    
    for user in User.query.all():
        G.add_node(f"User_{user.id}", label=f"U: {user.first_name}", node_type='user')
        # for connection in user.connections:
        #     G.add_node(f"Connection_{connection.id}", label=f"Connection: {connection.name}", node_type='connection')
        for education in user.educations:
            G.add_node(f"Education_{education.id}", label=f"E: {education.name}", node_type='education')
        for project in user.projects:
            G.add_node(f"Project_{project.id}", label=f"P: {project.name}", node_type='project')
        for organization in user.organizations:
            G.add_node(f"Organization_{organization.id}", label=f"O: {organization.name}", node_type='organization')
        for schedule in user.schedules:
            G.add_node(f"Schedule_{schedule.id}", label=f"S: {schedule.name}", node_type='schedule')
    
    for user in User.query.all():
        for connection in user.connections:
            G.add_edge(f"User_{user.id}", f"User_{connection.connection_id}", node_type='user')
            for project in connection.projects:
                G.add_edge(f"User_{connection.connection_id}", f"Project_{project.id}", node_type='project')
            for organization in connection.organizations:
                G.add_edge(f"User_{connection.connection_id}", f"Organization_{organization.id}", node_type='organization')
        for education in user.educations:
            G.add_edge(f"User_{user.id}", f"Education_{education.id}", node_type='education')
        for project in user.projects:
            G.add_edge(f"User_{user.id}", f"Project_{project.id}", node_type='project')
        for organization in user.organizations:
            G.add_edge(f"User_{user.id}", f"Organization_{organization.id}", node_type='organization')
        for schedule in user.schedules:
            G.add_edge(f"User_{user.id}", f"Schedule_{schedule.id}", node_type='schedule')
            for project in schedule.projects:
                G.add_edge(f"Schedule_{schedule.id}", f"Project_{project.id}", node_type='project')
            for organization in schedule.organizations:
                G.add_edge(f"Schedule_{schedule.id}", f"Organization_{organization.id}", node_type='organization')
  
    node_colors = {
        'user': 'lightcoral',
        'education': 'lightgreen',
        'project': 'lightblue',
        'organization': 'lightsalmon',
        'schedule': 'lightpink'
    }
     
    node_color = []
    labels = {}
    
    for nodes in G:
        node_color.append(node_colors[G.nodes[nodes]['node_type']])
        labels[nodes] = G.nodes[nodes]['label']    
    
    print(G.nodes('node_type'))
    
    deg_centrality = nx.degree_centrality(G) 
    print("Degree Centrality:")
    for key, deg in deg_centrality.items():
        print("\t" + key + ":" + str(deg))
    
    print("Closeness Centrality:")
    close_centrality = nx.closeness_centrality(G) 
    for key, deg in close_centrality.items():
        print("\t" + key + ":" + str(deg))
    
    # user_ids = []
    # for nodes in node_list:
    #     index = nodes.rfind("User_")
    #     if index != -1:
    #         substring = nodes[index + 5:]
    #         user_ids.append(substring)
        
    # print("User Ids: " + str(user_ids))
    
    user_list = []
    for name, data in G.nodes.data():
        if data["node_type"] == "user":
            user_list.append(name)
    
    user_list_pair = []
    for index, a in enumerate(user_list):
        for b in user_list[index + 1:]:
            user_list_pair.append((a,b))          
    # print(user_list_pair)
    
    plt.clf()
    nx.draw_networkx(G, with_labels=True, labels=labels, node_color=node_color) 
    
    
    preds1 = nx.jaccard_coefficient(G, user_list_pair)
    preds2 = nx.adamic_adar_index(G, user_list_pair)
    preds3 = nx.preferential_attachment(G, user_list_pair)
    
    # for u, v, p in preds1:
    #     print(f"Jaccard Coefficient ({u}, {v}) -> {p:.8f}")
    #     pass
        
    for u, v, p in preds2:
        print(f"Adamic Adar Index ({u}, {v}) -> {p:.8f}")
        pass
    
    # for u, v, p in preds3:
    #     print(f"Preferential Attachment ({u}, {v}) -> {p:.8f}")
    #     pass
    
    plt.show()
    
    
    # save graph object to file
    with open('graph.pickle', 'wb') as open_file:
        pickle.dump(G, open_file)
        
    print(G)
        
    # with open('graph.pickle', 'rb') as open_file:
    #     pickle.load(open_file)
    
    return redirect(url_for('index')) 

# @app.route('/display_login')
# def display_login():
#     return render_template('login.html')

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
            return redirect(url_for('home'))
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
        return redirect(url_for('display_login'))
    
# @app.route('/network_1', methods=['GET', 'POST'])
# def network_1():
#     return 
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
            
            
        # Only include birthdays within a month from current date  
            # SELECT *
            # FROM user
            # JOIN (SELECT  connection.connection_id
            # FROM connection
            # JOIN user on user.id = connection.user_id
            # where connection.user_id = USER_ID AND user.private = false
            # ) AS sub
            # where user.id = sub.connection_id;
        
        # Sub query returns all connections of user
        result_connection_birthdays_subq = (
            db.select(Connection.connection_id)
            .join(User, User.id == Connection.user_id)
            .where(Connection.user_id == user.id, \
                   User.private == False, 
            )
            .subquery()
        )    
        # Main query find the user of all connections 
        result_connection_birthdays = []
        result_connection_birthdays = db.session.execute(
            db.select(User.first_name, User.last_name, User.birthday)
            .join(result_connection_birthdays_subq, \
                  User.id == result_connection_birthdays_subq.c.connection_id
            )
        ).all()
        
        current_date = datetime.today().date()
        later_date = current_date + timedelta(days=30)
        result_connection_birthdays_final = []
        for tup in result_connection_birthdays:
            birthday = tup[2]
            if current_date <= birthday.replace(year=current_date.year) <= later_date:
                result_connection_birthdays_final.append(tup)
                
        # print("\t main birthdays" + str(result_connection_birthdays))
        # print("\t filtered birthdays" + str(result_connection_birthdays_final))
        
        
         # ------ Share all projects from user's connections not including user's projects   
             # SELECT *
             # FROM project
             # JOIN (SELECT project_connection.connection_id
             #     FROM project_connection
             #     JOIN project ON project_connection.project_id = project.id
             #     WHERE project.user_id = USER_ID
             # ) AS sub
             # WHERE project.user_id != USER_ID;
        
        # result_connected_projects_subq = (
        #     db.select(project_connection.c.connection_id)
        #     .join(Project)
        #     .where(Project.user_id == user.id)
        #     .subquery()
        # )
        result_connected_projects = []
        # result_connected_projects = db.session.execute(
        #     db.select(Project.id, Project.name, Project.tags, Project.start_date, \
        #           Project.end_date, Project.is_ongoing, Project.schedules)
        #     .join(result_connected_projects_subq, Project.user_id != user.id)
        #     # .distinct(Project.id)
        # ).all()
        # # print("connected projects:" + str(result_connected_projects))
            
        # # 2. Share all organizations from user's connections not including user's projects 
        #     # Same SQL as project above ^^^
        # result_connected_organizations_subq = (
        #     db.select(organization_connection.c.connection_id)
        #     .join(Organization)
        #     .where(Organization.user_id == user.id)
        #     .subquery()
        # )
        result_connected_organizations = []
        # result_connected_organizations = db.session.execute(
        #     db.select(Organization.id, Organization.name, Organization.tags, Organization.start_date, \
        #           Organization.end_date, Organization.is_ongoing)
        #     .join(result_connected_organizations_subq, Organization.user_id != user.id)
        #     # .distinct(Organization.id)
        # ).all()
        
        result_connected_projects = db.session.execute(
            db.select(Project.id, Project.name, Project.tags, Project.start_date, \
                      Project.end_date, Project.is_ongoing)
            .where(Project.private == False)
        ).all()
        result_connected_organizations = db.session.execute(
            db.select(Organization.id, Organization.name, Organization.tags, Organization.start_date, \
                      Organization.end_date, Organization.is_ongoing)
            .where(Organization.private == False)
        ).all()    
        # print("\t connected_projects" + str(result_connected_projects))
        # print("\t connected_organizations" + str(result_connected_organizations))
        # print("\t connected projects: " + str(result_connected_projects))
            
        # ------ Recommend connection's of connections 
            # SELECT * -- user.first_name, user.last_name 
            # FROM user 
            # LEFT JOIN (SELECT connection.connection_id
            # 	FROM connection
            # 	WHERE connection.user_id = 25
            # ) AS sub 
            # ON user.id = sub.connection_id -- user's connection is with a user
            # WHERE sub.connection_id IS NULL AND user.id != 25; -- find user's without connections excluding the user
        
        # Find user's connections
        result_connected_connections_subq = (
            db.select(Connection.connection_id)
            .where(Connection.user_id == user.id)
            .subquery()
        ) 
        
        # Final all connections that aren't user's connections
        result_connected_connections_original = [] 
        # result_connected_connections_original = db.session.execute(
        #     db.select(User.id, User.first_name, User.last_name)
        #     .join(result_connected_connections_subq, User.id == result_connected_connections_subq.c.connection_id, isouter=True)
        #     .where(
        #         result_connected_connections_subq.c.connection_id == None, \
        #         User.id != user.id
        #     )
        # ).all()
        # print("Connected connections original:" + str(result_connected_connections_original))
        
        
        # Find all connections
        result_connected_connections = [] 
        result_connected_connections = db.session.execute(
            db.select(User.id, User.first_name, User.last_name)
        ).all()
        
        
        # ------ Make ordered list of weighted recommendations
        
        # load graph object from file
        G = pickle.load(open('graph.pickle', 'rb'))
            
        # --- 1. make list of nodes from graph
        user_list = []
        for name, data in G.nodes.data():
            if data["node_type"] == "user":
                user_list.append(name)
        # print(user_list)
        
        project_list = [] # users, projects, and organizations
        for name, data in G.nodes.data():
            if data["node_type"] == "project":
                project_list.append(name)
        # print("\t project_list " + str(project_list))
        
        organization_list = [] # users, projects, and organizations
        for name, data in G.nodes.data():
            if data["node_type"] == "organization":
                organization_list.append(name)
        # print("\t organization_list " + str(organization_list))
        
        # --- 2. make list of tuples of connected nodes
        
        user_list_pair = []
        for index, a in enumerate(user_list):
            for b in user_list[index + 1:]:
                user_list_pair.append((a,b))          
        # print(user_list_pair)
        
        project_list_pair = []
        for index, a in enumerate(project_list):
            for b in project_list[index + 1:]:
                project_list_pair.append((a,b))          
        # print("\t project_list_pair: " + str(project_list_pair))
        
        organization_list_pair = []
        for index, a in enumerate(organization_list):
            for b in organization_list[index + 1:]:
                organization_list_pair.append((a,b))          
        # print("\t organization_list_pair: " + str(organization_list_pair))
        
        # --- 3. make predicates
        
        preds_user = nx.adamic_adar_index(G, user_list_pair)
        preds_project = nx.adamic_adar_index(G, project_list_pair)
        preds_organization = nx.adamic_adar_index(G, organization_list_pair)
        
        # --- 4. make dictionaries
        
        result_connected_connections_dict = {}
        for tup in result_connected_connections: 
            key = tup[0]
            value = (tup[1], tup[2])  
            result_connected_connections_dict[key] = value
        # print("Dict: " + str(result_connected_connections_dict))
        
        result_connected_projects_dict = {}
        for tup in result_connected_projects: 
            key = tup[0]
            value = (tup[1], tup[2], tup[3], tup[4], tup[5])  
            result_connected_projects_dict[key] = value
        # print("\t Project Dict: " + str(result_connected_projects_dict))
        
        result_connected_organizations_dict = {}
        for tup in result_connected_organizations: 
            key = tup[0]
            value = (tup[1], tup[2], tup[3], tup[4], tup[5])  
            result_connected_organizations_dict[key] = value
        # print("\t Organization Dict: " + str(result_connected_organizations_dict))
        
        # --- 5. make weighted lists and transform to ignore certain pairs
    
        result_connected_connections_weighed = []
        for u, v, p in preds_user:
            # print("u ", u, " v ", v, " p ", p)
            if p != 0:
                if u == f"User_{user.id}":
                    v = int(v[(v.rfind("User_") + 5):]) # find id
                    (attr1, attr2) = result_connected_connections_dict.get(v, (None, None))
                    # print("v ", v, attr1, attr2)
                    if attr1 is not None and attr2 is not None:
                        result_connected_connections_weighed.append((v,attr1,attr2,p))
                elif v == f"User_{user.id}":
                    u = int(u[(u.rfind("User_") + 5):]) # find id
                    # print("u ", u, attr1, attr2)
                    (attr1, attr2) = result_connected_connections_dict.get(u, (None, None))
                    if attr1 is not None and attr2 is not None:
                        result_connected_connections_weighed.append((u,attr1,attr2,p))
        result_connected_connections_weighed.sort(key=lambda x:x[3], reverse=True)
        
        result_connected_connections_transformed = []
        for tup in result_connected_connections_weighed:
            isConnected = False
            for connection in user.connections:
                # print(str(connection.connection_id) + " " + str(a))
                if connection.connection_id == tup[0]:
                    isConnected = True
                    break
            if not isConnected:
                result_connected_connections_transformed.append(tup)
        
        result_connected_projects_weighed = []
        for project in user.projects:
            # print("project: ", str(project.id))
            for u, v, p in preds_project:
                # print("u ", u, " v ", v, " p ", p)
                if p != 0:
                    if u == f"Project_{project.id}":
                        if v.rfind("Project_") != -1:
                            v = int(v[(v.rfind("Project_") + 8):]) # find id
                            (attr1, attr2, attr3, attr4, attr5) = result_connected_projects_dict.get(v, (None, None, None, None, None))
                            # print("v ", v, attr1, attr2, attr3, attr4, attr5)
                            connected_project = Project.query.get(v)
                            if not connected_project.private:
                                result_connected_projects_weighed.append((v,attr1,attr2,attr3,attr4,attr5,p))
                    elif v == f"Project_{project.id}":
                        if u.rfind("Project_") != -1:
                            u = int(u[(u.rfind("Project_") + 8):]) # find id
                            # print("u ", u, attr1, attr2, attr3, attr4, attr5)
                            (attr1, attr2, attr3, attr4, attr5) = result_connected_projects_dict.get(u, (None, None, None, None, None))
                            connected_project = Project.query.get(u)
                            if not connected_project.private:
                                result_connected_projects_weighed.append((u,attr1,attr2,attr3,attr4,attr5,p))
        result_connected_projects_weighed.sort(key=lambda x:x[6], reverse=True)
            
        result_connected_projects_transformed = []
        for tup in result_connected_projects_weighed:
            isConnected = False
            for project in user.projects:
                # print(str(connection.connection_id) + " " + str(a))
                if project.id == tup[0]:
                    isConnected = True
                    break
            if not isConnected:
                result_connected_projects_transformed.append(tup)
                
        result_connected_organizations_weighed = []
        for organization in user.organizations:
            # print("organization: ", str(organization.id))
            for u, v, p in preds_organization:
                # print("u ", u, " v ", v, " p ", p)
                if p != 0 and not project.private:
                    if u == f"Organization_{organization.id}":
                        if v.rfind("Organization_") != -1:
                            v = int(v[(v.rfind("Organization_") + 13):]) # find id
                            (attr1, attr2, attr3, attr4, attr5) = result_connected_organizations_dict.get(v, (None, None, None, None, None))
                            # print("v ", v, attr1, attr2, attr3, attr4, attr5)
                            connected_organization = Organization.query.get(v)
                            if not connected_organization.private:
                                result_connected_organizations_weighed.append((v,attr1,attr2,attr3,attr4,attr5,p))
                    elif v == f"Organization_{organization.id}":
                        if u.rfind("Organization_") != -1:
                            u = int(u[(u.rfind("Organization_") + 13):]) # find id
                            # print("u ", u, attr1, attr2, attr3, attr4, attr5)
                            (attr1, attr2, attr3, attr4, attr5) = result_connected_organizations_dict.get(u, (None, None, None, None, None))
                            connected_organization = Organization.query.get(u)
                            if not connected_organization.private:
                                result_connected_organizations_weighed.append((u,attr1,attr2,attr3,attr4,attr5,p))
        result_connected_organizations_weighed.sort(key=lambda x:x[6], reverse=True)
            
        result_connected_organizations_transformed = []
        for tup in result_connected_organizations_weighed:
            isConnected = False
            for organization in user.organizations:
                # print(str(connection.connection_id) + " " + str(a))
                if organization.id == tup[0]:
                    isConnected = True
                    break
            if not isConnected:
                result_connected_organizations_transformed.append(tup)

        # print("\t Weighted Connections:" + str(result_connected_connections_weighed))
        # print("\t Transformed Connections:"+ str(result_connected_connections_transformed))
        
        # print("\t Weighted Projects:" + str(result_connected_projects_weighed))
        # print("\t Transformed Projects:"+ str(result_connected_projects_transformed))
        
        # print("\t Weighted Organizations:" + str(result_connected_organizations_weighed))
        # print("\t Transformed Organizations:"+ str(result_connected_organizations_transformed))
        
        user_requests = Request.query.filter_by(user_id=user.id).all()
        print("\t User requests: " + str(user_requests))
        for request in user_requests:
            print("\t User requests:" + str(request))
        
        return render_template('home.html', user=user, \
            result_connection_birthdays=result_connection_birthdays_final, \
            result_connected_projects=result_connected_projects_transformed, \
            result_connected_organizations=result_connected_organizations_transformed, \
            result_connected_connections=result_connected_connections_transformed
       )
    else:
        return redirect(url_for('display_login'))

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
        private = request.form.get("private")
        if private == "on":
            private = True
        else:
            private = False
        
        try:
            if first_name != '' and last_name != '' and birthday and username != '' and password != '':
                new_user = User(first_name=first_name, last_name=last_name, birthday=birthday, private=private)
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

@app.route('/add_connection', methods=['GET', 'POST'])
def add_connection():    
    msg = ''
    
    if request.method == 'POST':
        username = request.form.get("username")
        user_id = session['user_id']
        
        account = Account.query.filter_by(username=username).first()
        
        try:
            if account and account.user_id != user_id:
                # user = User.query.get(account.user_id)
                # new_connection = Connection(name=user.first_name+" "+user.last_name, user_id=user_id, connection_id=account.user_id)
                # db.session.add(new_connection)
                # db.session.commit()
                
                user = User.query.get(user_id)
                new_request = Request(name=user.first_name+" "+user.last_name, reason="", user_id=user_id, recipient_id=account.user_id)
                db.session.add(new_request)
                db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid username!'
        except:
            # msg = 'Name is already taken!'
            msg = f"{user.name}, {username}, {account.user_id}"
    return render_template('add_connection.html', msg=msg, ) 

@app.route('/add_education', methods=['GET', 'POST'])
def add_education():    
    msg = ''
    if request.method == 'POST':
        name = request.form.get("name")
        degrees = request.form.get("degrees")
        fields_of_study = request.form.get("fields_of_study")
        start_date = request.form.get("start_date")
        private = request.form.get("private")
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
        if private == "on":
            private = True
        else:
            private = False
        
        user_id = session['user_id']
        
        try:
            if name != '':
                new_education = Education(name=name, degrees=degrees, fields_of_study=fields_of_study, \
                start_date=start_date, end_date=end_date, is_ongoing=is_ongoing, private=private, user_id=user_id)
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
    
    user_id = session.get('user_id')
    connections = []
    if user_id:
        # connections = Connection.query.filter_by(user_id=user_id).all()
        user = User.query.get(user_id)
        connections = user.connections
    
    if request.method == 'POST':
        name = request.form.get("name")
        tags = request.form.get("tags")
        start_date = request.form.get("start_date")
        private = request.form.get("private")
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
        if private == "on":
            private = True
        else:
            private = False
        connection_ids = request.form.getlist("connections[]")
        if not connection_ids:
            connection_ids = None
        
        try:
            if name != '':
                new_project = Project(name=name, tags=tags, start_date=start_date, \
                end_date=end_date, is_ongoing=is_ongoing, private=private, user_id=user_id)
                db.session.add(new_project)
                db.session.commit()
                
                if connection_ids:
                    for connection_id in connection_ids:
                        connection = Connection.query.get(connection_id)
                        connection.projects.append(new_project)
                        db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            # msg = 'Name is already taken!'
            msg = f"{name}, {tags}, {connection_id}, {start_date}, {end_date}, {is_ongoing}, {private}"
    return render_template('add_project.html', msg=msg, project_tags_list=project_tags_list, connections=connections) 

@app.route('/add_organization', methods=['GET', 'POST'])
def add_organization():    
    msg = ''
    
    user_id = session.get('user_id')
    connections = []
    if user_id:
        # connections = Connection.query.filter_by(user_id=user_id).all()
        user = User.query.get(user_id)
        connections = user.connections
        
    if request.method == 'POST':
        name = request.form.get("name")
        tags = request.form.get("tags")
        start_date = request.form.get("start_date")
        private = request.form.get("private")
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
        if private == "on":
            private = True
        else:
            private = False
        connection_ids = request.form.getlist("connections[]")
        if not connection_ids:
            connection_ids = None
        
        try:
            if name != '':
                new_organization = Organization(name=name, tags=tags, start_date=start_date, \
                    end_date=end_date, is_ongoing=is_ongoing, private=private, user_id=user_id)
                db.session.add(new_organization)
                db.session.commit()
                
                if connection_ids:
                    for connection_id in connection_ids:
                        connection = Connection.query.get(connection_id)
                        connection.organizations.append(new_organization)
                        db.session.commit()

                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            msg = 'Name is already taken!'
    return render_template('add_organization.html', msg=msg, organization_tags_list=organization_tags_list, connections=connections) 

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():    
    msg = ''
    
    user_id = session.get('user_id')
    projects = []
    organizations = []
    if user_id:
        # projects = Project.query.filter_by(user_id=user_id).all()
        # organizations = Organization.query.filter_by(user_id=user_id).all()
        
        user = User.query.get(user_id)
        projects = user.projects
        organizations = user.organizations
        
    if request.method == 'POST':
        
        name = request.form.get("name")
        project_ids = request.form.getlist("projects[]")
        organization_ids = request.form.getlist("organizations[]")
        private = request.form.get("private")
        if private == "on":
            private = True
        else:
            private = False
        
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
        if not days:
            days = None
        
        try:
            if name != '':
                new_schedule = Schedule(name=name, days=days, start_time=start_time, \
                    end_time=end_time, private=private, user_id=user_id)
                db.session.add(new_schedule)
                db.session.commit()
                
                if project_ids:
                    for project_id in project_ids:
                        project = Project.query.get(project_id)
                        project.schedules.append(new_schedule)
                        
                if organization_ids:
                    for organization_id in organization_ids:
                        organization = Organization.query.get(organization_id)
                        organization.schedules.append(new_schedule)
                        
                db.session.commit()
                
                return redirect(url_for('profile')) 
            else: 
                msg = 'Invalid name!'
        except:
            # msg = 'Name is already taken!'
            msg = f"Error: {name}, {days}, {start_time}, {end_time}, {user_id}, Project: ({project_ids})"
            # msg = f"{requested_projects}"
    return render_template('add_schedule.html', msg=msg, projects=projects, organizations=organizations) 


@app.route('/send_request/<int:id>')
def send_request(id):
    
    user_id = session.get('user_id')
    # connection = Connection.query.get(id)
    user = User.query.get(user_id)
    
    try:
        if id:
            new_request = Request(name=user.first_name+" "+user.last_name, reason="", user_id=user_id, recipient_id=id)
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('home')) 
        else:
            pass
    except:
        pass
    return redirect(url_for('home'))

@app.route('/accept_request/<int:id>')
def accept_request(id):
    request = Request.query.get(id)
    if request:
        sender = User.query.get(request.user_id)
        recipient = User.query.get(request.recipient_id)
        if sender and recipient:
            new_connection_1 = Connection(name=recipient.first_name+" "+recipient.last_name,user_id=sender.id, connection_id=recipient.id)
            db.session.add(new_connection_1)
            new_connection_2 = Connection(name=sender.first_name+" "+sender.last_name, user_id=recipient.id, connection_id=sender.id)
            db.session.add(new_connection_2)
            db.session.commit()
            
            ignore_request(id)
    return redirect(url_for('home'))

@app.route('/ignore_request/<int:id>')
def ignore_request(id):
    request = Request.query.get(id)
    if request:
        db.session.delete(request)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/view_project_schedule/<int:id>')
def view_project_schedule(id):
    project = Project.query.get(id)
    return render_template('view_project_schedule.html', project=project) 

@app.route('/view_organization_schedule/<int:id>')
def view_organization_schedule(id):
    organization = Organization.query.get(id)
    return render_template('view_organization_schedule.html', organization=organization) 

@app.route('/view_connection_profile/<int:id>')
def view_connection_profile(id):
    connection = Connection.query.get(id)
    user = User.query.get(connection.connection_id)
    return render_template('view_connection_profile.html', user=user) 

@app.route('/private_user/<int:id>')
def private_user(id):
    user = User.query.get(id)
    user.private = not user.private
    db.session.commit()
    return redirect(url_for('profile')) 

@app.route('/private_education/<int:id>')
def private_education(id):
    education = Education.query.get(id)
    education.private = not education.private
    db.session.commit()
    return redirect(url_for('profile')) 

@app.route('/private_project/<int:id>')
def private_project(id):
    project = Project.query.get(id)
    project.private = not project.private
    db.session.commit()
    return redirect(url_for('profile')) 

@app.route('/private_organization/<int:id>')
def private_organization(id):
    organization = Organization.query.get(id)
    organization.private = not organization.private
    db.session.commit()
    return redirect(url_for('profile')) 

@app.route('/private_schedule/<int:id>')
def private_schedule(id):
    schedule = Schedule.query.get(id)
    schedule.private = not schedule.private
    db.session.commit()
    return redirect(url_for('profile')) 

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
        projects = schedule.projects
        organizations = schedule.organizations
        
        
        for project in projects:
            project.schedule_id = None
        for organization in organizations:
            organization.schedule_id = None
        db.session.commit()
        
        db.session.delete(schedule)
        db.session.commit()
    return redirect(url_for('profile'))

@app.route('/delete_connection/<int:id>')
def delete_connection(id):
    user_connection = Connection.query.get(id)
    connected_connection = Connection.query.filter_by(
        user_id=user_connection.connection_id,
        connection_id=user_connection.user_id
    ).first()
    if user_connection:
        user_projects = user_connection.projects
        user_organizations = user_connection.organizations
        for project in user_projects:
            project.connection_id = None
        for organization in user_organizations:
            organization.connection_id = None
        
        db.session.delete(user_connection)
        db.session.commit()
        
        if connected_connection:
            delete_connection(connected_connection.id)
    return redirect(url_for('profile'))

@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        account = user.account
        
        if account:
            db.session.delete(account)
            
        for connection in user.connections:
            delete_connection(connection.id)
        for education in user.educations:
            delete_education(education.id)
        for project in user.projects:
            delete_project(project.id)
        for organization in user.organizations:
            delete_organization(organization.id)
        for schedule in user.schedules:
            delete_schedule(schedule.id)
        
        user_requests = Request.query.filter_by(user_id=id).all()
        for request in user_requests:
            ignore_request(request.id)
        
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
    
    