# Pediatric Clinical Data Management System (M3)

## Overview

The **Pediatric Clinical Data Management System (Module M3)** is a backend-driven healthcare system designed to manage, process, and analyze pediatric clinical data.

This module is part of a larger modular healthcare architecture and is responsible for:

* Tracking pediatric growth (height, weight, BMI)
* Monitoring immunization schedules
* Tracking developmental milestones
* Generating alerts for delays or abnormalities
* Providing processed data to other modules (M19, M28)

---

# System Architecture

## High-Level Architecture

```text
M1 (Patient Demographics)
        ↓
M3 Backend (FastAPI)
        ↓
MongoDB Atlas
        ↓
Processed Data (Alerts / Summary)
        ↓
M19 & M28 Modules
```

---

## Runtime Architecture

```text
Streamlit Frontend
        ↓ (HTTP Requests)
API Client (requests)
        ↓
FastAPI Backend
        ↓
MongoDB Atlas
```

---

## Key Insight

Unlike simple Streamlit apps:

✔ This project uses **real REST APIs (FastAPI)**
✔ Frontend communicates using **HTTP requests**
✔ Backend is **decoupled from UI**

---

# Technologies Used

### Frontend

* Streamlit

### Backend

* FastAPI (Python)

### Database

* MongoDB Atlas

### Libraries

* PyMongo
* Requests
* Pydantic
* Datetime

---

# API Layer (Core of Project)

Your system exposes structured REST APIs.

## API Base URL

```text
https://m3-nx5f.onrender.com
```

---

# Patient APIs

### Get All Patients

```http
GET /patients
```

### Get Single Patient

```http
GET /patients/{patient_id}
```

### Create Patient

```http
POST /patients
```

Payload:

```json
{
  "name": "John",
  "dob": "2020-01-01",
  "gender": "Male"
}
```

---

### Delete Patient

```http
DELETE /patients/{patient_id}
```

---

# Growth APIs

### Create Growth Record

```http
POST /growth
```

Payload:

```json
{
  "patient_id": "id",
  "weight": 12.5,
  "height": 90
}
```

### Get Growth Records

```http
GET /growth/{patient_id}
```

---

# Immunization APIs

### Add Immunization

```http
POST /immunization
```

### Get Records

```http
GET /immunization/{patient_id}
```

### Resolve Delay

```http
PATCH /immunization/{record_id}/resolve
```

---

# Milestone APIs

### Add Milestone

```http
POST /milestones
```

### Get Milestones

```http
GET /milestones/{patient_id}
```

### Resolve Delay

```http
PATCH /milestones/{record_id}/resolve
```

---

# Alerts API

### Get All Alerts

```http
GET /alerts
```

---

# API Client (Frontend Integration)

The frontend does NOT directly access database.

Instead, it uses an API client:

```python
session.get("/patients")
session.post("/growth", payload)
```

Example from your client:

* `_get()` → fetch data
* `_post()` → insert data
* `_patch()` → update
* `_delete()` → delete

This mimics **real-world frontend-backend architecture**.



---

# Database Design

## Collections:

### Patients

* name
* dob
* gender
* age_months

### Growth

* weight, height
* BMI, percentile
* recommendations

### Immunization

* vaccine_name
* scheduled_date
* delayed flag

### Milestones

* milestone_name
* expected_age
* achieved_age
* delayed flag

### Alerts

* generated dynamically from delayed records

---

# Backend Logic

The backend performs:

### Growth Analysis

* BMI calculation
* Percentile calculation
* WHO growth validation
* Recommendations generation

### Immunization Tracking

* Delay detection
* Auto alert generation

### Milestone Tracking

* Delay detection

### Alert System

* Aggregates delayed cases
* Provides centralized alert endpoint

---

#  Installation & Setup

## 1. Clone Repo

```bash
git clone https://github.com/Chinmaya-R-Nayaka/Frontend
cd Frontend
```

---

## 2. Setup Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
cd src/M3
pip install -r requirements.txt
```

---

## 4. Setup Secrets

In src/M3 Create:

```
.env
```

```
MONGO_URI = "your_mongodb_connection_string"
```

---

## Run Backend

```bash
uvicorn src.M3.backend:app --reload
```

---

## Run Frontend

```bash
streamlit run app.py
```

---

# Deployment

* Backend → Render
* Frontend → Streamlit Cloud

### Important:

Set in Streamlit:

```
API_BASE_URL = " https://m3-nx5f.onrender.com"
```

---

# Challenges Faced

* MongoDB Atlas SSL errors
* Streamlit Cloud secret configuration
* API integration debugging
* CORS issues between frontend & backend

---

# Future Enhancements

* Authentication (JWT)
* Role-based access (Doctor/Admin)
* ML-based prediction
* Graph analytics dashboard
* Full microservices architecture

---

# Team Members

* Chinmaya R Nayaka
* Enos Baskey
* Chapineni Sujitha

---

