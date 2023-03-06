from flask import Flask, redirect, url_for, render_template, request
import pymssql

conn = pymssql.connect(host='your host', database='daba base name',
                       user='user name', password='password', charset='utf8')
cursor = conn.cursor()

app = Flask(__name__)


@app.route("/")
def start():
    return render_template("start.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
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


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/why")
def why():
    return render_template("why.html")


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


if __name__ == "__main__":
    app.run(debug=True)
