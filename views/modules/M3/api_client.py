
from datetime import date
import requests
import os

BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "streamlit-client"
}

TIMEOUT = 60

session = requests.Session()
session.headers.update(HEADERS)

def _get(path: str) -> dict | list:
    r = session.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def _post(path: str, payload: dict) -> dict:
    r = session.post(f"{BASE_URL}{path}", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def _patch(path: str) -> dict:
    r = session.patch(f"{BASE_URL}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def _delete(path: str) -> dict:
    r = session.delete(f"{BASE_URL}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def get_all_patients() -> list[dict]:
    return _get("/patients")

def get_patient(patient_id: str) -> dict:
    return _get(f"/patients/{patient_id}")

def create_patient(name: str, dob: date, gender: str) -> dict:
    return _post("/patients", {
        "name": name,
        "dob": dob.isoformat(),
        "gender": gender,
    })

def delete_patient(patient_id: str) -> dict:
    return _delete(f"/patients/{patient_id}")

def get_growth_records(patient_id: str) -> list[dict]:
    return _get(f"/growth/{patient_id}")

def create_growth_record(patient_id: str, weight: float, height: float) -> dict:
    return _post("/growth", {
        "patient_id": patient_id,
        "weight": weight,
        "height": height,
    })

def get_immunization_records(patient_id: str) -> list[dict]:
    return _get(f"/immunization/{patient_id}")

def create_immunization_record(patient_id: str, vaccine_name: str, scheduled_date: date) -> dict:
    return _post("/immunization", {
        "patient_id": patient_id,
        "vaccine_name": vaccine_name,
        "scheduled_date": scheduled_date.isoformat(),
    })

def resolve_immunization(record_id: str) -> dict:
    return _patch(f"/immunization/{record_id}/resolve")

def get_milestone_records(patient_id: str) -> list[dict]:
    return _get(f"/milestones/{patient_id}")

def create_milestone_record(patient_id: str, milestone_name: str, expected_age: int, achieved_age: int) -> dict:
    return _post("/milestones", {
        "patient_id": patient_id,
        "milestone_name": milestone_name,
        "expected_age": expected_age,
        "achieved_age": achieved_age,
    })

def resolve_milestone(record_id: str) -> dict:
    return _patch(f"/milestones/{record_id}/resolve")

def get_all_alerts() -> list[dict]:
    data = _get("/alerts")
    return data.get("alerts", [])