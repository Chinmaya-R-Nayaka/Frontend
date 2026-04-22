
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PatientCreate(BaseModel):
    name:   str
    dob:    date
    gender: str  # "Male" | "Female"

class PatientResponse(BaseModel):
    id:         str
    name:       str
    dob:        str
    gender:     str
    age_months: int
    created_at: datetime

class GrowthCreate(BaseModel):
    patient_id: str
    weight:     float = Field(..., gt=0)
    height:     float = Field(..., gt=0)

class GrowthResponse(BaseModel):
    id:              str
    patient_id:      str
    patient_name:    str
    weight:          float
    height:          float
    bmi:             float
    bmi_status:      str
    weight_status:   str
    height_status:   str
    percentile:      int
    recommendations: list[str]
    recorded_at:     datetime

class ImmunizationCreate(BaseModel):
    patient_id:     str
    vaccine_name:   str
    scheduled_date: date

class ImmunizationResponse(BaseModel):
    id:             str
    patient_id:     str
    patient_name:   str
    vaccine_name:   str
    scheduled_date: str
    delayed:        bool
    created_at:     datetime

class MilestoneCreate(BaseModel):
    patient_id:     str
    milestone_name: str
    expected_age:   int = Field(..., ge=0)
    achieved_age:   int = Field(..., ge=0)

class MilestoneResponse(BaseModel):
    id:             str
    patient_id:     str
    patient_name:   str
    milestone_name: str
    expected_age:   int
    achieved_age:   int
    delayed:        bool
    created_at:     datetime

class AlertItem(BaseModel):
    patient_name:   str
    alert_type:     str
    detail:         str
    scheduled_date: str

class AlertsResponse(BaseModel):
    alerts: list[AlertItem]

class MessageResponse(BaseModel):
    message: str

    