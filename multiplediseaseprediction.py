import numpy as np
import tensorflow as tf

from PIL import Image
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import pyodbc

# Database connection
def get_db_connection():
    conn = pyodbc.connect(
         'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=HARIHARAN\SQLEXPRESS;'  # Replace with your server name
        'DATABASE=UserDB;'     # Replace with your database name
         'Trusted_Connection=yes;'
    )
    return conn


@st.cache_resource
def load_covid_model():
    return tf.keras.models.load_model("covid.h5")  # Replace with your trained model path

# Function to preprocess the uploaded image
def preprocess_image(image):
    img = image.resize((224, 224))  # Resize to match the input size of the model
    img_array = np.array(img)  # Convert image to NumPy array
    # Ensure the image has 3 channels (RGB)
    if img_array.ndim == 2:  # Grayscale image
        img_array = np.stack((img_array,) * 3, axis=-1)  # Convert grayscale to RGB by duplicating channels
    elif img_array.shape[2] == 4:  # RGBA image
        img_array = img_array[:, :, :3]  # Drop the alpha channel
    img_array = img_array / 255.0  # Normalize pixel values to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


# Function to create a new user
def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor ()
    cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Function to check user credentials
def check_user_credentials(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Username = ? AND Password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Load models
diabetes_model = pickle.load(open("diabetes_model.sav", 'rb'))
heart_disease_model =  pickle.load(open("heart_disease_model.sav", 'rb'))
parkinsons_model = pickle.load(open("parkinsons_model.sav", 'rb'))

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Initialize session state for input fields
if 'diabetes_inputs' not in st.session_state:
    st.session_state['diabetes_inputs'] = {
        'Pregnancies': '',
        'Glucose': '',
        'BloodPressure': '',
        'SkinThickness': '',
        'Insulin': '',
        'BMI': '',
        'DiabetesPedigreeFunction': '',
        'Age': ''
    }

if 'heart_disease_inputs' not in st.session_state:
    st.session_state['heart_disease_inputs'] = {
        'age': '',
        'sex': '',
        'cp': '',
        'trestbps': '',
        'chol': '',
        'fbs': '',
        'restecg': '',
        'thalach': '',
        'exang': '',
        'oldpeak': '',
        'slope': '',
        'ca': '',
        'thal': ''
    }

if 'parkinsons_inputs' not in st.session_state:
    st.session_state['parkinsons_inputs'] = {
        'fo': '',
        'fhi': '',
        'flo': '',
        'Jitter_percent': '',
        'Jitter_Abs': '',
        'RAP': '',
        'PPQ': '',
        'DDP': '',
        'Shimmer': '',
        'Shimmer_dB': '',
        'APQ3': '',
        'APQ5': '',
        'APQ': '',
        'DDA': '',
        'NHR': '',
        'HNR': '',
        'RPDE': '',
        'DFA': '',
        'spread1': '',
        'spread2': '',
        'D2': '',
        'PPE': ''
    }

# Track the previously selected page to detect page changes
if 'previous_page' not in st.session_state:
    st.session_state['previous_page'] = None

# Login and Sign Up Page
def login_signup_page():
    st.title("Login / Sign Up")
    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Select Option", menu)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            user = check_user_credentials(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")

    elif choice == "Sign Up":
        st.subheader("Sign Up")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')

        if st.button("Sign Up"):
            if new_password == confirm_password:
                create_user(new_username, new_password)
                st.success("Account created successfully! Please login.")
            else:
                st.error("Passwords do not match")

# Main App
def main_app():
    with st.sidebar:
        selected = option_menu('Multiple Disease Prediction System',
                               ['Diabetes Prediction',
                                'Heart Disease Prediction',
                                'Parkinsons Prediction',
                                'COVID-19 Detection'],
                               icons=['activity', 'heart', 'person', 'lungs'],
                               default_index=0)


        # Logout button
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.success("Logged out successfully!")
            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()

    # Detect page change and clear inputs for the previous page
    if st.session_state['previous_page'] != selected:
        if st.session_state['previous_page'] == 'Diabetes Prediction':
            st.session_state['diabetes_inputs'] = {key: '' for key in st.session_state['diabetes_inputs']}
        elif st.session_state['previous_page'] == 'Heart Disease Prediction':
            st.session_state['heart_disease_inputs'] = {key: '' for key in st.session_state['heart_disease_inputs']}
        elif st.session_state['previous_page'] == 'Parkinsons Prediction':
            st.session_state['parkinsons_inputs'] = {key: '' for key in st.session_state['parkinsons_inputs']}

        # Update the previous page to the current selection
        st.session_state['previous_page'] = selected

    st.title("Multiple Disease Prediction System")

    if selected == 'Diabetes Prediction':
        st.subheader('Diabetes Prediction')
        # Display the diabetes prediction features table
         
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state['diabetes_inputs']['Pregnancies'] = st.text_input('Number of Pregnancies', 
                help="Number of times the person has been pregnant (Normal: 0-15)", 
                value=st.session_state['diabetes_inputs']['Pregnancies'])
        with col2:
            st.session_state['diabetes_inputs']['Glucose'] = st.text_input('Glucose Level', 
                help="Glucose level in the blood (mg/dL) (Normal: 70-140, Max: 200)", 
                value=st.session_state['diabetes_inputs']['Glucose'])
        with col3:
            st.session_state['diabetes_inputs']['BloodPressure'] = st.text_input('Blood Pressure value', 
                help="Diastolic blood pressure (mm Hg) (Normal: 60-90, Max: 120)", 
                value=st.session_state['diabetes_inputs']['BloodPressure'])
        with col1:
            st.session_state['diabetes_inputs']['SkinThickness'] = st.text_input('Skin Thickness value', 
                help="Thickness of the skin fold on the triceps (mm) (Normal: 10-30, Max: 50)", 
                value=st.session_state['diabetes_inputs']['SkinThickness'])
        with col2:
            st.session_state['diabetes_inputs']['Insulin'] = st.text_input('Insulin Level', 
                help="2-Hour serum insulin (mu U/ml) (Normal: 16-166, Max: 846)", 
                value=st.session_state['diabetes_inputs']['Insulin'])
        with col3:
            st.session_state['diabetes_inputs']['BMI'] = st.text_input('BMI value', 
                help="Body Mass Index (weight in kg/(height in m)^2) (Normal: 18.5-24.9, Max: 60)", 
                value=st.session_state['diabetes_inputs']['BMI'])
        with col1:
            st.session_state['diabetes_inputs']['DiabetesPedigreeFunction'] = st.text_input('Diabetes Pedigree Function value', 
                help="A function that scores the likelihood of diabetes based on family history (Normal: 0.078-2.42, Max: 2.5)", 
                value=st.session_state['diabetes_inputs']['DiabetesPedigreeFunction'])
        with col2:
            st.session_state['diabetes_inputs']['Age'] = st.text_input('Age of the Person', 
                help="Age in years (Normal: 21-81, Max: 120)", 
                value=st.session_state['diabetes_inputs']['Age'])

        if st.button('Diabetes Test Result'):
            try:
                Pregnancies = int(st.session_state['diabetes_inputs']['Pregnancies'])
                Glucose = int(st.session_state['diabetes_inputs']['Glucose'])
                BloodPressure = int(st.session_state['diabetes_inputs']['BloodPressure'])
                SkinThickness = int(st.session_state['diabetes_inputs']['SkinThickness'])
                Insulin = int(st.session_state['diabetes_inputs']['Insulin'])
                BMI = float(st.session_state['diabetes_inputs']['BMI'])
                DiabetesPedigreeFunction = float(st.session_state['diabetes_inputs']['DiabetesPedigreeFunction'])
                Age = int(st.session_state['diabetes_inputs']['Age'])

                # Validate inputs
                if not (0 <= Pregnancies <= 15):
                    st.error(f"Number of Pregnancies must be between 0 and 15. You entered: {Pregnancies}")
                elif not (70 <= Glucose <= 200):
                    st.error(f"Glucose level must be between 70 and 200. You entered: {Glucose}")
                elif not (60 <= BloodPressure <= 120):
                    st.error(f"Blood Pressure must be between 60 and 120. You entered: {BloodPressure}")
                elif not (10 <= SkinThickness <= 50):
                    st.error(f"Skin Thickness must be between 10 and 50. You entered: {SkinThickness}")
                elif not (16 <= Insulin <= 846):
                    st.error(f"Insulin level must be between 16 and 846. You entered: {Insulin}")
                elif not (18.5 <= BMI <= 60):
                    st.error(f"BMI must be between 18.5 and 60. You entered: {BMI}")
                elif not (0.078 <= DiabetesPedigreeFunction <= 2.5):
                    st.error(f"Diabetes Pedigree Function must be between 0.078 and 2.5. You entered: {DiabetesPedigreeFunction}")
                elif not (21 <= Age <= 120):
                    st.error(f"Age must be between 21 and 120. You entered: {Age}")
                else:
                    diab_prediction = diabetes_model.predict([[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]])
                    if diab_prediction[0] == 1:
                        st.success('The person is diabetic')
                    else:
                        st.success('The person is not diabetic')
            except ValueError:
                st.error("Please enter valid numeric values for all fields.")

    elif selected == 'Heart Disease Prediction':
        st.subheader('Heart Disease Prediction')
        # Display the heart disease prediction features table 
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state['heart_disease_inputs']['age'] = st.text_input('Age', 
                help="Age in years (Normal: 20-80, Max: 120)", 
                value=st.session_state['heart_disease_inputs']['age'])
        with col2:
            st.session_state['heart_disease_inputs']['sex'] = st.text_input('Sex', 
                help="Sex (1 = male; 0 = female)", 
                value=st.session_state['heart_disease_inputs']['sex'])
        with col3:
            st.session_state['heart_disease_inputs']['cp'] = st.text_input('Chest Pain types', 
                help="Chest pain type (0 = typical angina; 1 = atypical angina; 2 = non-anginal pain; 3 = asymptomatic)", 
                value=st.session_state['heart_disease_inputs']['cp'])
        with col1:
            st.session_state['heart_disease_inputs']['trestbps'] = st.text_input('Resting Blood Pressure', 
                help="Resting blood pressure (mm Hg) (Normal: 80-120, Max: 200)", 
                value=st.session_state['heart_disease_inputs']['trestbps'])
        with col2:
            st.session_state['heart_disease_inputs']['chol'] = st.text_input('Serum Cholestoral in mg/dl', 
                help="Serum cholesterol level (mg/dL) (Normal: 120-240, Max: 600)", 
                value=st.session_state['heart_disease_inputs']['chol'])
        with col3:
            st.session_state['heart_disease_inputs']['fbs'] = st.text_input('Fasting Blood Sugar > 120 mg/dl', 
                help="Fasting blood sugar > 120 mg/dL (1 = true; 0 = false)", 
                value=st.session_state['heart_disease_inputs']['fbs'])
        with col1:
            st.session_state['heart_disease_inputs']['restecg'] = st.text_input('Resting Electrocardiographic results', 
                help="Resting electrocardiographic results (0 = normal; 1 = ST-T wave abnormality; 2 = probable or definite left ventricular hypertrophy)", 
                value=st.session_state['heart_disease_inputs']['restecg'])
        with col2:
            st.session_state['heart_disease_inputs']['thalach'] = st.text_input('Maximum Heart Rate achieved', 
                help="Maximum heart rate achieved during exercise (Normal: 60-100, Max: 220)", 
                value=st.session_state['heart_disease_inputs']['thalach'])
        with col3:
            st.session_state['heart_disease_inputs']['exang'] = st.text_input('Exercise Induced Angina', 
                help="Exercise-induced angina (1 = yes; 0 = no)", 
                value=st.session_state['heart_disease_inputs']['exang'])
        with col1:
            st.session_state['heart_disease_inputs']['oldpeak'] = st.text_input('ST depression induced by exercise', 
                help="ST depression induced by exercise relative to rest (Normal: 0-2, Max: 6)", 
                value=st.session_state['heart_disease_inputs']['oldpeak'])
        with col2:
            st.session_state['heart_disease_inputs']['slope'] = st.text_input('Slope of the peak exercise ST segment', 
                help="Slope of the peak exercise ST segment (0 = upsloping; 1 = flat; 2 = downsloping)", 
                value=st.session_state['heart_disease_inputs']['slope'])
        with col3:
            st.session_state['heart_disease_inputs']['ca'] = st.text_input('Major vessels colored by fluoroscopy', 
                help="Number of major vessels colored by fluoroscopy (0-3)", 
                value=st.session_state['heart_disease_inputs']['ca'])
        with col1:
            st.session_state['heart_disease_inputs']['thal'] = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversible defect', 
                help="Thalassemia (0 = normal; 1 = fixed defect; 2 = reversible defect)", 
                value=st.session_state['heart_disease_inputs']['thal'])

        if st.button('Heart Disease Test Result'):
            try:
                age = int(st.session_state['heart_disease_inputs']['age'])
                sex = int(st.session_state['heart_disease_inputs']['sex'])
                cp = int(st.session_state['heart_disease_inputs']['cp'])
                trestbps = int(st.session_state['heart_disease_inputs']['trestbps'])
                chol = int(st.session_state['heart_disease_inputs']['chol'])
                fbs = int(st.session_state['heart_disease_inputs']['fbs'])
                restecg = int(st.session_state['heart_disease_inputs']['restecg'])
                thalach = int(st.session_state['heart_disease_inputs']['thalach'])
                exang = int(st.session_state['heart_disease_inputs']['exang'])
                oldpeak = float(st.session_state['heart_disease_inputs']['oldpeak'])
                slope = int(st.session_state['heart_disease_inputs']['slope'])
                ca = int(st.session_state['heart_disease_inputs']['ca'])
                thal = int(st.session_state['heart_disease_inputs']['thal'])

                # Validate inputs
                if not (20 <= age <= 120):
                    st.error(f"Age must be between 20 and 120. You entered: {age}")
                elif not (sex in [0, 1]):
                    st.error(f"Sex must be either 0 or 1. You entered: {sex}")
                elif not (cp in [0, 1, 2, 3]):
                    st.error(f"Chest Pain type must be 0, 1, 2, or 3. You entered: {cp}")
                elif not (80 <= trestbps <= 200):
                    st.error(f"Resting Blood Pressure must be between 80 and 200. You entered: {trestbps}")
                elif not (120 <= chol <= 600):
                    st.error(f"Cholesterol must be between 120 and 600. You entered: {chol}")
                elif not (fbs in [0, 1]):
                    st.error(f"Fasting Blood Sugar must be either 0 or 1. You entered: {fbs}")
                elif not (restecg in [0, 1, 2]):
                    st.error(f"Resting ECG must be 0, 1, or 2. You entered: {restecg}")
                elif not (60 <= thalach <= 220):
                    st.error(f"Maximum Heart Rate must be between 60 and 220. You entered: {thalach}")
                elif not (exang in [0, 1]):
                    st.error(f"Exercise Induced Angina must be either 0 or 1. You entered: {exang}")
                elif not (0 <= oldpeak <= 6):
                    st.error(f"ST Depression must be between 0 and 6. You entered: {oldpeak}")
                elif not (slope in [0, 1, 2]):
                    st.error(f"Slope must be 0, 1, or 2. You entered: {slope}")
                elif not (0 <= ca <= 3):
                    st.error(f"Major Vessels Colored must be between 0 and 3. You entered: {ca}")
                elif not (thal in [0, 1, 2]):
                    st.error(f"Thalassemia must be 0, 1, or 2. You entered: {thal}")
                else:
                    heart_prediction = heart_disease_model.predict([[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]])
                    if heart_prediction[0] == 1:
                        st.success('The person is having heart disease')
                    else:
                        st.success('The person does not have any heart disease')
            except ValueError:
                st.error("Please enter valid numeric values for all fields.")

    elif selected == "Parkinsons Prediction":
        st.subheader("Parkinson's Disease Prediction")
        # Display the Parkinson's disease prediction features table 
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.session_state['parkinsons_inputs']['fo'] = st.text_input('MDVP:Fo(Hz)', 
                help="Average vocal fundamental frequency (Normal: 85-260 Hz, Max: 300)", 
                value=st.session_state['parkinsons_inputs']['fo'])
        with col2:
            st.session_state['parkinsons_inputs']['fhi'] = st.text_input('MDVP:Fhi(Hz)', 
                help="Maximum vocal fundamental frequency (Normal: 100-500 Hz, Max: 600)", 
                value=st.session_state['parkinsons_inputs']['fhi'])
        with col3:
            st.session_state['parkinsons_inputs']['flo'] = st.text_input('MDVP:Flo(Hz)', 
                help="Minimum vocal fundamental frequency (Normal: 60-180 Hz, Max: 200)", 
                value=st.session_state['parkinsons_inputs']['flo'])
        with col4:
            st.session_state['parkinsons_inputs']['Jitter_percent'] = st.text_input('MDVP:Jitter(%)', 
                help="Jitter as a percentage of the fundamental frequency (Normal: 0.001-0.01%, Max: 0.02%)", 
                value=st.session_state['parkinsons_inputs']['Jitter_percent'])
        with col5:
            st.session_state['parkinsons_inputs']['Jitter_Abs'] = st.text_input('MDVP:Jitter(Abs)', 
                help="Absolute jitter value (Normal: 0.00001-0.0001, Max: 0.0002)", 
                value=st.session_state['parkinsons_inputs']['Jitter_Abs'])
        with col1:
            st.session_state['parkinsons_inputs']['RAP'] = st.text_input('MDVP:RAP', 
                help="Relative amplitude perturbation (Normal: 0.001-0.01, Max: 0.02)", 
                value=st.session_state['parkinsons_inputs']['RAP'])
        with col2:
            st.session_state['parkinsons_inputs']['PPQ'] = st.text_input('MDVP:PPQ', 
                help="Five-point period perturbation quotient (Normal: 0.001-0.01, Max: 0.02)", 
                value=st.session_state['parkinsons_inputs']['PPQ'])
        with col3:
            st.session_state['parkinsons_inputs']['DDP'] = st.text_input('Jitter:DDP', 
                help="Average absolute difference of differences between consecutive periods (Normal: 0.001-0.01, Max: 0.02)", 
                value=st.session_state['parkinsons_inputs']['DDP'])
        with col4:
            st.session_state['parkinsons_inputs']['Shimmer'] = st.text_input('MDVP:Shimmer', 
                help="Shimmer (amplitude variation) (Normal: 0.01-0.05, Max: 0.1)", 
                value=st.session_state['parkinsons_inputs']['Shimmer'])
        with col5:
            st.session_state['parkinsons_inputs']['Shimmer_dB'] = st.text_input('MDVP:Shimmer(dB)', 
                help="Shimmer in decibels (Normal: 0.1-0.5 dB, Max: 1.0)", 
                value=st.session_state['parkinsons_inputs']['Shimmer_dB'])
        with col1:
            st.session_state['parkinsons_inputs']['APQ3'] = st.text_input('Shimmer:APQ3', 
                help="Amplitude perturbation quotient over three points (Normal: 0.01-0.05, Max: 0.1)", 
                value=st.session_state['parkinsons_inputs']['APQ3'])
        with col2:
            st.session_state['parkinsons_inputs']['APQ5'] = st.text_input('Shimmer:APQ5', 
                help="Amplitude perturbation quotient over five points (Normal: 0.01-0.05, Max: 0.1)", 
                value=st.session_state['parkinsons_inputs']['APQ5'])
        with col3:
            st.session_state['parkinsons_inputs']['APQ'] = st.text_input('MDVP:APQ', 
                help="Amplitude perturbation quotient (Normal: 0.01-0.05, Max: 0.1)", 
                value=st.session_state['parkinsons_inputs']['APQ'])
        with col4:
            st.session_state['parkinsons_inputs']['DDA'] = st.text_input('Shimmer:DDA', 
                help="Average absolute difference between consecutive differences of amplitudes (Normal: 0.01-0.05, Max: 0.1)", 
                value=st.session_state['parkinsons_inputs']['DDA'])
        with col5:
            st.session_state['parkinsons_inputs']['NHR'] = st.text_input('NHR', 
                help="Noise-to-harmonics ratio (Normal: 0.01-0.1, Max: 0.2)", 
                value=st.session_state['parkinsons_inputs']['NHR'])
        with col1:
            st.session_state['parkinsons_inputs']['HNR'] = st.text_input('HNR', 
                help="Harmonics-to-noise ratio (Normal: 20-30 dB, Max: 40)", 
                value=st.session_state['parkinsons_inputs']['HNR'])
        with col2:
            st.session_state['parkinsons_inputs']['RPDE'] = st.text_input('RPDE', 
                help="Recurrence period density entropy (Normal: 0.1-0.6, Max: 1.0)", 
                value=st.session_state['parkinsons_inputs']['RPDE'])
        with col3:
            st.session_state['parkinsons_inputs']['DFA'] = st.text_input('DFA', 
                help="Detrended fluctuation analysis (Normal: 0.5-1.5, Max: 2.0)", 
                value=st.session_state['parkinsons_inputs']['DFA'])
        with col4:
            st.session_state['parkinsons_inputs']['spread1'] = st.text_input('spread1', 
                help="Nonlinear measure of fundamental frequency variation (Normal: -7 to -2, Max: 0)", 
                value=st.session_state['parkinsons_inputs']['spread1'])
        with col5:
            st.session_state['parkinsons_inputs']['spread2'] = st.text_input('spread2', 
                help="Nonlinear measure of fundamental frequency variation (Normal: 0.01-0.2, Max: 0.3)", 
                value=st.session_state['parkinsons_inputs']['spread2'])
        with col1:
            st.session_state['parkinsons_inputs']['D2'] = st.text_input('D2', 
                help="Correlation dimension (Normal: 1.5-2.5, Max: 3.0)", 
                value=st.session_state['parkinsons_inputs']['D2'])
        with col2:
            st.session_state['parkinsons_inputs']['PPE'] = st.text_input('PPE', 
                help="Pitch period entropy (Normal: 0.1-0.5, Max: 1.0)", 
                value=st.session_state['parkinsons_inputs']['PPE'])

        if st.button("Parkinson's Test Result"):
            try:
                fo = float(st.session_state['parkinsons_inputs']['fo'])
                fhi = float(st.session_state['parkinsons_inputs']['fhi'])
                flo = float(st.session_state['parkinsons_inputs']['flo'])
                Jitter_percent = float(st.session_state['parkinsons_inputs']['Jitter_percent'])
                Jitter_Abs = float(st.session_state['parkinsons_inputs']['Jitter_Abs'])
                RAP = float(st.session_state['parkinsons_inputs']['RAP'])
                PPQ = float(st.session_state['parkinsons_inputs']['PPQ'])
                DDP = float(st.session_state['parkinsons_inputs']['DDP'])
                Shimmer = float(st.session_state['parkinsons_inputs']['Shimmer'])
                Shimmer_dB = float(st.session_state['parkinsons_inputs']['Shimmer_dB'])
                APQ3 = float(st.session_state['parkinsons_inputs']['APQ3'])
                APQ5 = float(st.session_state['parkinsons_inputs']['APQ5'])
                APQ = float(st.session_state['parkinsons_inputs']['APQ'])
                DDA = float(st.session_state['parkinsons_inputs']['DDA'])
                NHR = float(st.session_state['parkinsons_inputs']['NHR'])
                HNR = float(st.session_state['parkinsons_inputs']['HNR'])
                RPDE = float(st.session_state['parkinsons_inputs']['RPDE'])
                DFA = float(st.session_state['parkinsons_inputs']['DFA'])
                spread1 = float(st.session_state['parkinsons_inputs']['spread1'])
                spread2 = float(st.session_state['parkinsons_inputs']['spread2'])
                D2 = float(st.session_state['parkinsons_inputs']['D2'])
                PPE = float(st.session_state['parkinsons_inputs']['PPE'])

                # Validate inputs
                if not (85 <= fo <= 300):
                    st.error(f"MDVP:Fo(Hz) must be between 85 and 300. You entered: {fo}")
                elif not (100 <= fhi <= 600):
                    st.error(f"MDVP:Fhi(Hz) must be between 100 and 600. You entered: {fhi}")
                elif not (60 <= flo <= 200):
                    st.error(f"MDVP:Flo(Hz) must be between 60 and 200. You entered: {flo}")
                elif not (0.001 <= Jitter_percent <= 0.02):
                    st.error(f"MDVP:Jitter(%) must be between 0.001 and 0.02. You entered: {Jitter_percent}")
                elif not (0.00001 <= Jitter_Abs <= 0.0002):
                    st.error(f"MDVP:Jitter(Abs) must be between 0.00001 and 0.0002. You entered: {Jitter_Abs}")
                elif not (0.001 <= RAP <= 0.02):
                    st.error(f"MDVP:RAP must be between 0.001 and 0.02. You entered: {RAP}")
                elif not (0.001 <= PPQ <= 0.02):
                    st.error(f"MDVP:PPQ must be between 0.001 and 0.02. You entered: {PPQ}")
                elif not (0.001 <= DDP <= 0.02):
                    st.error(f"Jitter:DDP must be between 0.001 and 0.02. You entered: {DDP}")
                elif not (0.01 <= Shimmer <= 0.1):
                    st.error(f"MDVP:Shimmer must be between 0.01 and 0.1. You entered: {Shimmer}")
                elif not (0.1 <= Shimmer_dB <= 1.0):
                    st.error(f"MDVP:Shimmer(dB) must be between 0.1 and 1.0. You entered: {Shimmer_dB}")
                elif not (0.01 <= APQ3 <= 0.1):
                    st.error(f"Shimmer:APQ3 must be between 0.01 and 0.1. You entered: {APQ3}")
                elif not (0.01 <= APQ5 <= 0.1):
                    st.error(f"Shimmer:APQ5 must be between 0.01 and 0.1. You entered: {APQ5}")
                elif not (0.01 <= APQ <= 0.1):
                    st.error(f"MDVP:APQ must be between 0.01 and 0.1. You entered: {APQ}")
                elif not (0.01 <= DDA <= 0.1):
                    st.error(f"Shimmer:DDA must be between 0.01 and 0.1. You entered: {DDA}")
                elif not (0.01 <= NHR <= 0.2):
                    st.error(f"NHR must be between 0.01 and 0.2. You entered: {NHR}")
                elif not (20 <= HNR <= 40):
                    st.error(f"HNR must be between 20 and 40. You entered: {HNR}")
                elif not (0.1 <= RPDE <= 1.0):
                    st.error(f"RPDE must be between 0.1 and 1.0. You entered: {RPDE}")
                elif not (0.5 <= DFA <= 2.0):
                    st.error(f"DFA must be between 0.5 and 2.0. You entered: {DFA}")
                elif not (-7 <= spread1 <= 0):
                    st.error(f"spread1 must be between -7 and 0. You entered: {spread1}")
                elif not (0.01 <= spread2 <= 0.3):
                    st.error(f"spread2 must be between 0.01 and 0.3. You entered: {spread2}")
                elif not (1.5 <= D2 <= 3.0):
                    st.error(f"D2 must be between 1.5 and 3.0. You entered: {D2}")
                elif not (0.1 <= PPE <= 1.0):
                    st.error(f"PPE must be between 0.1 and 1.0. You entered: {PPE}")
                else:
                    parkinsons_prediction = parkinsons_model.predict([[fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]])
                    if parkinsons_prediction[0] == 1:
                        st.success("The person has Parkinson's disease")
                    else:
                        st.success("The person does not have Parkinson's disease")
            except ValueError:
                st.error("Please enter valid numeric values for all fields.")
    elif selected == 'COVID-19 Detection':
        st.subheader("COVID-19 Lung X-Ray Classification")
        st.write("Upload a lung X-ray image to classify it into one of the following categories: Normal, Lung Opacity, Viral Pneumonia, or COVID.")

        # File uploader for the lung image
        uploaded_file = st.file_uploader("Upload Lung X-Ray Image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Lung X-Ray Image", use_column_width=True)

            # Preprocess the image for the model
            img_array = preprocess_image(image)

            # Predict using the model
            if st.button("Classify Image"):
                try:
                    model = load_covid_model()
                    prediction = model.predict(img_array)
                    predicted_class = np.argmax(prediction, axis=1)[0]

                    # Define class names
                    class_names = ["Normal", "Lung Opacity", "Viral Pneumonia", "COVID"]
                    predicted_label = class_names[predicted_class]

                    # Display the result
                    if predicted_label == "Normal":
                        st.success(f"The image is classified as *{predicted_label}*.")
                    elif predicted_label == "Lung Opacity":
                        st.warning(f"The image is classified as *{predicted_label}*.")
                    elif predicted_label == "Viral Pneumonia":
                        st.error(f"The image is classified as *{predicted_label}*.")
                    elif predicted_label == "COVID":
                        st.error(f"The image is classified as *{predicted_label}*.")

                    # Display probabilities for each class
                    st.subheader("Prediction Probabilities:")
                    for i, prob in enumerate(prediction[0]):
                        st.write(f"{class_names[i]}: {prob * 100:.2f}%")
                except Exception as e:
                    st.error(f"An error occurred during prediction: {str(e)}")
# Run the app
if not st.session_state['logged_in']:
    login_signup_page()
else:
    main_app()