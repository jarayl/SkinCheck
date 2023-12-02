from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3

app = Flask(__name__)

#additional functionalities: verify email, password must have some level of security, settings, etc
Session(app)

@app.route("/")
def index():
    session.clear()
    if request.method == "POST":
        if request.get.form("type") == "Doctor":
            session["user_type"] = "Doctor"
            return redirect("/doctor/login")
        else:
            session["user_type"] = "Patient"
            return redirect("/patient/login")
    else:
        return render_template("index.html")

@app.route("/doctor/login")
@doctor_only
def doctor_login():
    if request.method == "POST":
        #TODO
    else:
        return render_template("doctor_login.html")

@app.route("/patient/login")
@patient_only
def patient_login():
    if request.method == "POST":
        #TODO
    else:
        return render_template("patient_login.html")

@app.route("/doctor/register")
@doctor_only
def doctor_register():
    if request.method == "POST":
        #TODO
    else:
        return render_template("doctor_register.html")

@app.route("/patient/register")
@patient_only
def patient_register():
    if request.method == "POST":
        #TODO
    else:
        return render_template("patient_register.html")

@app.route("/doctor/home") #table of patients with uploaded images
@login_required
@doctor_only
def doctor_home():


@app.route("/patient/home") #patient history
@patient_only
def patient_home():


@app.route("/doctor/upload") #place to upload the image for AI model
@login_required
@doctor_only
def img_upload():
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")






