from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def start():
	return render_template("start.html")

@app.route("/signup")
def signup():
	return render_template("signup.html")

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
