from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime, os

DATABASE_URL = "sqlite:///./reminders.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_data(db):
    from models import Patient, PatientHistory, Appointment

    now = datetime.datetime.utcnow()

    patients_data = [
        {"name": "Margaret Ellis",   "age": 72, "phone": "+1-555-0101", "email": "m.ellis@email.com"},
        {"name": "Carlos Rivera",    "age": 34, "phone": "+1-555-0102", "email": "c.rivera@email.com"},
        {"name": "Lily Nguyen",      "age": 15, "phone": "+1-555-0103", "email": "nguyen.family@email.com"},
        {"name": "David Okafor",     "age": 58, "phone": "+1-555-0104", "email": "d.okafor@email.com"},
        {"name": "Sarah Thompson",   "age": 41, "phone": "+1-555-0105", "email": "s.thompson@email.com"},
        {"name": "James Whitfield",  "age": 65, "phone": "+1-555-0106", "email": "j.whitfield@email.com"},
        {"name": "Priya Sharma",     "age": 29, "phone": "+1-555-0107", "email": "p.sharma@email.com"},
        {"name": "Robert Chen",      "age": 82, "phone": "+1-555-0108", "email": "r.chen@email.com"},
        {"name": "Emily Watson",     "age": 24, "phone": "+1-555-0109", "email": "e.watson@email.com"},
        {"name": "Michael Brown",    "age": 71, "phone": "+1-555-0110", "email": "m.brown@email.com"},
        {"name": "Aisha Patel",      "age": 45, "phone": "+1-555-0111", "email": "a.patel@email.com"},
        {"name": "William Martinez", "age": 52, "phone": "+1-555-0112", "email": "w.martinez@email.com"},
        {"name": "Chloe Smith",      "age": 8,  "phone": "+1-555-0113", "email": "smith.family@email.com"},
    ]

    histories_data = [
        {"total_visits": 12, "no_show_count": 1, "missed_last_appointment": True,  "no_show_risk": 75.0},
        {"total_visits": 5,  "no_show_count": 0, "missed_last_appointment": False, "no_show_risk": 10.0},
        {"total_visits": 0,  "no_show_count": 0, "missed_last_appointment": False, "no_show_risk": 20.0},
        {"total_visits": 8,  "no_show_count": 3, "missed_last_appointment": True,  "no_show_risk": 88.0},
        {"total_visits": 3,  "no_show_count": 0, "missed_last_appointment": False, "no_show_risk": 15.0},
        {"total_visits": 20, "no_show_count": 2, "missed_last_appointment": False, "no_show_risk": 60.0},
        {"total_visits": 1,  "no_show_count": 0, "missed_last_appointment": False, "no_show_risk": 5.0},
        {"total_visits": 15, "no_show_count": 4, "missed_last_appointment": True,  "no_show_risk": 92.0},
        {"total_visits": 4,  "no_show_count": 0, "missed_last_appointment": False, "no_show_risk": 12.0},
        {"total_visits": 18, "no_show_count": 3, "missed_last_appointment": True,  "no_show_risk": 85.0},
        {"total_visits": 9,  "no_show_count": 1, "missed_last_appointment": False, "no_show_risk": 30.0},
        {"total_visits": 2,  "no_show_count": 1, "missed_last_appointment": True,  "no_show_risk": 65.0},
        {"total_visits": 6,  "no_show_count": 0, "missed_last_appointment": False, "no_show_risk": 8.0},
    ]

    appointments_data = [
        {"type": "Cardiology Visit",        "days": 1},
        {"type": "General Checkup",         "days": 3},
        {"type": "Pediatric Visit",         "days": 2},
        {"type": "Surgery Consultation",    "days": 5},
        {"type": "Routine Follow-up",       "days": 2},
        {"type": "Mental Health Session",   "days": 4},
        {"type": "Telemedicine",            "days": 7},
        {"type": "Cancer Treatment",        "days": 1},
        {"type": "Dental Checkup",          "days": 3},
        {"type": "Orthopedic Follow-up",    "days": 2},
        {"type": "Neurology Consultation",  "days": 6},
        {"type": "Dermatology Visit",       "days": 4},
        {"type": "Vaccination",             "days": 1},
    ]

    for i, p in enumerate(patients_data):
        existing_patient = db.query(Patient).filter(Patient.name == p["name"]).first()
        if not existing_patient:
            patient = Patient(**p)
            db.add(patient)
            db.flush()

            h = histories_data[i]
            history = PatientHistory(patient_id=patient.id, **h)
            db.add(history)

            a = appointments_data[i]
            appt_dt = now + datetime.timedelta(days=a["days"])
            appointment = Appointment(
                patient_id=patient.id,
                appointment_type=a["type"],
                appointment_datetime=appt_dt,
                status="SCHEDULED",
            )
            db.add(appointment)

    db.commit()


if __name__ == "__main__":
    print("Seeding database...")
    db = SessionLocal()
    try:
        seed_data(db)
        print("Database seeding completed successfully.")
    finally:
        db.close()
