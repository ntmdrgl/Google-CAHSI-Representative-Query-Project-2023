# -*- coding: utf-8 -*-
"""
Created on March 11, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL


app = Flask(__name__)

app.secret_key = 'your secret key'
 
app.config["MYSQL_USER"] = "localhost"
app.config["MYSQL_PASSWORD"] = "Password123"
app.config["MYSQL_DB"] = "artifactdb"

 
mysql = MySQL(app)

# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="Password123!",
#     database="artifactdb"
# ) 
# mycursor = connection.cursor()

@app.route("/")
def users():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT user, host FROM mysql.user""")
    rv = cur.fetchall()
    return str(rv)

if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"), debug=True)

# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         cursor = mysql.connection.cursor()
#         print(cursor)
#         cursor.execute(
#             'SELECT * FROM accounts WHERE username = % s \
#             AND a_password = % s', (username, password, ))
#         account = cursor.fetchone()
#         print(account)
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['id']
#             session['username'] = account['username']
#             msg = 'Logged in successfully !'
#             return render_template('index.html', msg=msg)
#         else:
#             msg = 'Incorrect username / password !'
#     return render_template('login.html', msg=msg)
 
 
# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     msg = ''
#     # if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode'
#     # in request.form and 'organisation' in request.form:
#     #     username = request.form['username']
#     #     password = request.form['password']
#     #     email = request.form['email']
#     #     organisation = request.form['organisation']
#     #     address = request.form['address']
#     #     city = request.form['city']
#     #     state = request.form['state']
#     #     country = request.form['country']
#     #     postalcode = request.form['postalcode']
#     #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     #     cursor.execute(
#     #         'SELECT * FROM accounts WHERE username = % s', (username, ))
#     #     account = cursor.fetchone()
#     #     if account:
#     #         msg = 'Account already exists !'
#     #     elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#     #         msg = 'Invalid email address !'
#     #     elif not re.match(r'[A-Za-z0-9]+', username):
#     #         msg = 'name must contain only characters and numbers !'
#     #     else:
#     #         cursor.execute('INSERT INTO accounts VALUES \
#     #         (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)',
#     #                        (username, password, email, 
#     #                         organisation, address, city,
#     #                         state, country, postalcode, ))
#     #         mysql.connection.commit()
#     #         msg = 'You have successfully registered !'
#     # elif request.method == 'POST':
#     #     msg = 'Please fill out the form !'
#     return render_template('register.html', msg=msg)
 
 
# @app.route("/index")
# def index():
#     if 'loggedin' in session:
#         return render_template("index.html")
#     return redirect(url_for('login'))
 
 
# @app.route("/display")
# def display():
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM accounts WHERE id = % s',
#                         (session['id'], ))
#         account = cursor.fetchone()
#         return render_template("display.html", account=account)
#     return redirect(url_for('login'))
 
 
# @app.route("/update", methods=['GET', 'POST'])
# def update():
#     msg = ''
#     # if 'loggedin' in session:
#     #     if request.method == 'POST' and 'username' in request.form 
#     #     and 'password' in request.form and 'email' in request.form and
#     #     'address' in request.form and 'city' in request.form and 'country'
#     #     in request.form and 'postalcode' in request.form and
#     #     'organisation' in request.form:
#     #         username = request.form['username']
#     #         password = request.form['password']
#     #         email = request.form['email']
#     #         organisation = request.form['organisation']
#     #         address = request.form['address']
#     #         city = request.form['city']
#     #         state = request.form['state']
#     #         country = request.form['country']
#     #         postalcode = request.form['postalcode']
#     #         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     #         cursor.execute(
#     #             'SELECT * FROM accounts WHERE username = % s',
#     #                   (username, ))
#     #         account = cursor.fetchone()
#     #         if account:
#     #             msg = 'Account already exists !'
#     #         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#     #             msg = 'Invalid email address !'
#     #         elif not re.match(r'[A-Za-z0-9]+', username):
#     #             msg = 'name must contain only characters and numbers !'
#     #         else:
#     #             cursor.execute('UPDATE accounts SET username =% s,\
#     #             password =% s, email =% s, organisation =% s, \
#     #             address =% s, city =% s, state =% s, \
#     #             country =% s, postalcode =% s WHERE id =% s', (
#     #                 username, password, email, organisation, 
#     #               address, city, state, country, postalcode, 
#     #               (session['id'], ), ))
#     #             mysql.connection.commit()
#     #             msg = 'You have successfully updated !'
#     #     elif request.method == 'POST':
#     #         msg = 'Please fill out the form !'
#     #     return render_template("update.html", msg=msg)
#     return redirect(url_for('login'))
 
 
# if __name__ == "__main__":
#     app.run(host="localhost", port=int("5000"))
     