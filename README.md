# Welcome to SkinCheck!

VIDEO: https://youtu.be/UXG4kgdTNvQ 

To run this website, make sure you are in the SkinCheck directory (through cd statements). Then, on Mac, activate the virtual environment with source .venv/bin/activate then execute “flask run”. Then, all you need to do is click the link that shows up! 

Note:
If you encounter a Access Denied error when clicking on the “flask run” link at any point in time, paste this into your chrome browser:

	chrome://net-internals/#sockets

And click flush socket pools. That should fix the issue!

# # High-Level Description

SkinCheck serves as a website through which doctors and patients can communicate about the status of a patient’s potential skin cancer diagnosis. The primary use case is for physicians (mostly dermatologists or oncologists) that are dealing with cases of potential skin cancer. With the use of a machine learning model called CheckSkin50 (or CS50, for short), physicians can upload high-resolution images of a potential lesion on a patient’s skin, and SkinCheck’s model will output an analyzed version of the image with regions of interest (RoI’s) highlighted for the physician’s review and a diagnosis with a confidence percentage of that diagnosis. Based on this, the physician can make comments on the patient’s prognosis for the patient to review in their portal. Thus far, the accuracy of the machine learning model on a testing set of 660 images is 87.12%. 

The website begins with an initial screen in which the user has three options. 
The user has the ability to visit a “Learn More” page, which details the goals and mission of SkinCheck and some of the machine learning methodology. 
The user can choose to log in as a physician or a patient, depending on which they have the credentials for.
The user can register as a patient or physician. 

If the user is a physician, the user can enter their login credentials, and they are then able to access the physician homepage in the physician portal. Here, the physician will be able to view information about all of their patients, such as name, age, sex, etc. In addition, the physician is able to enter the “file” of a specific patient and upload an image of an area of skin of that patient. Once uploaded, the machine learning model on the back end of SkinCheck analyzes the image and highlights RoI’s. The modified image with highlighted RoI’s is then displayed on the screen using a gradient map, which indicates which RoI’s were perceived by the model as the most important in terms of making its diagnosis (i.e. which RoI’s are most relevant to look at). The model also returns its diagnosis along with a confidence percentage of that diagnosis. Based on this, the physician is able to analyze the image with RoI’s highlighted and use the model’s diagnosis to augment their own diagnosis of the patient, adding comments to the patient’s file accordingly. These comments will then appear in that patient’s portal, allowing patients to see the results of their skin cancer test and understand what their physician’s thoughts on the results are. 

If the user is a patient, the user can enter their login credentials, and they are then able to access the patient homepage in the patient portal. Here, the patient can access information in their “file” such as their name, age, sex, etc. In addition, the patient can access comments in their file that are made by the physician. Based on this, the patient is better able to stay updated on their prognosis and is empowered with information regarding their health. Based on the information available to them here, they can reach out to the physician if they desire. 

Finally, if the user is not signed up for SkinCheck, they can choose to register as a patient. The physician can add the patient to their roster of patients in the physician portal via email. The patient will then appear in the corresponding physician’s portal, and the physician can then upload images and leave comments regarding a potential diagnosis for that patient. 


# # How to Use

Users are greeted with the home page, which is also called the main screen. If they are interested in learning more about SkinCheck and the machine learning methodology behind it, they can click on the “Learn More” button, which will take them to a page that details SkinCheck’s mission and provides metrics to validate the machine learning model. By clicking the home page in the navigation bar, users can return back to the main screen. 

# # # For patients:

If you are a patient looking to sign up with SkinCheck, you will first click the “I am a patient” button on the main screen, at which point you will be directed to a patient login portal. If you click here by mistake, you can click “home” in the navigation bar to return to the main screen. If you have your login credentials already, you may sign in. Otherwise, click on “register” in the navigation bar to sign up for an account. Fill out your information, and you will be registered as a patient. Once you are registered, you can access the patient portal. Within the patient portal, you can view your file, which should have all instances where your doctor has uploaded an image of your skin lesion and made comments about it. For each instance, you can see which doctor made that entry, what date it was, what the diagnosis was, and what the comments were. Click on the text to view the entire comment that the doctor has put. If you want to exit the patient portal, press “log out” in the navigation bar. 

# # # For physicians: 

If you are a physician looking to sign up with SkinCheck, you will first click “I am a doctor”, which will direct you to the physician login portal. If you have clicked here by mistake, you can click “home” in the navigation bar to return to the main screen. If you have your login credentials already, you may sign in. If you are looking to sign up, click on “register” in the navigation bar, which will prompt you to set up an account. 

Once you are registered, you will be taken to the physician portal, where you should be able to see all of your patients. If you want to add any patients, click “Add” in the navigation bar and enter the email of a patient that is registered. If you want to drop any patients, go to “Drop” and you can choose a patient from all of your added patients to drop. 

Once a patient has been added, they will appear in your physician portal, but they will not have a diagnosis. In order to diagnose the patient, go to “Upload”, click on the box labeled “Drop files here”, and upload the image of your patient’s skin legion. Click the “Upload” button and wait for the page to process. The resultant page will have the image you uploaded as well as a gradient map of the analyzed image with the RoI’s highlighted. In addition, the model provides a diagnosis and a percentage of confidence in that diagnosis. To add this to a patient’s file, enter the patient’s email in the associated text box, add any comments you’d like the patient to see in the following text box, and press the submit button. Now, if that patient logs in through the patient portal, they should be able to see the diagnosis made and all of the doctor’s comments.

To return to the main screen, press “Log Out” in the navigation bar.


# # Impact

Ultimately, there are two major impacts to this project. 
Early Diagnosis: Using machine learning offers a rapid mechanism for the early diagnosis of diseases like skin cancer in an accessible manner. By automating the diagnosis workflow, this tool can aid physicians in making more definitive diagnoses in a shorter time frame. In addition, the machine learning model can recognize signs of malignancy early in the development of the tumor, which is critical for better treatment outcomes. 
Democratizing Healthcare: In areas with poor medical infrastructure, this is a tool to democratize access to healthcare, as it is an accessible metric through which physicians can obtain accurate diagnoses for their patients without the use of expensive medical equipment that may be difficult to procure otherwise.
