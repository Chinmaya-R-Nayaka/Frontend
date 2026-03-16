
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

    patient_list = list(patients_col.find())
    if len(patient_list) == 0:
        st.warning("No patients found")
        st.stop()

    patient_dict = {p["name"]: p["_id"] for p in patient_list}

    selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))
    selected_patient = patient_dict[selected_name]

    weight = st.number_input("Weight (kg)", min_value=0.0)
    height = st.number_input("Height (cm)", min_value=0.0)

    if st.button("Save Growth Record"):

        patient = patients_col.find_one({"_id": selected_patient})
        age_months = patient["age_months"]
        percentile = calculate_growth_percentile(weight, height)
        weight_status, height_status = check_who_growth(age_months, weight, height)
        bmi, bmi_status = calculate_bmi(weight, height)
        recommendations = generate_recommendation(weight_status, height_status, bmi_status)

        growth_col.insert_one({
            "patient_id": selected_patient,
            "patient_name": selected_name,
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "bmi_status": bmi_status,
            "weight_status": weight_status,
            "height_status": height_status,
            "percentile": percentile,
            "recommendations": recommendations,
            "recorded_at": datetime.now()
        })

        st.success("Growth record added successfully")

        st.subheader("Growth Analysis")

        st.write("BMI:", bmi)
        st.write("BMI Status:", bmi_status)
        st.write("Weight Status:", weight_status)
        st.write("Height Status:", height_status)

        st.subheader("Doctor Recommendations")

        for r in recommendations:
            st.warning(r)


# ADD IMMUNIZATION
elif menu == "Add Immunization":


    st.header("Add Immunization Record")

    # Fetch patients
    patient_list = list(patients_col.find())

    if len(patient_list) == 0:
        st.warning("No patients found. Please add a patient first.")
        st.stop()

    # Create name → id mapping
    patient_dict = {p["name"]: p["_id"] for p in patient_list}

    selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))
    selected_patient = patient_dict[selected_name]

    vaccine_name = st.text_input("Vaccine Name")
    scheduled_date = st.date_input("Scheduled Date")

    if st.button("Save Immunization"):

        if vaccine_name.strip() == "":
            st.error("Please enter vaccine name")
            st.stop()

        delayed = check_immunization_delay(scheduled_date)

        immunization_col.insert_one({
            "patient_id": selected_patient,
            "patient_name": selected_name,
            "vaccine_name": vaccine_name,
            "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
            "delayed": delayed,
            "created_at": datetime.now()
        })

        # Generate alert if delayed
        if delayed:
            alert_col.insert_one({
                "patient_id": selected_patient,
                "type": "Immunization Delay",
                "status": "Active",
                "created_at": datetime.now()
            })

        st.success("Immunization record added successfully")
    st.header("Add Immunization Record")


# ADD MILESTONE
elif menu == "Add Milestone":


    st.header("Add Developmental Milestone")

    patient_list = list(patients_col.find())

    if len(patient_list) == 0:
        st.warning("No patients found. Please add a patient first.")
        st.stop()

    # name -> id mapping
    patient_dict = {p["name"]: str(p["_id"]) for p in patient_list}

    selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))

    # geting ObjectId
    selected_patient = ObjectId(patient_dict[selected_name])

    milestone_name = st.text_input("Milestone Name")
    expected_age = st.number_input("Expected Age (Months)", min_value=0)
    achieved_age = st.number_input("Achieved Age (Months)", min_value=0)

    if st.button("Save Milestone"):

        delayed = check_milestone_delay(expected_age, achieved_age)

        milestone_col.insert_one({
            "patient_id": selected_patient,
            "patient_name": selected_name,
            "milestone_name": milestone_name,
            "expected_age": expected_age,
            "achieved_age": achieved_age,
            "delayed": delayed,
            "created_at": datetime.now()
        })

        if delayed:
            alert_col.insert_one({
                "patient_id": selected_patient,
                "type": "Milestone Delay",
                "status": "Active",
                "created_at": datetime.now()
            })

        st.success("Milestone saved successfully")
    st.header("Add Developmental Milestone")


# VIEW PATIENTS
elif menu == "View Patients":

    st.header("Patient Records")

    records = list(patients_col.find())

    if len(records) == 0:
        st.warning("No patients found")

    else:
        h1, h2, h3, h4, h5, h6 = st.columns([2,2,2,2,2,1])
        h1.write("Name")
        h2.write("DOB")
        h3.write("Gender")
        h4.write("Age (Months)")
        h5.write("Created At")
        h6.write("Delete")

        st.markdown("---")

        for patient in records:
            c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,2,2,1])

            # CLICKABLE NAME
            if c1.button(patient["name"], key=f"name_{patient['_id']}"):
                st.session_state.selected_patient = patient["_id"]
                st.session_state.menu = "View Patient Details"
                st.rerun()

            c2.write(patient["dob"])
            c3.write(patient["gender"])
            c4.write(patient["age_months"])
            c5.write(patient["created_at"].strftime("%Y-%m-%d"))

            if c6.button("Delete", key=f"del_{patient['_id']}"):

                pid = patient["_id"]

                patients_col.delete_one({"_id": pid})
                growth_col.delete_many({"patient_id": pid})
                immunization_col.delete_many({"patient_id": pid})
                milestone_col.delete_many({"patient_id": pid})
                alert_col.delete_many({"patient_id": pid})

                st.success(f"{patient['name']} deleted successfully")
                st.rerun()


# VIEW PATIENTS DETAILS PAGE
elif menu == "View Patient Details":

    st.header("Patient Complete Record")

    patient_list = list(patients_col.find())
    if len(patient_list) == 0:
        st.warning("No patients found")
    else:
        patient_dict = {p["name"]: p["_id"] for p in patient_list}

        if "selected_patient" in st.session_state:
            selected_patient = st.session_state["selected_patient"]
        else:
            selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))
            selected_patient = patient_dict[selected_name]

        st.markdown("---")

        patient_info = patients_col.find_one({"_id": selected_patient})

        st.subheader("Patient Profile")

        patient_info.pop("_id", None)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👶 Name", patient_info["name"])
        col2.metric("🧑 Gender", patient_info["gender"])
        col3.metric("📅 Age (Months)", patient_info["age_months"])
        col4.metric("🎂 DOB", patient_info["dob"])

        st.markdown("---")

        # HEALTH ALERT BANNER
        immunization_delays = list(immunization_col.find({
            "patient_id": selected_patient,
            "delayed": True
        }))

        milestone_delays = list(milestone_col.find({
            "patient_id": selected_patient,
            "delayed": True
        }))

        total_alerts = len(immunization_delays) + len(milestone_delays)
        if total_alerts > 0:
            st.error(f"⚠ {total_alerts} Health Alerts Detected")
        else:
            st.success("✅ No Health Alerts")

        # GROWTH RECORDS
        st.subheader("Growth Records")

        growth_records = list(growth_col.find({"patient_id": selected_patient}))
        if growth_records:
            for g in growth_records:
                g.pop("_id", None)
                g.pop("patient_id", None)
                if g.get("weight_status") == "Underweight":
                    st.warning(f"⚠ Underweight detected on {g['recorded_at']}")

            st.dataframe(growth_records)

        else:
            st.info("No growth records found")

        st.markdown("---")

        # IMMUNIZATION RECORDS
        st.subheader("Immunization Records")

        immunization_records = list(immunization_col.find({"patient_id": selected_patient}))
        if immunization_records:
            for i in immunization_records:
                i.pop("_id", None)
                i.pop("patient_id", None)

            st.dataframe(immunization_records)

        else:
            st.info("No immunization records found")

        st.markdown("---")

        # MILESTONE RECORDS
        st.subheader("Milestone Records")

        milestone_records = list(milestone_col.find({"patient_id": selected_patient}))
        if milestone_records:
            for m in milestone_records:
                m.pop("_id", None)
                m.pop("patient_id", None)

            st.dataframe(milestone_records)

        else:
            st.info("No milestone records found")

        st.markdown("---")

        # IMMUNIZATION DELAYS
        st.subheader("Immunization Delays")
        if immunization_delays:
            h1, h2, h3, h4 = st.columns([3,3,2,1])
            h1.write("Vaccine Name")
            h2.write("Scheduled Date")
            h3.write("Status")
            h4.write("Resolve")

            st.markdown("---")

            for record in immunization_delays:
                c1, c2, c3, c4 = st.columns([3,3,2,1])
                c1.write(record["vaccine_name"])
                c2.write(record["scheduled_date"])
                c3.markdown("🔴 **Active**")

                if c4.button("Resolve", key=f"imm_{record['_id']}"):
                    immunization_col.update_one(
                        {"_id": record["_id"]},
                        {"$set": {"delayed": False}}
                    )

                    st.success("Immunization delay resolved")
                    st.rerun()

        else:
            st.success("No immunization delays")

        st.markdown("---")

        # MILESTONE DELAYS
        st.subheader("Milestone Delays")

        if milestone_delays:
            h1, h2, h3, h4 = st.columns([3,2,2,2])
            h1.write("Milestone Name")
            h2.write("Expected Age")
            h3.write("Achieved Age")
            h4.write("Status")

            st.markdown("---")

            for record in milestone_delays:
                c1, c2, c3, c4 = st.columns([3,2,2,2])
                c1.write(record["milestone_name"])
                c2.write(f"{record['expected_age']} months")
                c3.write(f"{record['achieved_age']} months")
                c4.markdown("🔴 **Delayed**")

        else:
            st.success("No milestone delays")

    if st.button("⬅ Back to Patients"):
        st.session_state.menu = "View Patients"
        st.rerun()


# VIEW ALERTS PAGE (ONLY ACTIVE ALERTS)
elif menu == "View Alerts":

    st.header("Generated Alerts")
    display_data = []

    # IMMUNIZATION DELAYS
    immunization_delays = list(immunization_col.find({"delayed": True}))

    for record in immunization_delays:
        patient = patients_col.find_one({"_id": record["patient_id"]})
        if patient:
            patient_name = patient["name"]
        else:
            patient_name = "Unknown"

        display_data.append({
            "Patient Name": patient_name,
            "Alert Type": "Immunization Delay",
            "Detail": record.get("vaccine_name", "Unknown"),
            "Scheduled Date": record.get("scheduled_date", "Unknown")
        })

    # MILESTONE DELAYS
    # milestone_delays = list(milestone_col.find({"delayed": True}))
    # for record in milestone_delays:
    #     patient = patients_col.find_one({"_id": record["patient_id"]})
    #     if patient:
    #         patient_name = patient["name"]
    #     else:
    #         patient_name = "Unknown"

    #     display_data.append({
    #         "Patient Name": patient_name,
    #         "Alert Type": "Milestone Delay",
    #         "Detail": record.get("milestone_name", "Unknown"),
    #         "Scheduled Date": f"{record.get('expected_age','?')} months"
    #     })


    # DISPLAY TABLE
    if display_data:
        st.dataframe(display_data, use_container_width=True)
    else:
        st.success("✅ No Active Alerts")

    
