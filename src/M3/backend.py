
from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.M3.db import get_database
from src.M3.models import (
    PatientCreate, PatientResponse,
    GrowthCreate, GrowthResponse,
    ImmunizationCreate, ImmunizationResponse,
    MilestoneCreate, MilestoneResponse,
    AlertItem, AlertsResponse,
    MessageResponse,
)

from src.M3.services import (
    calculate_age_in_months,
    calculate_growth_percentile,
    check_who_growth,
    calculate_bmi,
    generate_recommendation,
    check_immunization_delay,
    check_milestone_delay,
)

app = FastAPI(
    title="M3 Pediatric Clinical API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = get_database()

patients_col = db["patients"]
growth_col = db["growth"]
immunization_col = db["immunization"]
milestone_col = db["milestones"]
alert_col = db["alerts"]

def oid(id_str: str):
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/patients", response_model=list[PatientResponse])
def get_patients():
    docs = list(patients_col.find().sort("created_at", -1))
    return [{
        "id": str(d["_id"]),
        "name": d["name"],
        "dob": d["dob"],
        "gender": d["gender"],
        "age_months": d["age_months"],
        "created_at": d["created_at"]
    } for d in docs]

@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str):
    d = patients_col.find_one({"_id": oid(patient_id)})
    if not d:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "id": str(d["_id"]),
        "name": d["name"],
        "dob": d["dob"],
        "gender": d["gender"],
        "age_months": d["age_months"],
        "created_at": d["created_at"]
    }

@app.post("/patients", response_model=PatientResponse, status_code=201)
def create_patient(body: PatientCreate):
    age_months = calculate_age_in_months(body.dob)

    doc = {
        "name": body.name,
        "dob": body.dob.strftime("%Y-%m-%d"),
        "gender": body.gender,
        "age_months": age_months,
        "created_at": datetime.now()
    }

    result = patients_col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "dob": doc["dob"],
        "gender": doc["gender"],
        "age_months": doc["age_months"],
        "created_at": doc["created_at"]
    }

@app.delete("/patients/{patient_id}", response_model=MessageResponse)
def delete_patient(patient_id: str):
    if not patients_col.find_one({"_id": oid(patient_id)}):
        raise HTTPException(status_code=404, detail="Patient not found")

    patients_col.delete_one({"_id": oid(patient_id)})
    growth_col.delete_many({"patient_id": oid(patient_id)})
    immunization_col.delete_many({"patient_id": oid(patient_id)})
    milestone_col.delete_many({"patient_id": oid(patient_id)})

    return {"message": "Patient deleted"}

@app.post("/growth", response_model=GrowthResponse)
def create_growth(body: GrowthCreate):
    patient = patients_col.find_one({"_id": oid(body.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    bmi, bmi_status = calculate_bmi(body.weight, body.height)
    percentile = calculate_growth_percentile(body.weight, body.height)
    weight_status, height_status = check_who_growth(
        patient["age_months"], body.weight, body.height
    )

    recs = generate_recommendation(weight_status, height_status, bmi_status)

    doc = {
        "patient_id": oid(body.patient_id),
        "weight": body.weight,
        "height": body.height,
        "bmi": bmi,
        "bmi_status": bmi_status,
        "weight_status": weight_status,
        "height_status": height_status,
        "percentile": percentile,
        "recommendations": recs,
        "recorded_at": datetime.now()
    }

    result = growth_col.insert_one(doc)
    
    doc["id"] = str(doc.pop("_id"))
    doc["patient_id"] = body.patient_id
    doc["patient_name"] = patient["name"]

    return doc

@app.get("/growth/{patient_id}")
def get_growth(patient_id: str):
    patient = patients_col.find_one({"_id": oid(patient_id)})
    p_name = patient["name"] if patient else "Unknown"

    docs = list(growth_col.find({"patient_id": oid(patient_id)}))
    for d in docs:
        d["id"] = str(d.pop("_id"))  
        d["patient_id"] = str(d["patient_id"])
        d["patient_name"] = p_name
    return docs

@app.post("/immunization", response_model=ImmunizationResponse)
def create_immunization(body: ImmunizationCreate):
    patient = patients_col.find_one({"_id": oid(body.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    delayed = check_immunization_delay(body.scheduled_date)

    doc = {
        "patient_id": oid(body.patient_id),
        "vaccine_name": body.vaccine_name,
        "scheduled_date": body.scheduled_date.isoformat(),
        "delayed": delayed,
        "created_at": datetime.now()
    }

    result = immunization_col.insert_one(doc)
    
    doc["id"] = str(doc.pop("_id"))
    doc["patient_id"] = body.patient_id
    doc["patient_name"] = patient["name"]

    return doc

@app.get("/immunization/{patient_id}")
def get_immunization(patient_id: str):
    patient = patients_col.find_one({"_id": oid(patient_id)})
    p_name = patient["name"] if patient else "Unknown"

    docs = list(immunization_col.find({"patient_id": oid(patient_id)}))
    for d in docs:
        d["id"] = str(d.pop("_id")) 
        d["patient_id"] = str(d["patient_id"])
        d["patient_name"] = p_name
    return docs

@app.patch("/immunization/{record_id}/resolve", response_model=MessageResponse)
def resolve_immunization(record_id: str):
    result = immunization_col.update_one(
        {"_id": oid(record_id)},
        {"$set": {"delayed": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Immunization record not found")
    
    return {"message": "Immunization delay resolved."}

@app.post("/milestones", response_model=MilestoneResponse)
def create_milestone(body: MilestoneCreate):
    patient = patients_col.find_one({"_id": oid(body.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    delayed = check_milestone_delay(body.expected_age, body.achieved_age)

    doc = {
        "patient_id": oid(body.patient_id),
        "milestone_name": body.milestone_name,
        "expected_age": body.expected_age,
        "achieved_age": body.achieved_age,
        "delayed": delayed,
        "created_at": datetime.now()
    }

    result = milestone_col.insert_one(doc)
    
    doc["id"] = str(doc.pop("_id"))
    doc["patient_id"] = body.patient_id
    doc["patient_name"] = patient["name"]

    return doc

@app.get("/milestones/{patient_id}")
def get_milestones(patient_id: str):
    patient = patients_col.find_one({"_id": oid(patient_id)})
    p_name = patient["name"] if patient else "Unknown"

    docs = list(milestone_col.find({"patient_id": oid(patient_id)}))
    for d in docs:
        d["id"] = str(d.pop("_id")) 
        d["patient_id"] = str(d["patient_id"])
        d["patient_name"] = p_name
    return docs

@app.patch("/milestones/{record_id}/resolve", response_model=MessageResponse)
def resolve_milestone(record_id: str):
    result = milestone_col.update_one(
        {"_id": oid(record_id)},
        {"$set": {"delayed": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Milestone record not found")
    
    return {"message": "Milestone delay resolved."}

@app.get("/alerts", response_model=AlertsResponse)
def get_alerts():
    alerts = []

    for rec in immunization_col.find({"delayed": True}):
        patient = patients_col.find_one({"_id": rec["patient_id"]})

        alerts.append(AlertItem(
            patient_name=patient["name"] if patient else "Unknown",
            alert_type="Immunization Delay",
            detail=rec["vaccine_name"],
            scheduled_date=rec["scheduled_date"]
        ))

    return AlertsResponse(alerts=alerts)