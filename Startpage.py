from flask import Flask, redirect, url_for, render_template, request
import pymssql
import re


conn = pymssql.connect(host='host', database='database',
                       user='user', password='password', charset='utf8')
cursor = conn.cursor()

app = Flask(__name__)


@app.route("/")
def start():
    return render_template("start.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'firstname' in request.form and 'lastname' in request.form and 'dateofbirth' in request.form and 'ssn' in request.form and 'adderss' in request.form and 'gender' in request.form and 'email' in request.form:
		username = request.form['username']
		fname = request.form['firstname']
		lname = request.form['lastname']
		birth = request.form['dateofbirth']
		ssn = request.form['ssn']
		adderss = request.form['adderss']
		gender = request.form['gender']
		email = request.form['email']
                
		cursor.execute('SELECT * FROM [sample].[dbo].[user] WHERE [username] = %s', (username))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cursor.execute('INSERT INTO [sample].[dbo].[user] VALUES (%s, %s, %s, %s, %s, %s, %s, %s);', (username, fname, lname, email, ssn, birth, adderss, gender))
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'

	return render_template("signup.html", msg = msg)



@app.route("/login", methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute(
            'SELECT [username],[password] FROM [sample].[dbo].[user] WHERE [username] = %s AND [password] = %s', (username, password))
        account = cursor.fetchone()
        if account:
            msg = 'login success'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'

    return render_template('login.html', msg=msg)

@app.route("/why")
def why():
    return render_template("why.html")


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


if __name__ == "__main__":
    app.run(debug=True)
