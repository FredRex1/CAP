from flask import Flask, redirect, url_for, render_template

<<<<<<< Updated upstream
=======
# connect ms sql
conn = pymssql.connect(host='DESKTOP-HDBD7J8', database='test', user='test', password='test12345', charset='utf8')
cursor = conn.cursor()
>>>>>>> Stashed changes
app = Flask(__name__)

@app.route("/")
def start():
	return render_template("start.html")

@app.route("/signup")
def signup():
	return render_template("signup.html")

<<<<<<< Updated upstream
@app.route("/login")
def login():
	return render_template("login.html")

@app.route("/why")
def why():
	return render_template("why.html")

@app.route("/aboutus")
def aboutus():
	return render_template("aboutus.html")
=======
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

@app.route("/files")
def files():
    return render_template("files.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if "userid" in session:
        msg = "already login"
        return render_template('login.html', msg=msg)

    if request.method == 'POST' and 'AccountNumber' in request.form and 'dateofbirth' in request.form:
        # ask id, id not sure provide by paratus or create by user
        AccountNumber = request.form['AccountNumber']
        birth = request.form['dateofbirth']
        cursor.execute(
            'SELECT [Username],[UserPassword] FROM [test].[dbo].[user] WHERE [Username] = %s AND [UserPassword] = %s', (AccountNumber, birth))
        account = cursor.fetchone()
        if account:
            msg = 'login success'
            session.permanent = True
            print("success")
            # record userid in session for search propose
            session["userid"] = AccountNumber
            # need to redirect to the file page
            return render_template('files.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
            print("faild")

    return render_template('login.html', msg=msg)


@app.route("/why")
def why():
    return render_template("why.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")
>>>>>>> Stashed changes

if __name__ == "__main__":
	app.run(debug=True)
