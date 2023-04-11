from flask import Flask, redirect, url_for, render_template, request, session, make_response, send_from_directory
from datetime import timedelta, datetime
import pymssql
import re
from werkzeug.utils import secure_filename
import random
import os


# connect ms sql
conn = pymssql.connect(
    host="DESKTOP-NH8EEHF", database="test", user="testuser", password="1234", charset="utf8"
)
cursor = conn.cursor()
app = Flask(__name__)
app.secret_key = "very_happy_key"
app.permanent_session_lifetime = timedelta(minutes=300)


@app.route("/")
def start():
    if "userid" in session:
        msg = "already login"
        return redirect(url_for("dashboard"))
    return render_template("start.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    # not sure need sign up page
    msg = ""
    if (
        request.method == "POST"
        and "firstname" in request.form
        and "lastname" in request.form
        and "dateofbirth" in request.form
        and "ssn" in request.form
        and "adderss" in request.form
        and "gender" in request.form
        and "email" in request.form
    ):
        fname = request.form["firstname"]
        lname = request.form["lastname"]
        birth = request.form["dateofbirth"]
        ssn = request.form["ssn"]
        adderss = request.form["adderss"]
        gender = request.form["gender"]
        email = request.form["email"]
        name = fname + " " + lname
        id = 0 
        cursor.execute(
            "SELECT * FROM [test].[dbo].[user] WHERE [UserEmail] = %s", (email)
        )
        account = cursor.fetchone()
        if account:
            msg = "Account already exists !"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"
        elif not re.match(r"[0-9]+", ssn):
            msg = "ssn must contain only numbers !"
        else:
            # not inster to the database
            # yet id not sure provide by paratus or create by user
            id = random.randint(2, 100000)
            cursor.execute('INSERT INTO [test].[dbo].[user] VALUES ( %s, %s, %s, %s, 1, 2);', (id, name + lname, email, birth))
            conn.commit()
            session["userid"] = id
            msg = "You have successfully registered !"
            return redirect(url_for("dashboard"))
    elif request.method == "POST":
        msg = "Please fill out the form !"

    return render_template("signup.html", msg=msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if "userid" in session:
        msg = "already login"
        return redirect(url_for("dashboard"))

    if (
        request.method == "POST"
        and "AccountNumber" in request.form
        and "dateofbirth" in request.form
    ):
        # ask id, id not sure provide by paratus or create by user
        AccountNumber = request.form["AccountNumber"]
        birth = request.form["dateofbirth"]
        cursor.execute(
            "SELECT [UserID],[UserEmail],[UserPassword] FROM [test].[dbo].[user] WHERE [UserEmail] = %s AND [UserPassword] = %s",
            (AccountNumber, birth),
        )
        account = cursor.fetchone()
        if account:
            msg = "login success"
            session.permanent = True
            print("success")
            # record userid in session for search propose
            session["userid"] = account[0]
            # need to redirect to the file page
            return redirect(url_for("dashboard"))
        else:
            msg = "Incorrect username / password !"
            print("faild")

    return render_template("login.html", msg=msg)


@app.route("/accountPage")
def accountPage():
    #info pull from data base later
    #put info to json and send back to html
    accountinfo = []
    #TODO: PULL INFO from the database or user saved info form session
    userid = session["userid"]
    cursor.execute(
            "SELECT [UserName], [UserEmail] FROM [test].[dbo].[user] WHERE [UserID] = %s",(userid)
    )
    account = cursor.fetchone()
    if account:
        accountinfo = account + ("1234567890","this is a fake addresss")
        return render_template("accountPage.html", accountinfo = accountinfo)
    #  the db do not have phone and address
    #  'phone': account[3],
    #  'address': account[4],
    
    #accountinfo = '{ "name":"First name", "email":"example@gmail.com", "phone":"1234567890", "Address": "123456"}'
    return render_template("accountPage.html", accountinfo = accountinfo)


@app.route("/accountPageEdit", methods = ['GET'])
def accountPageEdit():
        
    userid = session["userid"]
    cursor.execute(
            "SELECT [UserName], [UserEmail] FROM [test].[dbo].[user] WHERE [UserID] = %s",(userid)
    )
    account = cursor.fetchone()
    accountinfo = account + ("1234567890" , "this is a fake addresss")

    return render_template("accountPageEdit.html", accountinfo = accountinfo)

@app.route("/accountPageEdit", methods = ['POST'])
def updateAccount():
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'phone' in request.form and 'address' in request.form:
        print("pass")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        #TODO: update the database
        cursor.execute("UPDATE [test].[dbo].[user] SET [UserName] = %s, [UserEmail] = %s WHERE [UserID] = %s", (name, email, session["userid"]))
        # Commit the changes to the database
        conn.commit()

        message = "update success"
        return redirect(url_for("accountPage"))
    return redirect(url_for("accountPageEdit"))

@app.route("/dashboard")
def dashboard():    
    #TODO PULL PULL INFO from the database or user saved info form session
    userid = session["userid"]
    cursor.execute(
            "SELECT [UserID], [UserName] FROM [test].[dbo].[user] WHERE [UserID] = %s",(userid)
    )
    account = cursor.fetchone()
    if account:    
        name = account[1]

    return render_template("dashboard.html", name = name)



@app.route("/myFiles", methods=["GET", "POST"])
def myFiles():
    #TODO: return all file as request form at HTML Page such as picture and file path to download
    userid = session["userid"]
    cursor.execute("SELECT [FileID] FROM [test].[dbo].[UserReport] WHERE [UserID]= %s", (userid))
    fileIds = [row[0] for row in cursor.fetchall()]

    # Retrieve file information for all file IDs
    files = []
    for fileId in fileIds:
        cursor.execute("SELECT * FROM [test].[dbo].[File] WHERE [FileID]= %s", (fileId))
        row = cursor.fetchone()
        if row:
            file_dict = {
                'FileID': row[0],
                'FileName': row[1],
                'FilePath': row[2],
                'HospitalSystemRegionID': row[3]
            }
            files.append(file_dict)

    fileinfo = "amy be json file of info"
    return render_template("myFiles.html", fileinfo = fileinfo)

#import this
#  from werkzeug.utils import secure_filename
#  import os
#  from flask import make_response
app.config['UPLOAD_EXTENSIONS'] = [".pdf", ".doc", ".png", ".jpg", ".docx"]
app.config['UPLOAD_PATH'] = 'File'

@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                #TODO raise error
                return make_response("error")
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            #TODO save file path to database
            id = random.randint(2, 100000)
            id2 = random.randint(2, 100000)
            cursor.execute('INSERT INTO [test].[dbo].[File] VALUES ( %s, %s, %s, 1);', (id, filename, os.path.join(app.config['UPLOAD_PATH'], filename)))
            cursor.execute('INSERT INTO [test].[dbo].[UserReport] VALUES ( %s, %s, %s, %s, %s);', (id2, datetime.now(), filename, session["userid"], id))
            conn.commit()
            #print(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect(url_for("myFiles"))

    return render_template("upload.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("start"))


@app.route("/why")
def why():
    return render_template("why.html")


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")



if __name__ == "__main__":
    app.run(debug=True)
