<div align="center">

# 🏛️ LandSure AI
### Intelligent Multilingual Land Record Digitization & Cadastral Validation Platform
**Smart India Hackathon (SIH) • Problem Statement SIH26018**

[![Live Portal](https://img.shields.io/badge/Live_Portal-landsure--tech.vercel.app-059669?style=for-the-badge&logo=vercel)](https://landsure-tech.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend_API-Render_Live-4F46E5?style=for-the-badge&logo=render)](https://sih26018-land-digitization.onrender.com)
[![API Docs](https://img.shields.io/badge/API_Docs-Swagger_UI-0284C7?style=for-the-badge&logo=fastapi)](https://sih26018-land-digitization.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

</div>

---

## 🌐 Live Production Deployments

| Component | Platform | URL |
| :--- | :--- | :--- |
| **Frontend Web Portal** | **Vercel** | [https://landsure-tech.vercel.app](https://landsure-tech.vercel.app) |
| **Backend REST API** | **Render** | [https://sih26018-land-digitization.onrender.com](https://sih26018-land-digitization.onrender.com) |
| **Interactive API Documentation** | **Swagger / OpenAPI** | [https://sih26018-land-digitization.onrender.com/docs](https://sih26018-land-digitization.onrender.com/docs) |
| **Alternative Frontend Mirror** | **Vercel** | [https://sih-26018-land-digitization.vercel.app](https://sih-26018-land-digitization.vercel.app) |

---

## 📌 Executive Summary & Problem Context

Historical and legacy Indian land records (Pattas, ROR-1B / Adangal extracts, Sale Deeds, Mutation registers, and Cadastral village survey sheets) are frequently preserved as physical paper archives or degraded scanned images in various **Indic languages** (Telugu, Tamil, Hindi, Kannada, Marathi, Gujarati, Odia, English).

**LandSure AI** provides an end-to-end, automated, and human-in-the-loop digitization pipeline aligning with the **Digital India Land Records Modernization Programme (DILRMP)** standards:
- **Computer Vision Preprocessing**: CLAHE contrast enhancement, deskewing, noise filtering, and adaptive thresholding binarization.
- **Multilingual Neural OCR**: Deep neural text recognition across 8 Indian languages and scripts.
- **19-Field Canonical Revenue Schema**: Automated extraction of critical cadastral attributes (Pattadar names, survey/khasra numbers, khata, plot, area extents, boundary extents, mutation references).
- **Rule-Based Anomaly Detection**: Real-time cross-referencing for area discrepancies, ownership conflicts, duplicate entries, and boundary integrity.
- **Interactive Verification Workspace**: Side-by-side verification console with native script overlays and single-click cryptographic sealing.
- **Cryptographic Land Certificates**: Automated PDF generation featuring digital revenue seals and SHA-256 integrity verification hashes.

---

## 🏗️ System Architecture & Workflow

```mermaid
flowchart TD
    A[Scanned Land Record / Deed] --> B[OpenCV Preprocessing & Deskew]
    B --> C[Language & Layout Classifier]
    C --> D[Indic OCR / Neural HTR Engine]
    D --> E[19 Canonical Field Extractor]
    E --> F[Cadastral Validation & Anomaly Engine]
    F --> G{Confidence >= 88% & No Anomalies?}
    G -- Yes --> H[Auto-Approved & Cryptographically Sealed]
    G -- No --> I[Human-in-the-Loop Review Queue]
    I --> J[Officer Verification Workspace]
    J --> K[Audit Trail & Historical Logging]
    K --> H
    H --> L[(Database Registry)]
    H --> M[Official Government Land Certificate PDF]
    H --> N[Public Registry Search]
```

---

## ⚡ Technology Stack

### Frontend Client:
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS, Lucide Icons
- **HTTP Client**: Axios (with JWT interceptors)
- **Deployment**: Vercel Edge Network (Global CDN)

### Backend Services:
- **API Framework**: FastAPI (Python 3.11) with Uvicorn ASGI
- **Computer Vision**: OpenCV (Headless), Pillow, NumPy
- **OCR Engine**: RapidOCR (ONNX Neural Engine), PyTesseract (Tesseract 5 Indic Models)
- **PDF & Certificate Engine**: ReportLab, PyMuPDF, PyPDF
- **Database & ORM**: SQLAlchemy 2.0, SQLite / PostgreSQL
- **Security & Auth**: OAuth2 Password Flow, PyJWT, Passlib, Cryptography
- **Deployment**: Docker Container on Render Cloud Platform

---

## 👥 Team

- **Nikhil Appari** (Team Lead)
- **Hemanth Birda**
- **Sai Naidu Yalla**
- **Poojitha Bellam**
- **Kalyani Bondi**
- **Madhavi Nakka**

---

## 🚀 Local Development Setup

If you wish to run the system locally on your development machine:

### Prerequisites:
- Python 3.10+
- Node.js 18+ & npm
- Git

### 1. Clone the Repository:
```bash
git clone https://github.com/nikhilappari/SIH26018-Land-Digitization.git
cd SIH26018-Land-Digitization
```

### 2. Backend Setup:
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API docs available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### 3. Frontend Setup:
```bash
cd ../frontend
npm install
npm run dev
```
*Frontend Portal running at: [http://localhost:3000](http://localhost:3000)*

---

## 📜 License & Compliance

Distributed under the **MIT License**. Compliant with **DILRMP (Digital India Land Records Modernization Programme)** standards for secure digital governance.
