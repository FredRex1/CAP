from flask import Flask, redirect, url_for, render_template, request
import pymssql
import re

# connect ms sql
conn = pymssql.connect(host='host', database='database',
                       user='user', password='password', charset='utf8')
cursor = conn.cursor()
app = Flask(__name__)


@app.route("/")
def start():
    return render_template("start.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # not sure need sign up page
    msg = ''
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'dateofbirth' in request.form and 'ssn' in request.form and 'adderss' in request.form and 'gender' in request.form and 'email' in request.form:
        fname = request.form['firstname']
        lname = request.form['lastname']
        birth = request.form['dateofbirth']
        ssn = request.form['ssn']
        adderss = request.form['adderss']
        gender = request.form['gender']
        email = request.form['email']

        cursor.execute(
            'SELECT * FROM [sample].[dbo].[user] WHERE [email] = %s', (email))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[0-9]+', ssn):
            msg = 'ssn must contain only numbers !'
        else:
            # not inster to the database
            # yet id not sure provide by paratus or create by user
            # cursor.execute('INSERT INTO [sample].[dbo].[user] VALUES ( %s, %s, %s, %s, %s, %s, %s);', (
            #   fname, lname, email, ssn, birth, adderss, gender))
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template("signup.html", msg=msg)


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'id' in request.form and 'password' in request.form:
        # ask id, id not sure provide by paratus or create by user
        id = request.form['id']
        password = request.form['password']
        cursor.execute(
            'SELECT [id],[password] FROM [sample].[dbo].[user] WHERE [id] = %s AND [password] = %s', (id, password))
        account = cursor.fetchone()
        if account:
            msg = 'login success'
            # need to redirect to the file page
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
