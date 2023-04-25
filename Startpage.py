from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    request,
    session,
    make_response,
    send_from_directory,
)
from datetime import timedelta, datetime
import pymssql
import re
from werkzeug.utils import secure_filename
import random
import os


# connect ms sql
conn = pymssql.connect(
    host="localhost",
    database="test",
    user="user",
    password="pass-word",
    charset="utf8",
)

cursor = conn.cursor()
app = Flask(__name__)
app.secret_key = "very_happy_key"
app.permanent_session_lifetime = timedelta(minutes=300)
app.config["UPLOAD_EXTENSIONS"] = [".pdf", ".doc", ".png", ".jpg", ".docx"]
app.config["UPLOAD_PATH"] = "File"


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
            cursor.execute(
                "INSERT INTO [test].[dbo].[user] VALUES ( %s, %s, %s, %s, 1, 2);",
                (id, name + lname, email, birth),
            )
            conn.commit()
            session["userid"] = id
            cursor.execute(
                "SELECT [RoleName] FROM [test].[dbo].[Role] WHERE [RoleID] = %s",
                (2,),
            )
            rolename = cursor.fetchone()
            session["rolename"] = rolename[0]
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


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


@app.route("/accountPage")
def accountPage():
    if "userid" not in session:
        return render_template("logout.html")
    accountinfo = []
    # TODO
    # the db do not have phone and address update db
    userid = session["userid"]
    cursor.execute(
        "SELECT [UserName], [UserEmail] FROM [test].[dbo].[user] WHERE [UserID] = %s",
        (userid),
    )
    account = cursor.fetchone()
    if account:
        # TODO
        # the db do not have phone and address update db
        accountinfo = account + ("1234567890", "this is a fake addresss")
        return render_template("accountPage.html", accountinfo=accountinfo)

    # accountinfo = '{ "name":"First name", "email":"example@gmail.com", "phone":"1234567890", "Address": "123456"}'
    return render_template("accountPage.html", accountinfo=accountinfo)


@app.route("/accountPageEdit", methods=["GET"])
def accountPageEdit():
    if "userid" not in session:
        return render_template("logout.html")
    userid = session["userid"]
    cursor.execute(
        "SELECT [UserName], [UserEmail] FROM [test].[dbo].[user] WHERE [UserID] = %s",
        (userid),
    )
    account = cursor.fetchone()
    accountinfo = account + ("1234567890", "this is a fake addresss")

    return render_template("accountPageEdit.html", accountinfo=accountinfo)


@app.route("/accountPageEdit", methods=["POST"])
def updateAccount():
    if "userid" not in session:
        return render_template("logout.html")
    if (
        request.method == "POST"
        and "name" in request.form
        and "email" in request.form
        and "phone" in request.form
        and "address" in request.form
    ):
        print("pass")
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        cursor.execute(
            "UPDATE [test].[dbo].[user] SET [UserName] = %s, [UserEmail] = %s WHERE [UserID] = %s",
            (name, email, session["userid"]),
        )
        conn.commit()

        message = "update success"
        return redirect(url_for("accountPage"))
    return redirect(url_for("accountPageEdit"))


@app.route("/dashboard")
def dashboard():
    if "userid" not in session:
        return render_template("logout.html")
    userid = session["userid"]
    name = []
    cursor.execute(
        "SELECT [UserID], [UserName] FROM [test].[dbo].[user] WHERE [UserID] = %s",
        (userid),
    )
    account = cursor.fetchone()
    if account:
        print(account[1])
        name.append(account[1])

    cursor.execute(
        "SELECT [FileID] FROM [test].[dbo].[UserReport] WHERE [UserID]= %s", (userid)
    )
    account = cursor.fetchall()
    if account:
        name.append(len(account))
    else:
        name.append(0)

        # TODO count the report
        name.append(0)

        # TODO Find The most close report tahat schduled
        name.append(0)

    return render_template("dashboard.html", name=name)


@app.route("/myFiles", methods=["GET", "POST"])
def myFiles():
    if "userid" not in session:
        return render_template("start.html")
    userid = session["userid"]
    cursor.execute(
        "SELECT [FileID], [SendDate] FROM [test].[dbo].[UserReport] WHERE [UserID]= %s",
        (userid),
    )
    fileIds = [row for row in cursor.fetchall()]
    # Retrieve file information for all file IDs
    counter = 0
    box = ""
    htmlText = ""
    lenRow = len(fileIds)
    print(lenRow)
    for fileId in fileIds:
        cursor.execute(
            "SELECT * FROM [test].[dbo].[File] WHERE [FileID]= %s", (fileId[0])
        )
        row = cursor.fetchone()
        if row:
            if counter == 3:
                counter = 0
                lenRow -= 1
                htmlText += (
                    '<div class="row"> <div class="col-lg-12">' + box + "</div></div>"
                )
                box = ""
            else:
                counter += 1
                lenRow -= 1
                filepath = url_for("download", file=str(row[1]))
                box += (
                    '<div class="file-box">  <div class="file"> <a href="%s"> <span class="corner"></span> <div class="icon"> <i class="fa fa-file"></i> </div> <div class="file-name"> %s \
                                <br> <small>Added: %s</small>  </div> </a> </div> </div>'
                    % (filepath, str(row[1]), str(fileId[1].strftime("%m/%d/%Y")))
                )

    htmlText += '<div class="row"> <div class="col-lg-12">' + box + "</div></div>"

    # TODO if you want have sort add more here

    return render_template("myFiles.html", fileinfo=htmlText)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    if "userid" not in session:
        return render_template("start.html")
    # TODO let the page show the fie name. maybe it can done at html page

    if request.method == "POST" and "file" in request.files:
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        if filename != "":
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                return make_response("error")
            uploaded_file.save(os.path.join(app.config["UPLOAD_PATH"], filename))
            id = random.randint(2, 100000)
            id2 = random.randint(2, 100000)
            cursor.execute(
                "INSERT INTO [test].[dbo].[File] VALUES ( %s, %s, %s, 1);",
                (id, filename, os.path.join(app.config["UPLOAD_PATH"], filename)),
            )
            cursor.execute(
                "INSERT INTO [test].[dbo].[UserReport] VALUES ( %s, %s, %s, %s, %s);",
                (id2, datetime.now(), filename, session["userid"], id),
            )
            conn.commit()
            # print(os.path.join(app.config['UPLOAD_PATH'], filename))

            return redirect(url_for("myFiles"))

    return render_template("upload.html")


@app.route("/report")
def report():
    if "userid" not in session:
        return render_template("start.html")

    htmlText = ""

    # TODO Do the Same thing From the File page. But pull info form db with different path
    # path: User -> Recipients -> Schedular -> File
    # in Recipients only if active = 1

    return render_template("report.html")


@app.route("/scheduling", methods=["GET"])
def scheduling():
    if "userid" not in session:
        return render_template("start.html")
    # TODO html page not created yet

    # TODO send back these info to html so user can choose the option
    # User: all User belone to same Hostpital System
    # File: all file belone to you, may pull file name and file path(Check myFiles function)
    info = []

    #     #TODO html page not created yet

    #     #TODO take follwing info to schedule a file to send
    #     #User: User that want to send(more  then one)
    #     #File: File want to send (only one)
    #     #Hostpital System: (only one defult is 1 because our signup page do not have a place for Hostpital System)
    #     #Descrption: usually text form
    #     #schedule Frequence: 6 option #check the database dirgram
    #     #schedule period: 9 option #check the database dirgram
    #     #ScheduleId: plan to auto increase but now please give a random number

    #     #TODO add Reciptence
    #     #Descrption: usually text form
    #     #Activate: defult is 0 (not send yet)
    #     #scheduleID: id that create by pervious #TODO
    #     #ReciptenceID: plan to auto increase but now please give a random number

    return render_template("scheduling.html")


@app.route("/calendar", methods=["GET"])
def calendar():
    if "userid" not in session:
        return render_template("start.html")

    # TODO html page not created yet

    # TODO make calendar that retuen the scheduler info about user:
    # User -> Reciptence -> scheduler
    # only date if Reciptence's avtive value = 0
    # deturn the date for all schedule date

    info = []

    return render_template("calendar.html")


@app.route("/<path:file>", methods=["GET", "POST"])
def download(file):
    full_path = os.path.join(app.root_path, app.config["UPLOAD_PATH"])
    print(full_path)
    return send_from_directory(full_path, file)


@app.route("/why")
def why():
    # TODO in the html page add the info for why paratus
    return render_template("why.html")


@app.route("/compliance")
def compliance():
    # TODO in the html page add the info for why paratus
    return render_template("compliance.html")


@app.route("/aboutus")
def aboutus():
    # TODO in the html page add the info for about us
    return render_template("aboutus.html")


@app.route("/news")
def news():
    # TODO in the html page add the info for about us
    return render_template("news.html")


if __name__ == "__main__":
    app.run(debug=True)
