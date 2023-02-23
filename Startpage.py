from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def start():
	return render_template("start.html")

@app.route("/signup")
def signup():
	return render_template("signup.html")

if __name__ == "__main__":
	app.run(debug=True)
