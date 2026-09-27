from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.users import User
from app.models.documents import Document
from app.models.land_records import LandRecord
from app.models.validation import ValidationResult
from app.models.audit import AuditLog
from app.core.security import get_password_hash
import datetime

def seed_database():
    # 1. Initialize tables
    init_db()
    
    db = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).filter(User.username == "revenue_officer").first():
            print("Database users exist. Checking land records...")
            if db.query(LandRecord).count() >= 5:
                print("Government Database records already present. Skipping.")
                return

        print("Seeding database with Official Government Cadastral Registry...")

        # 2. Seed Users
        if not db.query(User).filter(User.username == "revenue_officer").first():
            officer = User(
                username="revenue_officer",
                email="officer@revenue.gov.in",
                hashed_password=get_password_hash("sih2026password"),
                role="Official",
                is_active=True
            )
            admin = User(
                username="admin_sih",
                email="admin@revenue.gov.in",
                hashed_password=get_password_hash("sih2026admin"),
                role="Admin",
                is_active=True
            )
            db.add(officer)
            db.add(admin)
            db.flush()

        # 3. Official Government Land Registry Records
        records = [
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

        for r_data in records:
            existing = db.query(LandRecord).filter(
                LandRecord.survey_number == r_data['survey_number'],
                LandRecord.village == r_data['village']
            ).first()
            if not existing:
                rec = LandRecord(**r_data)
                db.add(rec)

        db.commit()
        print("Government Database seeded with official verified records successfully.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
