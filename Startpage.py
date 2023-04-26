from flask import Flask, redirect, url_for, render_template, request, session, make_response, send_from_directory, jsonify
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
app.config['UPLOAD_EXTENSIONS'] = [".pdf", ".doc", ".png", ".jpg", ".docx"]
app.config['UPLOAD_PATH'] = 'File'



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
            cursor.execute('INSERT INTO [test].[dbo].[user] VALUES ( %s, %s, %s, %s, 1, 2);', (id, name, email, birth))
            conn.commit()
            session["userid"] = id
            cursor.execute(
                "SELECT [RoleName] FROM [test].[dbo].[Role] WHERE [RoleID] = %s",
                (2,),
            )
            rolename = cursor.fetchone()
            session["rolename"] = rolename[0]
            seession["username"] = name
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
            "SELECT [UserID], [RoleID], [UserName] [UserEmail],[UserPassword] FROM [test].[dbo].[user] WHERE [UserEmail] = %s AND [UserPassword] = %s",
            (AccountNumber, birth),
        )
        account = cursor.fetchone()
        if account:
            msg = "login success"
            session.permanent = True
            print("success")
            # record userid in session for search propose
            session["userid"] = account[0]
            session["username"] = account[2]
            cursor.execute(
                "SELECT [RoleName] FROM [test].[dbo].[Role] WHERE [RoleID] = %s",
                (account[1],),
            )
            rolename = cursor.fetchone()
            session["rolename"] = rolename[0]
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
    # 
    # the db do not have phone and address update db
    userid = session["userid"]
    cursor.execute(
            "SELECT [UserName], [UserEmail] FROM [test].[dbo].[user] WHERE [UserID] = %s",(userid)
    )
    account = cursor.fetchone()
    if account:
        # 
        # the db do not have phone and address update db
        accountinfo = account + ("1234567890","this is a fake addresss", session["rolename"])
        return render_template("accountPage.html", username = session["username"], userrole = session["rolename"], accountinfo = accountinfo)

    
    #accountinfo = '{ "name":"First name", "email":"example@gmail.com", "phone":"1234567890", "Address": "123456"}'
    return render_template("accountPage.html", username = session["username"], userrole = session["rolename"], accountinfo = accountinfo)


@app.route("/accountPageEdit", methods = ['GET'])
def accountPageEdit():
    userid = session["userid"]
    cursor.execute(
            "SELECT [UserName], [UserEmail] FROM [test].[dbo].[user] WHERE [UserID] = %s",(userid)
    )
    account = cursor.fetchone()
    accountinfo = account + ("1234567890" , "this is a fake addresss", session["rolename"])
    
    


    return render_template("accountPageEdit.html", userrole = session["rolename"], accountinfo = accountinfo)

@app.route("/accountPageEdit", methods = ['POST'])
def updateAccount():
    if "userid" not in session:
        return render_template("logout.html")
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'phone' in request.form and 'address' in request.form:
        print("pass")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        cursor.execute("UPDATE [test].[dbo].[user] SET [UserName] = %s, [UserEmail] = %s WHERE [UserID] = %s", (name, email, session["userid"]))
        session["username"] = name
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
            "SELECT [UserID], [UserName] FROM [test].[dbo].[user] WHERE [UserID] = %s",(userid)
    )
    account = cursor.fetchone()
    if account:    
        print(account[1])
        name.append(account[1])
    
    cursor.execute("SELECT [FileID] FROM [test].[dbo].[UserReport] WHERE [UserID]= %s", (userid))
    account = cursor.fetchall()
    if account:
        name.append(len(account))
    else:
        name.append(0)

    cursor.execute("SELECT [ScheduleID] FROM [test].[dbo].[Recipients] WHERE [UserID]= %s AND [Active] = 1", (userid))
    report = cursor.fetchall()
    if report:
        name.append(len(report))
    else:
        name.append(0)
    
    #TODO Find The most close report tahat schduled
        name.append("none")

    #TODO Next Appointment
        name.append("none")

    return render_template("dashboard.html", name = name)



@app.route("/myFiles", methods=["GET", "POST"])
def myFiles():
    if "userid" not in session:
        return render_template("start.html")
    userid = session["userid"]
    cursor.execute("SELECT [FileID], [SendDate] FROM [test].[dbo].[UserReport] WHERE [UserID]= %s", (userid))
    fileIds = [row for row in cursor.fetchall()]
    # Retrieve file information for all file IDs
    counter = 0
    box = ''
    htmlText = ''
    lenRow = len(fileIds)
    print(lenRow)
    for fileId in fileIds:
        cursor.execute("SELECT * FROM [test].[dbo].[File] WHERE [FileID]= %s", (fileId[0]))
        row = cursor.fetchone()
        if row:
            if counter == 3:
                counter = 0
                lenRow -= 1
                htmlText += '<div class="row"> <div class="col-lg-12">' + box + '</div></div>'
                box = ''
            else:
                counter += 1
                lenRow -= 1
                filepath = url_for("download" , file =str(row[1]))
                box += '<div class="file-box">  <div class="file"> <a href="%s"> <span class="corner"></span> <div class="icon"> <i class="fa fa-file"></i> </div> <div class="file-name"> %s \
                                <br> <small>Added: %s</small>  </div> </a> </div> </div>' % (filepath, str(row[1]), str(fileId[1].strftime('%m/%d/%Y')))
        
    htmlText += '<div class="row"> <div class="col-lg-12">' + box + '</div></div>'

    # if you want have sort add more here
    # TODO  have sort add more here
    #If not REMOVE FROM THE HTML PAGE
    return render_template("myFiles.html", username = session["username"], fileinfo = htmlText)

@app.route("/upload", methods=["POST", "GET"])
def upload():
    if "userid" not in session:
        return render_template("start.html")
    isExist = os.path.exists("File")
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs("File")



    if request.method == 'POST' and 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return make_response("error")
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            id = random.randint(2, 100000)
            id2 = random.randint(2, 100000)
            cursor.execute('INSERT INTO [test].[dbo].[File] VALUES ( %s, %s, %s, 1);', (id, filename, os.path.join(app.config['UPLOAD_PATH'], filename)))
            cursor.execute('INSERT INTO [test].[dbo].[UserReport] VALUES ( %s, %s, %s, %s, %s);', (id2, datetime.now(), filename, session["userid"], id))
            conn.commit()
            #print(os.path.join(app.config['UPLOAD_PATH'], filename))

            return redirect(url_for("myFiles"))



    return render_template("upload.html")
    




@app.route('/report')
def report():
    if "userid" not in session:
        return render_template("start.html")
    htmlText = ''
    user_id = session["userid"]
    
    query = """
        SELECT f.FileName, f.FilePath, st.ScheduleTaskDesc
        FROM [test].[dbo].[User] u
        JOIN [test].[dbo].[Recipients] r ON u.UserID = r.UserID
        JOIN [test].[dbo].[Scheduler] s ON r.ScheduleID = s.ScheduleID
        JOIN [test].[dbo].[ScheduleTask] st ON s.ScheduleTaskID = st.ScheduleTaskID
        JOIN [test].[dbo].[File] f ON s.FileID = f.FileID
        WHERE r.Active = 1 AND u.UserID = %s
    """
    cursor.execute(query, (user_id))
    result = cursor.fetchall()
    files = []
    counter = 0
    box = ''
    htmlText = ''
    lenRow = len(result)
    for row in result:
        if counter == 3:
            counter = 0
            lenRow -= 1
            htmlText += '<div class="row"> <div class="col-lg-12">' + box + '</div></div>'
            box = ''
        else:
            counter += 1
            lenRow -= 1
            filepath = url_for("download" , file =str(row[1]))
            box += '<div class="file-box">  <div class="file"> <a href="%s"> <span class="corner"></span> <div class="icon"> <i class="fa fa-file"></i> </div> <div class="file-name"> %s \
                        <br> <small>Desc: %s</small>  </div> </a> </div> </div>' % (filepath, str(row[0]), str(row[2]))
        
    htmlText += '<div class="row"> <div class="col-lg-12">' + box + '</div></div>'


    #TODO in the html page make one similar to myfile.html but for the report 
    return render_template("report.html", username = session["username"] ,fileinfo = htmlText)


@app.route('/email', methods=["GET"])
def email():
    
    if "userid" not in session:
        return render_template("start.html")
    
    userid = session["userid"]
    query = f"SELECT RoleID, HospitalSystemRegionID FROM [test].[dbo].[User] WHERE UserID = {userid}"
    cursor.execute(query)
    roleid, hospitalid = cursor.fetchone()
    
    # Task 1: Find all UserIDs in User table with same HospitalSystemRegionID as #1
    if session["rolename"] == "admin":
        query = f"SELECT UserID FROM [test].[dbo].[User] WHERE HospitalSystemRegionID = {hospitalid}"
    else:
        query = f"SELECT UserID FROM [test].[dbo].[User] WHERE HospitalSystemRegionID = {hospitalid} AND RoleID <> 0"
    cursor.execute(query)
    userids = [row[0] for row in cursor]

    # Task 2: Get UserName and UserEmail for all UserIDs in #2
    query = f"SELECT UserName, UserEmail FROM [test].[dbo].[User] WHERE UserID IN ({','.join(str(uid) for uid in userids)})"
    cursor.execute(query)
    user_data = cursor.fetchall()

    info = []
    info.append(session["username"])
    user = []
    for row in user_data:
        file = {
            'UserName': row[0],
            'UserEmail': row[1],
        }
        user.append(file)
    info.append(user)

    #file name
    user_files = []
    cursor.execute("SELECT [FileID], [SendDate] FROM [test].[dbo].[UserReport] WHERE [UserID]= %s", (userid))
    fileIds = [row for row in cursor.fetchall()]
    # Retrieve file information for all file IDs
    for fileId in fileIds:
        cursor.execute("SELECT * FROM [test].[dbo].[File] WHERE [FileID]= %s", (fileId[0]))
        row = cursor.fetchone()
        if row:
            user_files.append(row[1])
        
    info.append(user_files)


    #TODO html page not created yet 
    #return this
    #[user] = [{'UserName' ,'UserEmail'}, ....]
    #[userfile] = [filename, ......]
    #[[user][userfile]]
    #use this info to make the scheduling page
    return render_template("scheduling.html", username = session["username"], info = info)

@app.route('/email', methods=["POST"])
def scheduling():
    if "userid" not in session:
        return render_template("start.html")

    #TODO html page not created yet

    #take follwing info to schedule a file to send
    #User: User that want to send(more  then one)
    #File: File want to send (only one) 
    #Hostpital System: (only one defult is 1 because our signup page do not have a place for Hostpital System)
    #Descrption: usually text form
    #schedule Frequence: 6 option #check the database dirgram
    #schedule period: 9 option #check the database dirgram
    #ScheduleId: plan to auto increase but now please give a random number 

#=========This need get from the html GET=================
    #TODO get these info form the front-end page
    user = []
    file = "filename"
    Hostpital_System = 1 
    Descrption = "this is Descrption of this schedule"
    schedule_Frequence = 1
    Schedule_Period = 1
    ScheduleId = random.randint(2, 100000)
    ScheduleTaskId = random.randint(2, 100000)

#=========================================================
    cursor.execute('INSERT INTO [test].[dbo].[ScheduleTask] VALUES ( %s, %s, %s);', (ScheduleTaskId, Descrption, 0))
    conn.commit()
    cursor.execute("SELECT [FileID] FROM [test].[dbo].[File] WHERE [FileName]= %s", (file))
    row = cursor.fetchone()
    cursor.execute('INSERT INTO [test].[dbo].[SchedulePeriod] VALUES ( %s, %s, %s, %s, %s, %s);', (ScheduleId, ScheduleTaskId, Hostpital_System, schedule_Frequence, Schedule_Period, row[0]))
    conn.commit()

    for R_user in user:
        ReciptenceId = random.randint(2, 100000)
        cursor.execute('INSERT INTO [test].[dbo].[Recipients] VALUES ( %s, %s, %s, %s);', (ReciptenceId, ScheduleId, R_user,0))
#====================================================================


    #TODO maybe add a pop up message show upload success
    return redirect(url_for("dashboard"))


@app.route('/calendar', methods=["GET"])
def calendar():
    if "userid" not in session:
        return render_template("start.html")
    

    #TODO make calendar that retuen the scheduler info about user:
    #User -> Reciptence -> scheduler 
    #only date if Reciptence's avtive value = 0
    #deturn the date for all schedule date


    info = []
    info.append( session["username"])
    return render_template("calendar.html", info = info)



@app.route('/<path:file>', methods=['GET', 'POST'])
def download(file):
    full_path = os.path.join(app.root_path, app.config['UPLOAD_PATH'])
    print(full_path)
    return send_from_directory(full_path, file)

@app.route("/why")
def why():
    return render_template("why.html")

@app.route("/compliance")
def compliance():
    return render_template("compliance.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/news")
def news():
    return render_template("news.html")



if __name__ == "__main__":
    app.run(debug=True)