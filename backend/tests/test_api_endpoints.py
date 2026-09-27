import pytest
import httpx
from app.main import app
from app.core.security import create_access_token
from app.database.session import SessionLocal, init_db
from app.models.users import User
from app.models.documents import Document
from app.core.security import get_password_hash

@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    init_db()
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test_officer").first()
    if not user:
        user = User(
            username="test_officer",
            email="test_officer@gov.in",
            hashed_password=get_password_hash("testpassword123"),
            role="Official",
            is_active=True
        )
        db.add(user)
        db.commit()
        
    doc = db.query(Document).filter(Document.id == 1).first()
    if not doc:
        doc = Document(
            id=1,
            original_filename="sample_test_doc.jpg",
            file_path="sample_documents/telugu_adangal_sample.jpg",
            status="Verified",
            language="Telugu",
            confidence_score=92.0,
            processing_stage="COMPLETED",
            ocr_text="పట్టాదారు పేరు: కొండ్రు రాము\nసర్వే నంబరు: 124/2A"
        )
        db.add(doc)
        db.commit()
    db.close()

@pytest.mark.anyio
async def test_root_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Healthy"
        assert "BhoomiSetu" in data["service"]

@pytest.mark.anyio
async def test_auth_login_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": "test_officer", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.anyio
async def test_dashboard_stats_endpoint():
    token = create_access_token(data={"sub": "test_officer", "role": "Official", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/dashboard/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "status_distribution" in data

@pytest.mark.anyio
async def test_verification_queue_endpoint():
    token = create_access_token(data={"sub": "test_officer", "role": "Official", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/verification/list", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.anyio
async def test_extraction_debug_endpoint():
    token = create_access_token(data={"sub": "test_officer", "role": "Official", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/documents/1/extraction-debug", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == 1
        assert "raw_ocr" in data
        assert "language" in data
        assert "validation" in data
