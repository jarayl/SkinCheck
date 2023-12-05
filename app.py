from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, doctor_only, patient_only

import sqlite3

db = sqlite3.connect("skincheck.db")
cur = db.cursor()

app = Flask(__name__)
app.secret_key = "JustinJaraySahil"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#additional functionalities: verify email, password must have some level of security, settings, etc
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    session.clear()
    if request.method == "POST":
        print(request.form.get("userType"))
        if request.form.get("userType") == "Doctor":
            session["user_type"] = "Doctor"
            return redirect("/doctor/login")
        else:
            session["user_type"] = "Patient"
            return redirect("/patient/login")
    else:
        return render_template("index.html")

@app.route("/doctor/login", methods=["GET", "POST"])
@doctor_only
def doctor_login():
    if request.method == "POST":
        #TODO
        # Ensure patient email was submitted
        if not request.form.get("email"):
            return 
        # Ensure patient password was submitted
        elif not request.form.get("password"):
            return 
        #sql logic to make sure that user exists in db

        return redirect("/doctor/home")
    else:
        return render_template("doctor-login.html")

@app.route("/patient/login", methods=["GET", "POST"])
@patient_only
def patient_login():
    if request.method == "POST":
        #TODO
        # Ensure patient email was submitted
        if not request.form.get("email"):
            return 
        
        # Ensure patient password was submitted
        elif not request.form.get("password"):
            return 
        
        #sql logic to make sure patient exists in db
        return redirect("/patient/home")
    else:
        return render_template("patient-login.html")

@app.route("/doctor/register", methods=["GET", "POST"])
@doctor_only
def doctor_register():
    if request.method == "POST":
        #TODO
        return None
    else:
        return render_template("doctor-register.html")

@app.route("/patient/register", methods=["GET", "POST"])
@patient_only
def patient_register():
    if request.method == "POST":
        #TODO
        return None
    else:
        return render_template("patient-register.html")

@app.route("/doctor/home", methods=["GET", "POST"]) #table of patients with uploaded images
@login_required
@doctor_only
def doctor_home():
    if request.method == "POST":
        #form should have value of patient id
        pId = request.form.get("pId")
        return redirect(url_for("patient_history", patient_id = pId))
    else:
        return render_template("doctor_home.html")

@app.route("/patient/home",  methods=["GET", "POST"]) #patient history
@login_required
@patient_only
def patient_home():
    return TODO

@app.route("/doctor/upload", methods=["GET", "POST"]) #place to upload the image for AI model
@login_required
@doctor_only
def img_upload():
    return TODO

@app.route("/doctor/<patient_id>", methods=["GET", "POST"]) #implement downloading image
@login_required
@doctor_only
def patient_hist(patient_id):
    #some sql stuff that gets the patient history with doctor id and patient id
    return render_template("patient_history.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout Successful!")
    return redirect("/")






