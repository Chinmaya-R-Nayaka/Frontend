import streamlit as st
import requests
from src.M3 import api_client as api

# --- Custom Alert Overrides ---
def custom_success(msg, *args, **kwargs):
    msg = str(msg).replace("✅", "").strip()
    st.markdown(f"""
        <div style="background-color: #173620; color: #57c776; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1rem;">✅ {msg}</span>
        </div>
    """, unsafe_allow_html=True)

def custom_error(msg, *args, **kwargs):
    msg = str(msg).replace("🚨", "").replace("⚠", "").strip()
    st.markdown(f"""
        <div style="background-color: #3b1515; color: #ff6b6b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1rem;">🚨 {msg}</span>
        </div>
    """, unsafe_allow_html=True)

def custom_warning(msg, *args, **kwargs):
    msg = str(msg).replace("⚠", "").strip()
    st.markdown(f"""
        <div style="background-color: #3b3010; color: #ffca28; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1rem;">⚠ {msg}</span>
        </div>
    """, unsafe_allow_html=True)

def _load_patient_dict() -> dict[str, str]:
    try:
        patients = api.get_all_patients()
    except requests.RequestException as e:
        st.error(f"Could not reach API: {e}")
        st.stop()
        return {}

    if not patients:
        st.warning("No patients found. Please add a patient first.")
        st.stop()

    return {f"{p['name']} ({p['id'][:4]})": p["id"] for p in patients}

def _api_error(e: requests.HTTPError) -> None:
    try:
        detail = e.response.json().get("detail", str(e))
    except Exception:
        detail = str(e)
    st.error(f"API error: {detail}")

def run_pediatric_system():
    # Override default Streamlit alerts with custom CSS
    st.success = custom_success
    st.error = custom_error
    st.warning = custom_warning

    # --- Global CSS ---
    st.markdown("""
    <style>
        div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
            background-color: #ff4b4b !important;
            color: white !important;
            border: none !important;
        }
        div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover {
            background-color: #ff1f1f !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏥 M3 - Pediatric Clinical Data System")
    st.markdown("---")

    MENU_OPTIONS = [
        "Add Patient",
        "Add Growth Record",
        "Add Immunization",
        "Add Milestone",
        "View Patients",
        "View Patient Details",
        "View Alerts",
    ]

    if "menu" not in st.session_state:
        st.session_state.menu = "Add Patient"

    # ADD THESE LINES
    menu = st.pills(
        "Module Navigation",
        MENU_OPTIONS,
        default=st.session_state.menu,
        label_visibility="collapsed"
    )

    if menu:
        st.session_state.menu = menu

    # ══════════════════════════════════════════════════════════════════════════════
    if menu == "Add Patient":
        st.header("👶 Add New Pediatric Patient")

        col1, col2 = st.columns(2)
        with col1:
            name   = st.text_input("Child Name")
            gender = st.selectbox("Gender", ["Male", "Female"])
        with col2:
            dob = st.date_input("Date of Birth")

        if st.button("Save Patient", type="primary"):
            if not name.strip():
                st.error("Patient name cannot be empty.")
            else:
                try:
                    patient = api.create_patient(name.strip(), dob, gender)
                    st.success(
                        f"✅ Patient **{patient['name']}** created "
                        f"(age: {patient['age_months']} months)"
                    )
                except requests.HTTPError as e:
                    _api_error(e)
                except requests.RequestException as e:
                    st.error(f"Could not reach API: {e}")

    # ══════════════════════════════════════════════════════════════════════════════
    elif menu == "Add Growth Record":
        st.header("📈 Add Growth Measurement")
        patient_dict = _load_patient_dict()

        selected_name    = st.selectbox("Select Patient", list(patient_dict.keys()))
        selected_patient = patient_dict[selected_name]

        weight = st.number_input("Weight (kg)", min_value=0.1, step=0.1, format="%.1f")
        height = st.number_input("Height (cm)", min_value=1.0,  step=0.5, format="%.1f")

        if st.button("Save Growth Record", type="primary"):
            try:
                record = api.create_growth_record(selected_patient, weight, height)
                st.success("Growth record added successfully.")

                st.subheader("📊 Growth Analysis")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Weight (kg)", record["weight"])
                c2.metric("Height (cm)", record["height"])
                c3.metric("BMI",         record["bmi"])
                c4.metric("Percentile",  f"{record['percentile']}th")

                st.markdown(f"**BMI Status:** {record['bmi_status']}")
                st.markdown(f"**Weight Status:** {record['weight_status']}")
                st.markdown(f"**Height Status:** {record['height_status']}")

                st.subheader("🩺 Doctor Recommendations")
                for rec in record["recommendations"]:
                    st.warning(rec)

            except requests.HTTPError as e:
                _api_error(e)
            except requests.RequestException as e:
                st.error(f"Could not reach API: {e}")

    # ══════════════════════════════════════════════════════════════════════════════
    elif menu == "Add Immunization":
        st.header("💉 Add Immunization Record")
        patient_dict = _load_patient_dict()

        selected_name    = st.selectbox("Select Patient", list(patient_dict.keys()))
        selected_patient = patient_dict[selected_name]

        vaccine_name   = st.text_input("Vaccine Name")
        scheduled_date = st.date_input("Scheduled Date")

        if st.button("Save Immunization", type="primary"):
            if not vaccine_name.strip():
                st.error("Please enter the vaccine name.")
            else:
                try:
                    record = api.create_immunization_record(
                        selected_patient, vaccine_name.strip(), scheduled_date
                    )
                    if record["delayed"]:
                        st.warning(
                            f"⚠ **{record['vaccine_name']}** is overdue "
                            f"(scheduled: {record['scheduled_date']}) — alert raised."
                        )
                    else:
                        st.success("Immunization record added successfully.")

                except requests.HTTPError as e:
                    _api_error(e)
                except requests.RequestException as e:
                    st.error(f"Could not reach API: {e}")

    # ══════════════════════════════════════════════════════════════════════════════
    elif menu == "Add Milestone":
        st.header("🏆 Add Developmental Milestone")
        patient_dict = _load_patient_dict()

        selected_name    = st.selectbox("Select Patient", list(patient_dict.keys()))
        selected_patient = patient_dict[selected_name]

        milestone_name = st.text_input("Milestone Name")
        expected_age   = st.number_input("Expected Age (Months)", min_value=0, step=1)
        achieved_age   = st.number_input("Achieved Age (Months)", min_value=0, step=1)

        if st.button("Save Milestone", type="primary"):
            if not milestone_name.strip():
                st.error("Please enter the milestone name.")
            else:
                try:
                    record = api.create_milestone_record(
                        selected_patient,
                        milestone_name.strip(),
                        int(expected_age),
                        int(achieved_age),
                    )
                    if record["delayed"]:
                        lag = record["achieved_age"] - record["expected_age"]
                        st.warning(
                            f"⚠ **{record['milestone_name']}** achieved "
                            f"{lag} month(s) late — alert raised."
                        )
                    else:
                        st.success("Milestone saved successfully.")

                except requests.HTTPError as e:
                    _api_error(e)
                except requests.RequestException as e:
                    st.error(f"Could not reach API: {e}")

    # ══════════════════════════════════════════════════════════════════════════════
    elif menu == "View Patients":
        st.header("📋 Patient Records")

        try:
            patients = api.get_all_patients()
        except requests.RequestException as e:
            st.error(f"Could not reach API: {e}")
            st.stop()

        if not patients:
            st.warning("No patients found.")
        else:
            h1, h2, h3, h4, h5, h6 = st.columns([2, 2, 2, 2, 2, 1])
            h1.write("**Name**")
            h2.write("**DOB**")
            h3.write("**Gender**")
            h4.write("**Age (Months)**")
            h5.write("**Created At**")
            h6.write("**Delete**")
            st.markdown("---")

            for p in patients:
                c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 1])

                if c1.button(p["name"], key=f"name_{p['id']}"):
                    st.session_state.selected_patient_id = p["id"]
                    st.session_state.menu = "View Patient Details"
                    st.rerun()

                c2.write(p["dob"])
                c3.write(p["gender"])
                c4.write(p["age_months"])
                c5.write(p["created_at"][:10])

                if c6.button("🗑", key=f"del_{p['id']}", type="primary"):
                    try:
                        result = api.delete_patient(p["id"])
                        st.success(result["message"])
                        st.rerun()
                    except requests.HTTPError as e:
                        _api_error(e)
                    except requests.RequestException as e:
                        st.error(f"Could not reach API: {e}")

    # ══════════════════════════════════════════════════════════════════════════════
    elif menu == "View Patient Details":
        st.header("📝 Patient Complete Record")

        if "selected_patient_id" in st.session_state:
            selected_patient_id = st.session_state["selected_patient_id"]
        else:
            patient_dict = _load_patient_dict()
            selected_name       = st.selectbox("Select Patient", list(patient_dict.keys()))
            selected_patient_id = patient_dict[selected_name]

        try:
            patient = api.get_patient(selected_patient_id)
        except requests.HTTPError:
            st.error("Patient not found.")
            st.stop()
        except requests.RequestException as e:
            st.error(f"Could not reach API: {e}")
            st.stop()

        st.subheader("👤 Patient Profile")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👶 Name",         patient["name"])
        col2.metric("🧑 Gender",       patient["gender"])
        col3.metric("📅 Age (Months)", patient["age_months"])
        col4.metric("🎂 DOB",          patient["dob"])

        st.markdown("---")

        try:
            growth_records       = api.get_growth_records(selected_patient_id)
            immunization_records = api.get_immunization_records(selected_patient_id)
            milestone_records    = api.get_milestone_records(selected_patient_id)
        except requests.RequestException as e:
            st.error(f"Could not fetch records: {e}")
            st.stop()

        imm_delays = [r for r in immunization_records if r["delayed"]]
        ms_delays  = [r for r in milestone_records    if r["delayed"]]
        total      = len(imm_delays) + len(ms_delays)

        if total:
            st.error(f"⚠ {total} Health Alert(s) Detected")
        else:
            st.success("✅ No Health Alerts")

        st.markdown("---")

        st.subheader("📈 Growth Records")
        if growth_records:
            for g in growth_records:
                if g["weight_status"] == "Underweight":
                    st.warning(f"⚠ Underweight detected on {g['recorded_at'][:10]}")

            display = [{
                "Recorded At":     r["recorded_at"][:10],
                "Weight (kg)":     r["weight"],
                "Height (cm)":     r["height"],
                "BMI":             r["bmi"],
                "BMI Status":      r["bmi_status"],
                "Weight Status":   r["weight_status"],
                "Height Status":   r["height_status"],
                "Percentile":      r["percentile"],
                "Recommendations": ", ".join(r["recommendations"]),
            } for r in growth_records]
            st.dataframe(display, use_container_width=True)
        else:
            st.info("No growth records found.")

        st.markdown("---")

        st.subheader("💉 Immunization Records")
        if immunization_records:
            display = [{
                "Vaccine Name":   r["vaccine_name"],
                "Scheduled Date": r["scheduled_date"],
                "Delayed":        "Yes" if r["delayed"] else "No",
                "Created At":     r["created_at"][:10],
            } for r in immunization_records]
            st.dataframe(display, use_container_width=True)
        else:
            st.info("No immunization records found.")

        st.markdown("---")

        st.subheader("🏆 Milestone Records")
        if milestone_records:
            display = [{
                "Milestone":     r["milestone_name"],
                "Expected (mo)": r["expected_age"],
                "Achieved (mo)": r["achieved_age"],
                "Delayed":       "Yes" if r["delayed"] else "No",
                "Created At":    r["created_at"][:10],
            } for r in milestone_records]
            st.dataframe(display, use_container_width=True)
        else:
            st.info("No milestone records found.")

        st.markdown("---")

        st.subheader("⚠️ Immunization Delays")
        if imm_delays:
            h1, h2, h3, h4 = st.columns([3, 3, 2, 1])
            h1.write("**Vaccine Name**")
            h2.write("**Scheduled Date**")
            h3.write("**Status**")
            h4.write("**Action**")
            st.markdown("---")

            for r in imm_delays:
                c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
                c1.write(r["vaccine_name"])
                c2.write(r["scheduled_date"])
                c3.markdown("🔴 **Active**")

                if c4.button("Resolve", key=f"imm_{r['id']}", type="primary"):
                    try:
                        result = api.resolve_immunization(r["id"])
                        st.success(result["message"])
                        st.rerun()
                    except requests.HTTPError as e:
                        _api_error(e)
        else:
            st.success("No immunization delays.")

        st.markdown("---")

        st.subheader("⚠️ Milestone Delays")
        if ms_delays:
            h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
            h1.write("**Milestone Name**")
            h2.write("**Expected (mo)**")
            h3.write("**Achieved (mo)**")
            h4.write("**Status**")
            h5.write("**Action**")
            st.markdown("---")

            for r in ms_delays:
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                c1.write(r["milestone_name"])
                c2.write(f"{r['expected_age']} mo")
                c3.write(f"{r['achieved_age']} mo")
                c4.markdown("🔴 **Delayed**")

                if c5.button("Resolve", key=f"ms_{r['id']}", type="primary"):
                    try:
                        result = api.resolve_milestone(r["id"])
                        st.success(result["message"])
                        st.rerun()
                    except requests.HTTPError as e:
                        _api_error(e)
        else:
            st.success("No milestone delays.")

        if st.button("⬅ Back to Patients", type="primary"):
            st.session_state.pop("selected_patient_id", None)
            st.session_state.menu = "View Patients"
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════════
    elif menu == "View Alerts":
        st.header("🚨 Generated Alerts")

        try:
            alerts = api.get_all_alerts()
        except requests.RequestException as e:
            st.error(f"Could not reach API: {e}")
            st.stop()

        if alerts:
            display = [{
                "Patient Name":   a["patient_name"],
                "Alert Type":     a["alert_type"],
                "Detail":         a["detail"],
                "Scheduled Date": a["scheduled_date"],
            } for a in alerts]
            st.dataframe(display, use_container_width=True)
        else:
            st.success("✅ No Active Alerts")