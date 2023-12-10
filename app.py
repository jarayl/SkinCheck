#Import necessary app modules
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

#Import helper modules or files
from helpers import login_required, doctor_only, patient_only
import datetime

#Import necessary modules used in machine learning and image processing 
import model_1
from io import BytesIO
import base64
from keras.preprocessing import image
from PIL import Image
import numpy as np
from keras.models import load_model

#Import database management module
import sqlite3

"""
Parts of website design takes inspiration from CS50: Finance:

https://cs50.harvard.edu/college/2023/fall/psets/9/finance/ 

Parts of the front-end website were developed with the help of ChatGPT:

chat.openai.com

Datasets downloaded from Kaggle:

https://www.kaggle.com/datasets/fanconic/skin-cancer-malignant-vs-benign/data
https://www.kaggle.com/datasets/wanderdust/skin-lesion-analysis-toward-melanoma-detection/data

Imported base models from built in tensorflow libraries (added our own layers):

https://www.tensorflow.org/api_docs/python/tf/keras/applications
"""

#Initialize flask app
app = Flask(__name__)

#App configuration
app.secret_key = "JustinJaraySahil"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#Initialize session
Session(app)

#Make truncating helper function
def truncate(s, length, end='...'):
    #truncate string to given length
    if len(s) > length:
        return s[:length] + end
    return s

# Register truncating filter
app.template_filter('truncate')(truncate)

@app.route("/", methods=["GET", "POST"])
def index():
    """Homepage of App"""

    #Clear session
    session.clear()
    if request.method == "POST":
        #Save the user type (doctor or patient) into session variable
        if request.form.get("userType") == "Doctor":
            session["user_type"] = "Doctor"
            #Redirect to corresponding login page 
            return redirect("/doctor/login")
        else:
            session["user_type"] = "Patient"
            #Redirect to corresponding login page 
            return redirect("/patient/login")
    else:
        return render_template("index.html")


@app.route("/doctor/login", methods=["GET", "POST"])
@doctor_only
def doctor_login():
    """Doctor Login Portal"""

    if request.method == "POST":

        #Ensure doctor email was submitted
        if not request.form.get("email"):
            flash("Must submit email!")
            return render_template("doctor-login.html")
        
        #Ensure doctor password was submitted
        elif not request.form.get("password"):
            flash("Must submit password!")
            return render_template("doctor-login.html")
        
        #Check if the doctor exists in database
        con = sqlite3.connect("skincheck.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM doctors WHERE dEmail = ?", (request.form.get("email"),))
        row = cur.fetchone()

        #If the doctor does not exist, flash error and re-render tempalte
        if row is None or not check_password_hash(row["password"], request.form.get("password")):
            flash("Email or Password Incorrect")
            con.close()
            return render_template("doctor-login.html")

        #Store doctor id in session variable
        session["user_id"] = row["dID"]
        con.close()

        #Redirect user to doctor home page
        return redirect("/doctor/home")
    
    #If user reached route through GET request
    else:
        return render_template("doctor-login.html")

@app.route("/patient/login", methods=["GET", "POST"])
@patient_only
def patient_login():
    """Patient Login Portal"""

    if request.method == "POST":

        #Ensure patient email was submitted
        if not request.form.get("email"):
            flash("Must submit email!")
            return render_template("patient-login.html")
        
        #Ensure patient password was submitted
        elif not request.form.get("password"):
            flash("Must submit password!")
            return render_template("patient-login.html")
        
        #Check if the doctor exists in database
        con = sqlite3.connect("skincheck.db")
        con.row_factory = sqlite3.Row 
        cur = con.cursor()
        cur.execute("SELECT * FROM patients WHERE pEmail = ?", (request.form.get("email"),))
        row = cur.fetchone()

        #If patient does not exist, flash error and re-render tempalte
        if row is None or not check_password_hash(row["password"], request.form.get("password")):
            flash("Email or Password Incorrect")
            con.close()
            return render_template("patient-login.html")

        #Store patient id in session variable 
        session["user_id"] = row["pID"]
        con.close()

        #Redirect to patient home page
        return redirect("/patient/home")
    
    #If user reached route through GET request
    else:
        return render_template("patient-login.html")

@app.route("/doctor/register", methods=["GET", "POST"])
@doctor_only
def doctor_register():
    """Doctor Register Page"""

    if request.method == "POST":

        #Get form submissions and store in variables
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #Ensure all required fields were submitted by user
        if not all((name, email, password, confirmation)):
            flash("All fields are required!")
            return render_template("doctor-register.html")

        #Ensure confirmed password matches password
        if password != confirmation:
            flash("Passwords must match!")
            return render_template("doctor-register.html")

        #Ensure some level of complexity in password
        if len(password) < 8 or not any(c.isdigit() for c in password):
            flash("Password must be at least 8 characters long and contain a number!")
            return render_template("doctor-register.html")

        #Try to insert new doctor in database
        try:
            #Insert the new doctor into database
            con = sqlite3.connect("skincheck.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("INSERT INTO doctors (password, name, dEmail) VALUES (?, ?, ?)", (generate_password_hash(password), name, email))
            con.commit()

            #Check if the doctor exists in database
            cur.execute("SELECT dID FROM doctors WHERE dEmail = ?", (email,))
            rows = cur.fetchall()

            #If doctor does exist in database, redirect to doctor homepage
            if rows:
                session["user_id"] = rows[0]["dID"]
                return redirect("/doctor/home")
            
            #If doctor does not exist in database, flash error and re-render template
            else:
                flash("Registration failed. Please try again.")
                return render_template("doctor-register.html")
            
        #If the email is already in use, throw error and re-render template
        except sqlite3.IntegrityError:
            flash("Email already exists!")
            return render_template("doctor-register.html")

        #Close database connection
        finally:
            con.close()
    
    #If user reached route through GET request
    else:
        return render_template("doctor-register.html")

@app.route("/patient/register", methods=["GET", "POST"])
@patient_only
def patient_register():
    """Patient Register Page"""

    if request.method == 'POST':

        #Get form submissions and store in variables
        name = request.form.get('name')
        email = request.form.get('email')
        sex = request.form.get('sex')
        dob = request.form.get('dob')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        #Ensure all required fields were submitted by user
        if not all((name, email, sex, dob, password, confirmation)):
            flash('All fields are required!')
            return render_template('patient-register.html')
        
        # Validate Date of Birth format
        try:
            dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            flash('Invalid Date of Birth format! Please use YYYY-MM-DD.')
            return render_template('patient-register.html')

        #Ensure confirmed password matches password
        if password != confirmation:
            flash('Passwords must match!')
            return render_template('patient-register.html')

        #Ensure some level of complexity in password
        if len(password) < 8 or not any(map(str.isdigit, password)):
            flash('Password must be at least 8 characters long and contain a number!')
            return render_template('patient-register.html')

        #Try to insert new patient in database
        try:
            #Insert the new patient into database
            con = sqlite3.connect('skincheck.db')
            con.row_factory = sqlite3.Row  # Fetch rows as dictionaries
            cur = con.cursor()
            hashed_password = generate_password_hash(password)
            cur.execute('INSERT INTO patients (password, name, pEmail, sex, dob) VALUES (?, ?, ?, ?, ?)', (hashed_password, name, email, sex, dob))
            con.commit()

            #Check if the patient exists in database
            cur.execute('SELECT pId FROM patients WHERE pEmail = ?', (email,))
            rows = cur.fetchall()

            #If patient does exist in database, redirect to patient homepage
            if rows:
                session['user_id'] = rows[0]['pId']
                return redirect('/patient/home')
            
            #If patient does not exist in database, flash error and re-render template
            else:
                flash('Registration failed. Please try again.')
                return render_template('patient-register.html')

        #If the email is already in use, throw error and re-render template
        except sqlite3.IntegrityError:
            flash('Email already exists!')
            return render_template('patient-register.html')

        #Close database connection
        finally:
            con.close()
    
    #If user reached route through GET request
    else:
        return render_template('patient-register.html')

@app.route('/about-us')
def about_us():
    """About Us Page"""

    #render the about us template
    return render_template('about-us.html')

@app.route("/doctor/home")
@login_required
@doctor_only
def doctor_home():
    """Doctor Home Page"""

    #Connect to database
    con = sqlite3.connect("skincheck.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    #Get doctor's name
    cur.execute("SELECT name FROM doctors WHERE dId = ?", (session["user_id"],))
    doctor = cur.fetchone()
    doc_name = doctor["name"]

    #Get all patient info associated with the doctor currently logged in
    cur.execute("SELECT patients.pId, patients.pEmail, patients.name AS pat_name, patients.dob, patients.sex AS sex, patients.status FROM patients INNER JOIN docPatRel ON patients.pId = docPatRel.pId WHERE docPatRel.dId = ?", (session["user_id"],))
    patients = cur.fetchall()

    con.close()
    
    #Pass in patient info associated with doctor to template
    return render_template("doctor-home.html", name=doc_name, patients=patients)

@app.route("/patient/home")
@login_required
@patient_only
def patient_home():
    """Patient Home Page"""

    #Connect to database
    con = sqlite3.connect("skincheck.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Get patients's name
    cur.execute("SELECT name FROM patients WHERE pId = ?", (session["user_id"],))
    patient = cur.fetchone()
    pat_name = patient["name"]

    # Get all data associated with the current patient
    cur.execute("SELECT doctors.name AS doctor_name, doctors.dId AS dId, patients.pId AS patient_id, data.diagnosis, data.desc, data.date, data.id AS id FROM doctors JOIN docPatRel ON doctors.dId = docPatRel.dId JOIN patients ON docPatRel.pId = patients.pId JOIN data ON patients.pId = data.pId WHERE patients.pId = ?", (session["user_id"],))
    data = cur.fetchall()
    con.close()

    #Pass patient data to template
    return render_template("patient-home.html", name=pat_name, data = data)

@app.route("/doctor/upload", methods=["GET", "POST"])
@login_required
@doctor_only
def img_upload():
    """Image Upload Page"""

    if request.method == 'POST':

        #Ensure image is passed in
        if 'imageFile' not in request.files:
            flash("Must upload an image!")
            return render_template("upload-img.html")

        #Get file that was passed in
        f = request.files['imageFile']

        #Ensure filename is not empty
        if f.filename == '':
            flash("No selected file")
            return render_template("upload-img.html")

        #Load the ML models 
        diagnosis_model = load_model("densenet169")
        grad_cam_model = load_model("resnet50v2")

        #Read file that was passed in, flash error if unable to read
        try:
            img = Image.open(BytesIO(f.read()))
        except Exception as e:
            flash("Unable to read the image file!")
            return render_template("upload-img.html")

        #Convert image to numpy array to pass into make_inference function
        img_array = np.array(img)

        #Call make_inference
        resized_img, overlay, network_prediction, network_confidence = model_1.make_inference(diagnosis_model, grad_cam_model, img_array)

        #Convert output arrays to PIL object and then to byte streams
        pil_img1 = Image.fromarray(resized_img.astype('uint8'), 'RGB')
        pil_img2 = Image.fromarray(overlay.astype('uint8'), 'RGB')

        img1_buffer = BytesIO()
        img2_buffer = BytesIO()

        #Save PIL objects to buffers
        pil_img1.save(img1_buffer, format='PNG')
        pil_img2.save(img2_buffer, format='PNG')

        #Encode images to base64 strings and store them in the session (needed in order to display in HTML)
        session['image_data1'] = base64.b64encode(img1_buffer.getvalue()).decode('utf-8')
        session['image_data2'] = base64.b64encode(img2_buffer.getvalue()).decode('utf-8')

        #Store prediction and confidence % in the session
        session['network_prediction'] = network_prediction
        session['network_confidence'] = network_confidence

        #Redirect to img_uploaded route
        return redirect(url_for('img_uploaded'))
    
    #If user reached route through GET request
    else:
        return render_template("upload-img.html")

@app.route("/doctor/uploaded", methods=["GET", "POST"])
@login_required
@doctor_only
def img_uploaded():
    """Uploaded Image Page"""

    # Retrieve image data from the session
    image_data1 = session.get('image_data1')
    image_data2 = session.get('image_data2')
    network_prediction = session.get('network_prediction')
    network_confidence = session.get('network_confidence')

    if request.method == "POST":

        #Get the submitted input and store in variables
        doc_com = request.form.get('comments')
        pEmail = request.form.get('patientEmail')

        #Get curent time using datetime module
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #Ensure all session variables stored in img_upload are not None
        if not all((image_data1, image_data2, network_prediction, network_confidence)):
            flash('Error loading in model data!')
            return redirect("/doctor/upload")

        #Ensure all fields are submitted
        if not all((doc_com, pEmail)):
            flash('All fields are required!')
            return render_template('uploaded-img.html', resized_original=image_data1, overlay=image_data2, prediction=network_prediction, confidence=network_confidence)

        #Connect to database
        con = sqlite3.connect("skincheck.db")
        cur = con.cursor()

        #Try inserting new entry into data table
        try:

            #Fetch patient ID using patient email
            cur.execute("SELECT pId FROM patients WHERE pEmail = ?", (pEmail,))
            patient_id = cur.fetchone()

            #If patient exists
            if patient_id:

                # Insert data into the data table
                cur.execute("INSERT INTO data (dId, pId, diagnosis, desc, date, img, overlay) VALUES (?, ?, ?, ?, ?, ?, ?)", (session.get('user_id'), patient_id[0], network_prediction, doc_com, date, image_data1, image_data2))
                con.commit()

                #Check if patient and doctor have existing relationship in docPatRel
                cur.execute("SELECT * FROM docPatRel WHERE dId = ? AND pId = ?", (session.get('user_id'), patient_id[0]))
                exists = cur.fetchone()

                #If no pre-existing relationship, insert
                if not exists:
                    cur.execute("INSERT INTO docPatRel (dId, pId) VALUES (?, ?)", (session.get('user_id'), patient_id[0]))
                    con.commit()

                #Update status of patient in the patients table
                cur.execute("UPDATE patients SET status = ? WHERE pId = ?", (network_prediction, patient_id[0]))
                con.commit()

                #Close connection
                con.close()

                #Flash success message
                flash("Data uploaded successfully!")

                #Redirect to doctor homepage
                return redirect('/doctor/home')

            #If patient does not exist
            else:
                flash("Patient does not exist.")
                con.close()
                return render_template('uploaded-img.html', resized_original=image_data1, overlay=image_data2, prediction=network_prediction, confidence=network_confidence)

        #In case of error inserting into database
        except sqlite3.Error as e:

            flash("Error uploading data. Please try again.")
            con.rollback()

            #Clear session variables set in upload
            session.pop('image_data1', None)  
            session.pop('image_data2', None) 
            session.pop('network_prediction', None) 
            session.pop('network_confidence', None) 

            #Redirect to upload screen again
            return redirect("/doctor/upload")

        #Close database connection
        finally:
            con.close()

    #If user reaches route through GET request
    else:
        #Pass in relevant session variables
        return render_template('uploaded-img.html', resized_original=image_data1, overlay=image_data2, prediction=network_prediction, confidence=network_confidence)

@app.route("/doctor/drop_patient", methods=["GET", "POST"])
@login_required
@doctor_only
def drop_patient():
    """Drop Patient Page"""

    #Connect to database
    con = sqlite3.connect("skincheck.db")
    con.row_factory = sqlite3.Row 
    cur = con.cursor()

    #Get names of all patients associated with doctor
    cur.execute("SELECT patients.pId, patients.name AS pat_name FROM patients INNER JOIN docPatRel ON patients.pId = docPatRel.pId WHERE docPatRel.dId = ?", (session["user_id"],))
    patients = cur.fetchall()

    if request.method == "POST":

        #Get patient id submitted
        patient_id = request.form.get("patient")

        #Try to delete patient from docPatRel table
        try:
            #Delete patient doctor relationship
            cur.execute("DELETE FROM docPatRel WHERE dId = ? AND pId = ?", (session["user_id"], patient_id))
            con.commit()
        
        #If there is an error dropping patient
        except sqlite3.Error as e:
            flash("Error dropping patient!")
            return render_template("doctor-drop-patient.html", patients=patients)
        
        #Close database connection
        finally:
            con.close()

        #Redirect to doctor home page
        return redirect("/doctor/home")
    
    #If user reaches route through GET request
    else:
        #Pass in patient names to template
        return render_template("doctor-drop-patient.html", patients=patients)

@app.route("/doctor/add_patient", methods=["GET", "POST"])
@login_required
@doctor_only
def add_patient():
    """Add Patient Page"""

    #
    con = sqlite3.connect("skincheck.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if request.method == "POST":
        
        #Get patient email from HTML form
        pEmail = request.form.get("pEmail")

        #Ensure patient email was submitted
        if not pEmail:
            flash ("Must provide patient email!")
            return render_template("doctor-add-patient.html")

        #Query database for patient with patient email
        cur.execute("SELECT pId FROM patients WHERE pEmail = ?", (pEmail,))
        patient = cur.fetchone()

        #If patient does not exist in database
        if not patient:
            flash("Patient does not exist in database!")
            return render_template("doctor-add-patient.html")
        
        #Get patient id from query
        pId = patient["pId"]

        #Query database for existing patient-doctor relationship
        cur.execute("SELECT * FROM docPatRel WHERE dId = ? AND pId = ?", (session["user_id"], pId))
        rels = cur.fetchall()

        #If patient is not already a patient of the doctor
        if not rels:

            #Try to insert new relationship into table
            try:

                #Insert new relationship into docPatRel table
                cur.execute("INSERT INTO docPatRel (dId, pId) VALUES (?,?)", (session["user_id"], pId))
                con.commit()

            #If error inserting relationship
            except sqlite3.Error as e:
                flash("Error adding patient")
                return render_template("doctor-add-patient.html")

            #Close connection to database
            finally:
                con.close()
        
        #If patient is already a patient of the doctor
        else:
            flash("Already a Patient")
            con.close()
            return render_template("doctor-add-patient.html")
        
        #Redirect to doctor home page
        return redirect("/doctor/home")

    #If user reached route through GET request
    else:
        return render_template("doctor-add-patient.html")

@app.route("/doctor/<patient_id>")
@login_required
@doctor_only
def patient_history(patient_id):
    """Patient History"""

    #Try to fetch all data for patient with passed in patient_id
    try:
        con = sqlite3.connect("skincheck.db")
        con.row_factory = sqlite3.Row  # Fetch rows as dictionaries
        cur = con.cursor()

        #Fetch patient history
        cur.execute("SELECT id, diagnosis, date, desc, img, overlay FROM data WHERE dId = ? AND pId = ?", (session["user_id"], patient_id))

        #Store data into pat_hist variable
        pat_hist = cur.fetchall()

    #Handle SQL errors
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}")

        #Redirect to doctor home page
        return redirect(url_for("/doctor/home"))
    
    #Close database connection
    finally:
        con.close()

    #Pass pat_hist to the template
    return render_template("doctor-patient-history.html", pat_hist=pat_hist)

@app.route("/patient/<id>")
@login_required
@patient_only
def diagnosis(id):
    """Diagnosis Page"""

    #Try fetching patient history for specific data id
    try:
        con = sqlite3.connect("skincheck.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        #Fetch patient history
        cur.execute("SELECT diagnosis, date, desc, img, overlay FROM data WHERE id = ?", (id,))

        #Store data into diagnosis variable
        diagnosis = cur.fetchone()

    #Handle SQL errors
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}")

        #Redirect to patient home page
        return redirect(url_for("/patient/home"))
    
    #Close database connection
    finally:
        con.close()

    #Pass diagnosis to the template
    return render_template("patient-diagnosis.html", diagnosis=diagnosis)


@app.route("/doctor/delete/<id>", methods=["POST"])
@login_required
@doctor_only
def delete_data(id):
    """Delete Data"""

    #Try to delete the entry in data table from database
    try:
        con = sqlite3.connect("skincheck.db")
        cur = con.cursor()

        #Delete the entry with id=id from data table
        cur.execute("DELETE FROM data WHERE id = ?", (id,))
        con.commit()
    
    #Handle SQL deletion error
    except sqlite3.Error as e:
        flash(f"An error occurred: {e}")

        #Redirect to doctor home page
        return redirect("/doctor/home")
    
    #Close database connection
    finally:
        con.close()

    flash("Record deleted successfully.")

    #Redirect to doctor home page
    return redirect("/doctor/home")


@app.route("/logout")
def logout():
    # Clear the session variables stored
    session.clear()
    flash("Logout Successful!")

    #Redirect to index
    return redirect("/")






