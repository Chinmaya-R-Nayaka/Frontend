
from bson import ObjectId
import streamlit as st
from datetime import datetime
from db import get_database
from services import (
    calculate_age_in_months, calculate_growth_percentile, 
    check_milestone_delay, check_immunization_delay, check_who_growth,
    calculate_bmi, generate_recommendation
)

# Database Setup
db = get_database()

patients_col = db["patients"]
growth_col = db["growth"]
immunization_col = db["immunization"]
milestone_col = db["milestones"]
alert_col = db["alerts"]

# UI Layout
st.set_page_config(page_title="M3 Pediatric System", layout="wide")

st.title("M3 - Pediatric Clinical Data System")
st.markdown("---")

menu_options = [
    "Add Patient",
    "Add Growth Record",
    "Add Immunization",
    "Add Milestone",
    "View Patients",
    "View Patient Details",
    "View Alerts"
]

# initialize session menu
if "menu" not in st.session_state:
    st.session_state.menu = "View Patients"

menu = st.sidebar.selectbox(
    "Select Module",
    menu_options,
    index=menu_options.index(st.session_state.menu)
)

st.session_state.menu = menu


# ADD PATIENT
if menu == "Add Patient":

    st.header("Add New Pediatric Patient")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Child Name")
        gender = st.selectbox("Gender", ["Male", "Female"])

    with col2:
        dob = st.date_input("Date of Birth")

    if st.button("Save Patient"):

        if name.strip() == "":
            st.error("Patient name cannot be empty")
            st.stop()

        age_months = calculate_age_in_months(dob)

        patients_col.insert_one({
            "name": name.strip(),
            "dob": dob.strftime("%Y-%m-%d"),
            "gender": gender,
            "age_months": age_months,
            "created_at": datetime.now()
        })

        st.success("Patient saved successfully")



# ADD GROWTH
elif menu == "Add Growth Record":

    st.header("Add Growth Measurement")


# ADD IMMUNIZATION
elif menu == "Add Immunization":

    st.header("Add Immunization Record")


# ADD MILESTONE
elif menu == "Add Milestone":

    st.header("Add Developmental Milestone")


# VIEW PATIENTS
elif menu == "View Patients":

    st.header("Patient Records")


# VIEW PATIENTS DETAILS PAGE
elif menu == "View Patient Details":

    st.header("Patient Complete Record")


# VIEW ALERTS PAGE (ONLY ACTIVE ALERTS)
elif menu == "View Alerts":

    st.header("Generated Alerts")
    
