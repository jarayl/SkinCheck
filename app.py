from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, doctor_only, patient_only
import datetime

import model_1
from io import BytesIO
import base64
from keras.preprocessing import image
from PIL import Image
import numpy as np
from keras.models import load_model
import cv2

import sqlite3

app = Flask(__name__)
app.secret_key = "JustinJaraySahil"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#additional functionalities: verify email, settings, etc
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
        # Ensure doctor email was submitted
        if not request.form.get("email"):
            flash("Must submit email!")
            return render_template("doctor-login.html")
        # Ensure doctor password was submitted
        elif not request.form.get("password"):
            flash("Must submit password!")
            return render_template("doctor-login.html")
        
        # SQL logic to verify the doctor's credentials
        con = sqlite3.connect("skincheck.db")
        con.row_factory = sqlite3.Row  # Set row factory to fetch rows as dictionaries
        cur = con.cursor()
        cur.execute("SELECT * FROM doctors WHERE dEmail = ?", (request.form.get("email"),))
        row = cur.fetchone()

        if row is None or not check_password_hash(row["password"], request.form.get("password")):
            flash("Email or Password Incorrect")
            con.close()
            return render_template("doctor-login.html")

        session["user_id"] = row["dID"]
        con.close()
        return redirect("/doctor/home")
    else:
        return render_template("doctor-login.html")

@app.route("/patient/login", methods=["GET", "POST"])
@patient_only
def patient_login():
    if request.method == "POST":
        # Ensure patient email was submitted
        if not request.form.get("email"):
            flash("Must submit email!")
            return render_template("patient-login.html")
        # Ensure patient password was submitted
        elif not request.form.get("password"):
            flash("Must submit password!")
            return render_template("patient-login.html")
        
        # SQL logic to verify the patient's credentials
        con = sqlite3.connect("skincheck.db")
        con.row_factory = sqlite3.Row  # Set row factory to fetch rows as dictionaries
        cur = con.cursor()
        cur.execute("SELECT * FROM patients WHERE pEmail = ?", (request.form.get("email"),))
        row = cur.fetchone()

        if row is None or not check_password_hash(row["password"], request.form.get("password")):
            flash("Email or Password Incorrect")
            con.close()
            return render_template("patient-login.html")

        session["user_id"] = row["pID"]
        con.close()
        return redirect("/patient/home")
    else:
        return render_template("patient-login.html")

@app.route("/doctor/register", methods=["GET", "POST"])
@doctor_only
def doctor_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not all((name, email, password, confirmation)):
            flash("All fields are required!")
            return render_template("doctor-register.html")

        if password != confirmation:
            flash("Passwords must match!")
            return render_template("doctor-register.html")

        if len(password) < 8 or not any(c.isdigit() for c in password):
            flash("Password must be at least 8 characters long and contain a number!")
            return render_template("doctor-register.html")

        try:
            con = sqlite3.connect("skincheck.db")
            con.row_factory = sqlite3.Row  # Fetch rows as dictionaries
            cur = con.cursor()
            cur.execute("INSERT INTO doctors (password, name, dEmail) VALUES (?, ?, ?)", (generate_password_hash(password), name, email))
            con.commit()

            cur.execute("SELECT dID FROM doctors WHERE dEmail = ?", (email,))
            rows = cur.fetchall()

            if rows:
                session["user_id"] = rows[0]["dID"]
                return redirect("/doctor/home")
            else:
                flash("Registration failed. Please try again.")
                return render_template("doctor-register.html")

        except sqlite3.IntegrityError:
            flash("Email already exists!")
            return render_template("doctor-register.html")

        finally:
            con.close()
    else:
        return render_template("doctor-register.html")

@app.route("/patient/register", methods=["GET", "POST"])
@patient_only
def patient_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        sex = request.form.get('sex')
        dob = request.form.get('dob')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not all((name, email, sex, dob, password, confirmation)):
            flash('All fields are required!')
            return render_template('patient-register.html')

        try:
            # Validate Date of Birth format
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            flash('Invalid Date of Birth format! Please use YYYY-MM-DD.')
            return render_template('patient-register.html')

        if password != confirmation:
            flash('Passwords must match!')
            return render_template('patient-register.html')

        if len(password) < 8 or not any(map(str.isdigit, password)):
            flash('Password must be at least 8 characters long and contain a number!')
            return render_template('patient-register.html')

        try:
            con = sqlite3.connect('skincheck.db')
            con.row_factory = sqlite3.Row  # Fetch rows as dictionaries
            cur = con.cursor()
            hashed_password = generate_password_hash(password)
            cur.execute('INSERT INTO patients (password, name, pEmail, sex, dob) VALUES (?, ?, ?, ?, ?)',
                        (hashed_password, name, email, sex, dob))
            con.commit()

            cur.execute('SELECT pId FROM patients WHERE pEmail = ?', (email,))
            rows = cur.fetchall()

            if rows:
                session['user_id'] = rows[0]['pId']
                return redirect('/patient/home')
            else:
                flash('Registration failed. Please try again.')
                return render_template('patient-register.html')

        except sqlite3.IntegrityError:
            flash('Email already exists!')
            return render_template('patient-register.html')

        finally:
            con.close()
    else:
        return render_template('patient-register.html')

@app.route("/doctor/home", methods=["GET", "POST"]) #table of patients with uploaded images
@login_required
@doctor_only
def doctor_home():
    con = sqlite3.connect("skincheck.db")
    con.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    cur = con.cursor()
    
    # Get doctor's name
    cur.execute("SELECT name FROM doctors WHERE dId = ?", (session["user_id"],))
    doctor = cur.fetchone()
    doc_name = doctor["name"]

    # Get all patient info associated with the current doctor
    cur.execute("SELECT patients.pId, patients.pEmail, patients.name AS pat_name, patients.dob, patients.gender AS sex, patients.status FROM patients INNER JOIN docPatRel ON patients.pId = docPatRel.pId WHERE docPatRel.dId = ?", (session["user_id"],))
    patients = cur.fetchall()

    con.close()

    if request.method == "POST":
        p_id = request.form.get("pId")
        return redirect(url_for("patient-history", patient_id=p_id))
    else:
        return render_template("doctor-home.html", name=doc_name, patients=patients)

@app.route("/patient/home",  methods=["GET", "POST"]) #patient history
@login_required
@patient_only
def patient_home():
    return None

@app.route("/doctor/upload", methods=["GET", "POST"])
@login_required
@doctor_only
def img_upload():
    if request.method == 'POST':
        if 'imageFile' not in request.files:
            flash("Must upload an image!")
            return render_template("upload-img.html")

        f = request.files['imageFile']

        if f.filename == '':
            flash("No selected file")
            return render_template("upload-img.html")

        diagnosis_model = load_model("densenet169")
        grad_cam_model = load_model("resnet50v2")

        try:
            img = Image.open(BytesIO(f.read()))
        except Exception as e:
            flash("Unable to read the image file!")
            return render_template("upload-img.html")

        img_array = np.array(img)

        resized_img, overlay, network_prediction, network_confidence = model_1.make_inference(diagnosis_model, grad_cam_model, img_array)

        # Convert images to PIL format and then to byte streams
        pil_img1 = Image.fromarray(resized_img.astype('uint8'), 'RGB')
        pil_img2 = Image.fromarray(overlay.astype('uint8'), 'RGB')

        img1_buffer = BytesIO()
        img2_buffer = BytesIO()

        pil_img1.save(img1_buffer, format='PNG')
        pil_img2.save(img2_buffer, format='PNG')

        # Encode the images to base64 strings and store them in the session
        session['image_data1'] = base64.b64encode(img1_buffer.getvalue()).decode('utf-8')
        session['image_data2'] = base64.b64encode(img2_buffer.getvalue()).decode('utf-8')

        # Also store the prediction and confidence in the session
        session['network_prediction'] = network_prediction
        session['network_confidence'] = network_confidence

        return redirect(url_for('img_uploaded'))
    else:
        return render_template("upload-img.html")

@app.route("/doctor/uploaded", methods=["GET", "POST"])
@login_required
@doctor_only
def img_uploaded():
    # Retrieve image data from the session
    image_data1 = session.get('image_data1')
    image_data2 = session.get('image_data2')
    network_prediction = session.get('network_prediction')
    network_confidence = session.get('network_confidence')

    if request.method == "POST":
        doc_com = request.form.get('comments')
        pEmail = request.form.get('patientEmail')
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not all((doc_com, pEmail)):
            flash('All fields are required!')
            return render_template('uploaded-img.html', resized_original=image_data1, overlay=image_data2, prediction=network_prediction, confidence=network_confidence)

        con = sqlite3.connect("skincheck.db")
        cur = con.cursor()

        try:
            # Fetch patient ID using patient's email from the patients table
            cur.execute("SELECT pId FROM patients WHERE pEmail = ?", (pEmail,))
            patient_id = cur.fetchone()

            if patient_id:
                # Insert data into the data table
                cur.execute("INSERT INTO data (dId, pId, diagnosis, desc, date, img, overlay) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (session.get('user_id'), patient_id[0], network_prediction, doc_com, date, image_data1, image_data2))
                con.commit()

                # Update docPatRel table with dId and pId
                cur.execute("INSERT INTO docPatRel (dId, pId) VALUES (?, ?)", (session.get('user_id'), patient_id[0]))
                con.commit()

                con.close()
                flash("Data uploaded successfully!")

                # Clear session variables related to image data
                session.pop('image_data1', None)  
                session.pop('image_data2', None) 
                session.pop('network_prediction', None) 
                session.pop('network_confidence', None) 

                return redirect('/doctor/home')

            else:
                # Patient does not exist, flash message and render the upload form again
                flash("Patient does not exist.")
                con.close()
                return render_template('uploaded-img.html', resized_original=image_data1, overlay=image_data2, prediction=network_prediction, confidence=network_confidence)

        except sqlite3.Error as e:
            # Handle database errors
            flash("Error uploading data. Please try again.")
            con.rollback()
            session.pop('image_data1', None)  
            session.pop('image_data2', None) 
            session.pop('network_prediction', None) 
            session.pop('network_confidence', None) 
            return render_template('upload-img.html')

        finally:
            con.close()

    else:
        # Render the image display template
        return render_template('uploaded-img.html', resized_original=image_data1, overlay=image_data2, prediction=network_prediction, confidence=network_confidence)

@app.route("/doctor/drop_patient", methods=["GET", "POST"]) #place to upload the image for AI model
@login_required
@doctor_only
def drop_patient():
    con = sqlite3.connect("skincheck.db")
    con.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    cur = con.cursor()

    cur.execute("SELECT patients.pId, patients.name AS pat_name FROM patients INNER JOIN docPatRel ON patients.pId = docPatRel.pId WHERE docPatRel.dId = ?", (session["user_id"],))
    patients = cur.fetchall()

    if request.method == "POST":
        patient_id = request.form.get("patient")
        try:
            cur.execute("DELETE FROM docPatRel WHERE dId = ? AND pId = ?", (session["user_id"], patient_id))
            con.commit()
        except sqlite3.Error as e:
            flash("Error deleting entry:")
            return render_template("doctor-drop-patient.html", patients=patients)
        finally:
            con.close()

        return redirect("/doctor/home")
    else:
        return render_template("doctor-drop-patient.html", patients=patients)

@app.route("/doctor/add_patient", methods=["GET", "POST"]) #place to upload the image for AI model
@login_required
@doctor_only
def add_patient():
    
    return TODO

@app.route("/doctor/<patient_id>", methods=["GET", "POST"])
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






