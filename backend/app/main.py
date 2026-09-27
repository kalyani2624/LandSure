import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.session import init_db, SessionLocal
from app.api import api_router
from app.models.users import User
from app.core.dependencies import get_password_hash

# Initialize database schema tables
init_db()

def seed_default_users():
    """Ensure default official users exist in database on startup."""
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "revenue_officer").first():
            officer = User(
                username="revenue_officer",
                email="officer@revenue.gov.in",
                hashed_password=get_password_hash("sih2026password"),
                role="Official",
                is_active=True
            )
            db.add(officer)

        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@revenue.gov.in",
                hashed_password=get_password_hash("sih2026admin"),
                role="Admin",
                is_active=True
            )
            db.add(admin)

        if not db.query(User).filter(User.username == "admin_sih").first():
            admin_sih = User(
                username="admin_sih",
                email="admin_sih@revenue.gov.in",
                hashed_password=get_password_hash("sih2026admin"),
                role="Admin",
                is_active=True
            )
            db.add(admin_sih)

        db.commit()
    except Exception as e:
        print(f"Error auto-seeding users: {e}")
        db.rollback()
    finally:
        db.close()

def seed_default_land_records():
    """Ensure the 5 Official Government Cadastral Baseline Records are always present in database on startup."""
    from app.models.land_records import LandRecord
    from app.models.documents import Document
    db = SessionLocal()
    try:
        baseline_records = [
            {
                'owner_name': 'Devansh Kanubhai Patel',
                'father_name': 'Kanubhai Patel',
                'survey_number': '123/4',
                'khasra_number': '123/4',
                'khata_number': 'GJ-398',
                'plot_number': '45',
                'area': 120.0,
                'area_unit': 'Sq. Meters',
                'village': 'Athwa',
                'tehsil_mandal': 'Kamrej',
                'district': 'Surat',
                'land_classification': 'Residential / Non-Agricultural',
                'ownership_type': 'Pattadar / Self-owned',
                'registration_number': 'GJ 398765',
                'registration_date': '2024-01-05',
                'verification_status': 'Verified'
            },
            {
                'owner_name': 'Amol Ashok Deshmukh',
                'father_name': 'Ashok Deshmukh',
                'survey_number': '123',
                'khasra_number': 'Gat 123',
                'khata_number': 'MH-812',
                'plot_number': '101',
                'area': 1000.0,
                'area_unit': 'Sq. Meters',
                'village': 'Talmavale',
                'tehsil_mandal': 'Karad',
                'district': 'Satara',
                'land_classification': 'Agricultural / Non-Agricultural Land',
                'ownership_type': 'Pattadar / Sole Owner',
                'registration_number': 'MA 812345',
                'registration_date': '2024-06-01',
                'verification_status': 'Verified'
            },
            {
                'owner_name': 'Ravindra Hegde',
                'father_name': 'Hegde',
                'survey_number': '123/4',
                'khasra_number': 'Site 123/4',
                'khata_number': '4567',
                'plot_number': 'Site 123/4',
                'area': 2400.0,
                'area_unit': 'Sq. Feet',
                'village': 'Jayanagar',
                'tehsil_mandal': 'Bengaluru South',
                'district': 'Bengaluru',
                'land_classification': 'Residential / Urban Property',
                'ownership_type': 'Sole Owner / Self-owned',
                'registration_number': 'KA 684512',
                'registration_date': '2024-04-20',
                'verification_status': 'Verified'
            },
            {
                'owner_name': 'Mutyala Narasimhulu',
                'father_name': 'Mutyala Subbarayudu',
                'survey_number': '224/2B',
                'khasra_number': '224/2B',
                'khata_number': '578',
                'plot_number': 'Plot 2',
                'area': 3.15,
                'area_unit': 'Acres',
                'village': 'Velagapudi',
                'tehsil_mandal': 'Eluru',
                'district': 'West Godavari',
                'land_classification': 'Agricultural Land (వ్యవసాయ భూమి)',
                'ownership_type': 'Pattadar / Sole Owner',
                'registration_number': 'DU 478965',
                'registration_date': '2023-07-18',
                'verification_status': 'Verified'
            },
            {
                'owner_name': 'Ramkishor Yadav',
                'father_name': 'Badri Prasad Yadav',
                'survey_number': '89/2',
                'khasra_number': '89/2',
                'khata_number': '275',
                'plot_number': 'Plot 1',
                'area': 0.86,
                'area_unit': 'Hectares',
                'village': 'Dharampur',
                'tehsil_mandal': 'Sahjanwa',
                'district': 'Gorakhpur',
                'land_classification': 'Agricultural Irrigated (कृषि सिंचित)',
                'ownership_type': 'Pattadar / Khatedar',
                'registration_number': 'AP 896512',
                'registration_date': '2024-04-12',
                'verification_status': 'Verified'
            }
        ]

        for r_data in baseline_records:
            existing = db.query(LandRecord).filter(
                (LandRecord.survey_number == r_data['survey_number']) &
                ((LandRecord.village == r_data['village']) | (LandRecord.registration_number == r_data['registration_number']))
            ).first()
            if not existing:
                rec = LandRecord(**r_data)
                db.add(rec)

        db.commit()
    except Exception as e:
        print(f"Error auto-seeding baseline land records: {e}")
        db.rollback()
    finally:
        db.close()

# Auto-seed users and official government land records on initialization
seed_default_users()
seed_default_land_records()

app = FastAPI(
    title="LandSure AI - Land Record Digitization & Validation API",
    description="SIH26018 Production-Ready Multilingual Land Records Digitization Backend Services",
    version="2.0.0"
)

import traceback
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    err_tb = traceback.format_exc()
    print("GLOBAL UNCAUGHT EXCEPTION:", err_tb)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_message": str(exc), "traceback": err_tb}
    )

# Robust Production CORS Configuration for Vercel, Render & Localhost
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://sih-26018-land-digitization.vercel.app",
        "https://sih26018-land-digitization.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files for serving original and preprocessed images securely
uploads_abs_path = os.path.abspath(settings.UPLOAD_DIR)
preprocessed_abs_path = os.path.abspath(settings.PREPROCESSED_DIR)

os.makedirs(uploads_abs_path, exist_ok=True)
os.makedirs(preprocessed_abs_path, exist_ok=True)

app.mount("/static/uploads", StaticFiles(directory=uploads_abs_path), name="uploads")
app.mount("/static/preprocessed", StaticFiles(directory=preprocessed_abs_path), name="preprocessed")

# Register API Router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "Healthy",
        "service": "LandSure AI Land Record Digitization API",
        "version": "2.0.0",
        "docs": "/docs"
    }
